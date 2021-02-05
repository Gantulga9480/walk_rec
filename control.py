from tkinter import Label, LabelFrame, Tk, messagebox, ttk
from tkinter.constants import DISABLED, LEFT, NORMAL
from lib.sensor_control import Sensor
from lib.paho_mqtt import PahoMqtt
from lib.params import *
from lib.utils import *
import os


class Control(Tk):

    def __init__(self, screenName=None, baseName=None,
                 useTk=1, sync=0, use=None):
        super().__init__(screenName=screenName, baseName=baseName,
                         useTk=useTk, sync=sync, use=use)

        self.__init()
        self.__disp()
        self.set_state()
        self.mainloop()

    def stream_init(self):
        sen_count = 0
        for i in range(len(self.clients)):
            if self.clients[i].sensor_ready:
                sen_count += 1
            else:
                messagebox.showwarning("Sensor Error",
                                        f"{SENSOR_ERROR}-{i+1}")
        if sen_count == len(self.clients):
            self.start_btn['state'] = NORMAL
            self.reset_btn['state'] = NORMAL
            self.init_btn['state'] = DISABLED
            print('SENSORS READY')
        else:
            self.reset_btn['state'] = DISABLED
            self.start_btn['state'] = DISABLED

    def stream_start(self):
        if self.los_ind < 1:
            label = self.label[self.label_index]
            for client in self.clients:
                if not client.is_started:
                    path = f'{CACHE_PATH}/{label}'
                    client.init(path)
                client.label = label
            msg = f'{START}-{SAVE_PATH}/{label}/{self.index}'
            self.sound_client.publish('sound', msg)
            msg = f'{ACTIVITIE_START}-{label}'
            self.sound_client.publish('sound', msg)
            self.los_ind += 1
        else:
            self.stream_save()
        self.update_label()

    def stream_reset(self):
        msg = f'{RESET}-?'
        self.sound_client.publish('sound', msg)
        self.los_ind = 0
        for client in self.clients:
            client.stop()
            client.reset()
        self.update_label()
        self.init_btn['state'] = DISABLED
        self.start_btn['state'] = NORMAL
        self.reset_btn['state'] = DISABLED

    def stream_stop(self):
        for client in self.clients:
            client.stop()

    def stream_resume(self):
        for client in self.clients:
            client.start()

    def stream_save(self):
        msg = f'{SAVE}-?'
        self.sound_client.publish('sound', msg)
        self.stream_stop()
        for client in self.clients:
            client.save(self.index)
        self.los_ind = 0
        self.label_index += 1
        if self.label_index == 10:
            self.label_index = 0
            messagebox.showinfo('Recorder', 'Done')
            self.index += 1

    def result(self):
        pass

    def update_label(self):
        if self.label_index < 10 and self.los_ind < 1:
            lbl = self.label[self.label_index]
            st = f'{lbl}'
            self.current_location['text'] = st
            self.start_btn['text'] = f'{lbl}'
        else:
            self.start_btn['text'] = 'SAVE'
        self.current_index['text'] = f'Participant: {self.index}'

    def set_state(self):
        for index, client in enumerate(self.clients):
            if client.counter != client.counter_temp:
                client.counter_temp = client.counter
                client.death_counter = 0
                client.sensor_ready = True
                self.sensor_state[index]["foreground"] = 'green'
            else:
                print(f'[WARNING] SENSOR-{client.info} is not responding')
                client.death_counter += 1
                client.sensor_ready = False
                self.sensor_state[index]["foreground"] = 'red'
            if client.death_counter > 8:
                messagebox.showerror('ERROR', f'SENSOR {client.info} DEAD')
        self.after(1000, self.set_state)

    def __init(self):
        for item in LABEL_LIST:
            try:
                os.makedirs(f'{CACHE_PATH}/{item}')
            except FileExistsError:
                pass
            try:
                os.makedirs(f'{SAVE_PATH}/{item}')
            except FileExistsError:
                pass

        self.sound_client = PahoMqtt(BROKER, "SOUND", c_msg="sound")
        self.sound_client.loop_start()
        self.los_ind = 0
        self.label = LABEL_LIST
        self.label_index = 0
        self.index = get_index()
        self.clients = list()
        dis = 0
        for i, item in enumerate(SENSORS):
            if item[2]:
                self.clients.append(Sensor(BROKER, f"{item[1]}",
                                           c_msg=item[0]))
                self.clients[i-dis].subscribe(item[0])
                self.clients[i-dis].loop_start()
            else:
                dis += 1

    def __disp(self):
        self.title("Control")
        self.resizable(0, 0)
        self.configure(bg='white')
        self.sensor_frame1 = LabelFrame(self, text="Sensor control",
                                        background='white')
        self.sensor_frame1.pack(side=LEFT, fill="y")
        self.sensor_state = list()
        for item in self.clients:
            self.sensor_state.append(Label(self.sensor_frame1,
                                           text=f"SENSOR {item.info}",
                                           background='white',
                                           font=("default", 15, 'bold')))
            self.sensor_state[-1].grid(row=len(self.sensor_state),
                                       column=0)
        self.sensor_frame2 = LabelFrame(self, text="Data control",
                                        background='white')
        self.sensor_frame2.pack(side=LEFT, fill="y")
        self.current_index = Label(self.sensor_frame2,
                                   text=f'Participant: {self.index}',
                                   background='white',
                                   font=("default", 10, 'bold'))
        self.current_index.grid(row=0, column=0, padx=2, pady=2)
        self.current_location = Label(self.sensor_frame2,
                                      text=f'{self.label[self.label_index]}',
                                      background='white',
                                      font=("default", 10, 'bold'))
        self.current_location.grid(row=0, column=1, padx=2, pady=2)
        self.init_btn = ttk.Button(self.sensor_frame2, text="Stream init",
                                   command=self.stream_init,
                                   width=11)
        self.init_btn.grid(row=1, column=0, padx=2, pady=2, columnspan=2)
        self.resume_btn = ttk.Button(self.sensor_frame2, text="Stream stop",
                                     command=self.stream_resume,
                                     width=11)
        self.resume_btn['state'] = DISABLED
        self.resume_btn.grid(row=2, column=0, padx=2, pady=2)
        self.stop_btn = ttk.Button(self.sensor_frame2, text="Stream stop",
                                   command=self.stream_stop,
                                   width=11)
        self.stop_btn['state'] = DISABLED
        self.stop_btn.grid(row=2, column=1, padx=2, pady=2)
        self.start_btn = ttk.Button(self.sensor_frame2,
                                    text=f"{self.label[self.label_index]}",
                                    command=self.stream_start,
                                    width=11)
        self.start_btn['state'] = DISABLED
        self.start_btn.grid(row=3, column=0, padx=2, pady=2)
        self.reset_btn = ttk.Button(self.sensor_frame2,
                                    text='RESET',
                                    command=self.stream_reset,
                                    width=11)
        self.reset_btn['state'] = DISABLED
        self.reset_btn.grid(row=3, column=1, padx=2, pady=2)
