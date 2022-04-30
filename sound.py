import time
import vlc
from pprint import pprint

p = vlc.MediaPlayer('viva-la-vida.mp3')
p.audio_set_volume(50)
p.play()
time.sleep(10)
print(p.get_position())
p.set_position(0)
time.sleep(10)
print(p.get_position())
p.stop()
