import os
from lib.params import SAVE_PATH
from lib.params import LABEL_LIST


def get_index():
    index = 0
    while True:
        if not os.path.isdir(f'{SAVE_PATH}/{LABEL_LIST[0]}/{index}'):
            break
        else:
            index += 1
    return index
