# One and only broker
# BROKER = "192.168.0.100"
BROKER = "127.0.0.1"
PORT = 1883
NODE = 'mic_1'

# Topic list
SENSORS = [["sensors/sensor1/data", 1, 1],
           ["sensors/sensor2/data", 2, 1],
           ["sensors/sensor3/data", 3, 1],
           ["sensors/sensor4/data", 4, 1],
           ["sensors/sensor5/data", 5, 1],
           ["sensors/sensor6/data", 6, 1],
           ["sensors/sensor7/data", 7, 1],
           ["sensors/sensor8/data", 8, 0],
           ["sensors/sensor9/data", 9, 0],
           ["sensors/sensor10/data", 10, 1]]

LOCATION_LIST = ['2', '3', '4', '5', '6', '7', '8']
LABEL_LIST = ['south', 'west', 'north', 'east']

# Command list
START = 'start'
STOP = 'stop'
RESET = 'reset'
SAVE = 'save'
PLAY = 'play'
QUIT = 'quit'
ACTIVITIE_START = 'a_start'
ACTIVITIE_STOP = 'a_stop'

DEVICE = 0
CHANNEL = 1
SAMPLERATE = 48000
DOWNSAMPLE = 4

SOUND_BUFFER_MAX_CAPACITY = 300_000

SENSOR_ERROR = "Sensor is not ready, check"

CACHE_PATH = r'cache'
SAVE_PATH = r'data'

TIME_FORMAT = "%H_%M_%S"
DATE_FORMAT = "%Y_%m_%d"
DATE_TIME = "%Y_%m_%d_%H_%M_%S"
