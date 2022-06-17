import time
import json
import datetime
import random

import vlc
import requests
from displayhatmini import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont

from alarm import Alarm
from buttons import SerialListener

PORT = '/dev/ttyACM0'
ALARMS = []

alarms_from = (6, 0)
alarms_by = 7
alarms_count = 4

for i in range(alarms_count):
  tmp_h, tmp_m = alarms_from
  tmp_m += alarms_by * i
  while tmp_m > 60:
    tmp_h += 1
    tmp_m -= 60

  ALARMS.append(Alarm(tmp_h, tmp_m))

add_mins = 45
if add_mins > 0:
	for i in range(len(ALARMS)):
		ALARMS[i].minute += add_mins
		if ALARMS[i].minute > 59:
			ALARMS[i].hour += ALARMS[i].minute // 60
			ALARMS[i].minute %= 60

now = datetime.datetime.now()
for i in ALARMS:
  print(i, i.from_now(now))

TRIGGER_ALARM_ON_BOOT = False
if TRIGGER_ALARM_ON_BOOT:
    now = datetime.datetime.now()
    ALARMS.append(Alarm(now.hour, now.minute))

SLEEP_ALL_ENDPOINT = 'http://192.168.0.193:8123/api/webhook/sleep_all'

width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
buffer = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(buffer)
LARGE_FONT = ImageFont.truetype("FiraCode-Bold.ttf", 64)
MEDIUM = ImageFont.truetype("FiraCode-Bold.ttf", 40)
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
                p = vlc.MediaPlayer('viva-la-vida.mp3')
                p.audio_set_volume(50)
                p.play()

                t = time.time()

                stage = 'A'

                a_guess = 0

                x_num = random.randint(-9, 9)
                y_num = random.randint(-9, 9)
                z_num = random.randint(-50, 50)
                w_num = x_num * y_num + z_num
                displayhatmini.set_backlight(1)

                time_since_c = 0

                count = 0
                while True:
                    draw.rectangle((0, 0, width, height), (0, 0, 0))
                    time_text = 'WAKE UP'
                    w, h = draw.textsize(time_text, font=LARGE_FONT)
                    draw.text(((width-w)/2, 0), time_text,
                              fill="white", font=LARGE_FONT)

                    time_text = now.strftime(f"%H:%M")

                    w, h = draw.textsize(time_text, font=LARGE_FONT)
                    draw.text(((width-w)/2, 64), time_text,
                              fill="white", font=LARGE_FONT)

                    if (time.time() - t) > 45:
                        p.audio_set_volume(125)
                    elif (time.time() - t) > 25:
                        p.audio_set_volume(100)
                    elif (time.time() - t) > 10:
                        p.audio_set_volume(75)

                    if time.time() - time_since_c > 20:
                        x_num = random.randint(-9, 9)
                        y_num = random.randint(-9, 9)
                        z_num = random.randint(-50, 50)
                        w_num = x_num * y_num + z_num
                        time_since_c = time.time()

                    if stage in 'AB':
                        time_text = f'{stage}: {count}/20'
                        w, h = draw.textsize(time_text, font=MEDIUM)
                        draw.text(((width-w)/2, 130), time_text,
                                  fill="white", font=MEDIUM)
                    else:
                        op = '+' if z_num > 0 else ''
                        time_text = f'x*{y_num}{op}{z_num}={w_num}'
                        w, h = draw.textsize(time_text, font=MEDIUM)
                        draw.text(((width-w)/2, 130), time_text,
                                  fill="white", font=MEDIUM)
                        time_text = f"{a_guess} ({int(time.time() - time_since_c)}/20)"
                        w, h = draw.textsize(time_text, font=MEDIUM)
                        draw.text(((width-w)/2, 190), time_text,
                                  fill="white", font=MEDIUM)

                    if stage == 'C':
                        if serial.state.a:
                            while serial.state.a:
                                pass
                            a_guess += 1
                            if a_guess > 9:
                                a_guess = 9
                        if serial.state.b:
                            while serial.state.b:
                                pass
                            a_guess -= 1
                            if a_guess < -9:
                                a_guess = -9
                        if serial.state.c:
                            while serial.state.c:
                                pass

                            if a_guess == x_num:
                                break
                            else:
                                draw.rectangle(
                                    (0, 0, width, height), (0, 0, 0))
                                time_text = 'WRONG'
                                w, h = draw.textsize(
                                    time_text, font=LARGE_FONT)
                                draw.text(((width-w)/2, 20), time_text,
                                          fill="white", font=LARGE_FONT)
                                time.sleep(1)
                                a_guess = 0
                                continue

                    if stage == 'A' and serial.state.a:
                        while serial.state.a:
                            pass
                        count += 1

                        if count >= 20:
                            count = 0
                            stage = 'B'
                    if stage == 'B' and serial.state.b:
                        while serial.state.a:
                            pass
                        count += 1

                        if count >= 20:
                            stage = 'C'
                            time_since_c = time.time()

                    displayhatmini.display()

                p.stop()
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

            if serial.state.b and serial.state.a:
                requests.post(SLEEP_ALL_ENDPOINT)
                while serial.state.a or serial.state.b:
                    pass

            if serial.state.a:
                p = vlc.MediaPlayer('viva-la-vida.mp3')
                p.audio_set_volume(50)
                p.play()
                while serial.state.a:
                    pass
                p.stop()

            if timeout <= time.time() and timeout_enabled:
                displayhatmini.set_backlight(0)
            else:
                displayhatmini.set_backlight(1)

            displayhatmini.display()
    except KeyboardInterrupt:
        serial.kill()
