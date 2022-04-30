import time
import json
import board
from digitalio import DigitalInOut, Direction, Pull

if __name__ == '__main__':
    last = [False, False, False, False]
    buttons = [
        DigitalInOut(board.GP2),
        DigitalInOut(board.GP3),
        DigitalInOut(board.GP4),
        DigitalInOut(board.GP5),
    ]

    for button in buttons:
        button.direction = Direction.INPUT
        button.pull = Pull.UP

    i = 0
    while True:
        values = [not button.value for button in buttons]
        if json.dumps(values) != json.dumps(last):
            last = [i for i in values]
            print(json.dumps(values))

        i += 1
        if i % 100 == 0:
            print(json.dumps(values))

        time.sleep(0.01)
