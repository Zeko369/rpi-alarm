import time
import json
import datetime

from displayhatmini import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont

from alarm import Alarm
from buttons import SerialListener

PORT = '/dev/ttyACM0'
ALARMS = [Alarm(23, 35), Alarm(7, 0), Alarm(7, 15)]


width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
buffer = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(buffer)
LARGE_FONT = ImageFont.truetype("FiraCode-Bold.ttf", 64)
REGULAR_FONT = ImageFont.truetype("Roboto-Regular.ttf", 24)

displayhatmini = DisplayHATMini(buffer, backlight_pwm=True)
displayhatmini.set_led(0, 0, 0)

DEFAULT_TIMEOUT = 5
timeout_enabled = False
timeout = time.time() + DEFAULT_TIMEOUT

if __name__ == '__main__':
    serial = SerialListener(PORT)
    serial.start()

    displayhatmini.set_backlight(1)
    alarms_done = []

    last_time = datetime.datetime.now()

    try:
        while True:
            if serial.state.d:
                while serial.state.d:
                    pass

                displayhatmini.set_backlight(1)
                timeout = time.time() + DEFAULT_TIMEOUT

            if serial.state.c:
                while serial.state.c:
                    pass

                timeout_enabled = not timeout_enabled
                if timeout_enabled:
                    timeout = time.time()

            now = datetime.datetime.now()
            if now.day != last_time.day:
                last_time = now
                alarms_done = []

            alarms_to_call = list(
                filter(
                    lambda a: a.is_equal(now) and a not in alarms_done,
                    ALARMS
                )
            )

            for alarm in alarms_to_call:
                print(alarm)
                time.sleep(0.5)
                alarms_done.append(alarm)

            draw.rectangle((0, 0, width, height), (0, 0, 0))
            if now.second % 2 == 0:
                colon = ":"
            else:
                colon = " "
            time_text = now.strftime(f"%H{colon}%M")

            w, h = draw.textsize(time_text, font=LARGE_FONT)
            draw.text(((width-w)/2, 20), time_text,
                      fill="white", font=LARGE_FONT)

            for i, alarm in enumerate(ALARMS):
                tmp_text = f"a[{i}]: {alarm.short()} (in {alarm.from_now(now)})"

                w, h = draw.textsize(tmp_text, font=REGULAR_FONT)
                draw.text(((width - w) / 2, 100 + h * i), tmp_text,
                          font=REGULAR_FONT, fill="white")

            if timeout <= time.time() and timeout_enabled:
                displayhatmini.set_backlight(0)
            else:
                displayhatmini.set_backlight(1)

            displayhatmini.display()
    except KeyboardInterrupt:
        serial.kill()
