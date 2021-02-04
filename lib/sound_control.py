import sounddevice as sd
import numpy as np
import os

from lib.paho_mqtt import PahoMqtt
from lib.params import *


class Sound(PahoMqtt):

    def __init__(self, broker, info, port=1883, raw_msg=False,
                 c_msg='', d_msg=''):
        super().__init__(broker, info, port=port, raw_msg=raw_msg,
                         c_msg=c_msg, d_msg=d_msg)

        self.run = True
        self.is_streaming = False
        self.is_playing = False
        self.is_idle = True
        self.label = []
        self.path = None
        self.file_index = 0
        self.buffer_index = 0
        self.buffer = np.zeros((1, CHANNEL), dtype=np.float32)
        self.data = np.zeros((1, CHANNEL), dtype=np.float32)

    def _on_connect(self, client, userdata, level, buf):
        self.reset()
        self.publish(topic='sound', msg=f'{self.info}, connected')
        self.subscribe(topic='sound', qos=0)
        print(f"{self.info} connected")

    def _on_message(self, client, userdata, message):
        msg = message.payload.decode("utf-8", "ignore")
        msgs = msg.split("-")
        if msgs[0] == START:
            self.is_streaming = True
            self.is_playing = False
            self.is_idle = False
            self.path = msgs[1]
        elif msgs[0] == STOP:
            self.is_streaming = False
            self.is_playing = False
            self.is_idle = True
        elif msgs[0] == ACTIVITIE_START:
            lbl = self.buffer_index + self.buffer.shape[0]
            self.label.append([f'{msgs[1]}', lbl])
        elif msgs[0] == ACTIVITIE_STOP:
            lbl = self.buffer_index + self.buffer.shape[0]
            self.label.append([f'{msgs[1]}', lbl])
        elif msgs[0] == SAVE:
            self.save()
            self.reset()
        elif msgs[0] == RESET:
            self.reset()
        elif msgs[0] == PLAY:
            self.is_streaming = False
            self.is_playing = True
            self.is_idle = False
        elif msgs[0] == QUIT:
            self.reset()
            self.is_idle = False
            self.run = False

    def reset(self):
        self.is_streaming = False
        self.is_playing = False
        self.is_idle = True
        self.buffer = np.zeros((1, CHANNEL), dtype=np.float32)
        self.data = np.zeros((1, CHANNEL), dtype=np.float32)
        self.label.clear()
        self.buffer_index = 0
        self.file_index = 0
        i = 0
        while True:
            try:
                os.remove(f'{CACHE_PATH}/data_{i}.npy')
            except FileNotFoundError:
                break
            i += 1
        print('[INFO] RESET ...')

    def save(self):
        print('[INFO] SAVING DATA ...')
        np.save(f'{CACHE_PATH}/data_{self.file_index}.npy', self.buffer)
        self.is_streaming = False
        self.is_playing = False
        self.is_idle = True
        self.data = np.zeros((1, CHANNEL), dtype=np.float32)
        i = 0
        while True:
            try:
                tmp = np.load(f'{CACHE_PATH}/data_{i}.npy')
                self.data = np.concatenate((self.data, tmp), axis=0)
                os.remove(f'{CACHE_PATH}/data_{i}.npy')
                i += 1
            except FileNotFoundError:
                break
        try:
            os.makedirs(self.path)
        except FileExistsError:
            pass
        np.save(f'{self.path}/sound_{self.info}.npy', self.data)
        label_file = open(f'{self.path}/label_time.txt', '+w')
        with label_file:
            for item in self.label:
                label_file.write(f'{item[0]},{item[1]}\n')
        print('[INFO] DONE SAVING DATA ...')

    def callback(self, indata, frames, times, status):
        """This is called (from a separate thread) for each audio block."""
        data = indata[::DOWNSAMPLE]
        self.buffer = np.concatenate((self.buffer, data), axis=0)
        if self.buffer.shape[0] > SOUND_BUFFER_MAX_CAPACITY:
            self.buffer = np.delete(self.buffer, 0, axis=0)
            self.buffer_index += self.buffer.shape[0]
            np.save(f'{CACHE_PATH}/data_{self.file_index}.npy', self.buffer)
            self.buffer = np.zeros((1, CHANNEL), dtype=np.float32)
            self.file_index += 1

    def create_streamer(self):
        streamer = sd.InputStream(device=DEVICE, channels=CHANNEL,
                                  samplerate=SAMPLERATE,
                                  callback=self.callback,
                                  dtype=np.float32)
        return streamer
