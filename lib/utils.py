import os


def get_index():
    index = 0
    while True:
        if not os.path.isdir(f'data/2/{index}'):
            break
        else:
            index += 1
    return index
