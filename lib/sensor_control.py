from lib.paho_mqtt import PahoMqtt
from lib.params import SAVE_PATH
from shutil import move
import csv
import os


class Sensor(PahoMqtt):

    def __init__(self, broker, info, port=1883, raw_msg=False,
                 c_msg='', d_msg=''):
        super().__init__(broker, info, port=port, raw_msg=raw_msg,
                         c_msg=c_msg, d_msg=d_msg)

        # Flags
        self.is_streaming = False
        self.is_started = False
        self.sensor_ready = False

        # Attributes
        self.label = None
        self.counter = 1
        self.counter_temp = 0
        self.death_counter = 0

    def _on_message(self, client, userdata, message):
        self.counter += 1
        if self.counter > 10000:
            self.counter = 1
        if self.is_streaming:
            msg = message.payload.decode("utf-8", "ignore")
            msg = msg.replace("[", "")
            msg = msg.replace("]", "")
            msg = msg.replace(" ", "")
            # TODO: insert timestamp
            if self.label:
                self._writer.writerow([msg, self.label])
                self.label = None
            else:
                self._writer.writerow([msg, 0])

    def init(self, path):
        self.path = f'{path}/sensor_{self.info}.csv'
        self._file = open(self.path, "w+", newline='')
        self._writer = csv.writer(self._file)
        self.is_started = True
        self.is_streaming = True

    def stop(self):
        self.is_streaming = False

    def start(self):
        self.is_streaming = True

    def save(self, index):
        self.is_started = False
        paths = self.path.split('/')
        try:
            os.makedirs(f'{SAVE_PATH}/{paths[1]}/{index}')
        except FileExistsError:
            pass
        new_path = f'{SAVE_PATH}/{paths[1]}/{index}'
        try:
            move(self.path, new_path)
        except Exception as e:
            print(str(e), 'in sensor_control.save')

    def reset(self):
        self.is_started = False
        if not self.is_streaming and self.is_started:
            try:
                os.remove(self.path)
            except Exception as e:
                print(str(e), 'in sensor_control.reset')
            return True
        else:
            return False
