import os
from lib.params import SAVE_PATH


def get_index():
    index = 0
    while True:
        if not os.path.isdir(f'{SAVE_PATH}/2_1/{index}'):
            break
        else:
            index += 1
    return index
