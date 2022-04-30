import json
from dataclasses import dataclass
import threading

from serial import Serial


@dataclass()
class ButtonState:
    a: bool
    b: bool
    c: bool
    d: bool

    def __str__(self):
        return f"{self.a}{self.b}{self.c}{self.d}"


class SerialListener:
    def __init__(self, port):
        self.port = port
        self.state = ButtonState(False, False, False, False)
        self._thread = None

        self._kill_thread = False

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

    def kill(self):
        self._kill_thread = True

    def _run(self):
        with Serial(self.port, 9600, timeout=1) as ser:
            # read a '\n' terminated line
            while not self._kill_thread:
                try:
                    raw = ser.readline()
                    line = json.loads(raw.strip())
                    if len(line) != 4:
                        continue

                    for i, v in enumerate(line[::-1]):
                        tmp = False
                        if isinstance(v, bool):
                            tmp = v

                        self.state.__setattr__(chr(ord('a') + i), tmp)
                except json.decoder.JSONDecodeError:
                    pass
