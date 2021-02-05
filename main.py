import threading
import sounddevice as sd
import numpy as np
import time
from control import Control
from lib.sound_control import Sound
from lib.params import BROKER, NODE, SAMPLERATE, DOWNSAMPLE


mic = Sound(BROKER, NODE)
mic.loop_start()


def sound_main():
    while mic.run:
        if mic.is_streaming:
            print(f'{mic.info} record start')
            stream = mic.create_streamer()
            with stream:
                while mic.is_streaming:
                    time.sleep(1)
                    print(f'[INFO] {mic.info} is recording')
            print(f'{mic.info} record end')
        elif mic.is_idle:
            while mic.is_idle:
                print(f'[INFO] {mic.info} is in Idle')
                time.sleep(0.1)
        elif mic.is_playing:
            print(f'[INFO] {mic.info} is playing')
            sd.play(mic.data, SAMPLERATE/DOWNSAMPLE)
            sd.wait()
            mic.is_streaming = False
            mic.is_playing = False
            mic.is_idle = True


sound = threading.Thread(target=sound_main)
sound.start()
Control()
print('END')
