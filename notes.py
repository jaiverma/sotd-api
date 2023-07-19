import random
import pickle
import time
import pytz
import os
from uwsgidecorators import *
from datetime import datetime, timedelta

RANDOM_STATE_PATH = None
HI_NOTE_IDX = None
LOVE_NOTE_IDX = None
HI_NOTES = [
    'Anu',
    'Coco',
    'Anubhuti',
    'Anubhuti Agarwal',
    'Maharani Coco',
    'Jaanu',
    'Jojo\'s lover',
    'Lover of Jai',
    'Soda',
    'Soda Screamer'
]
LOVE_NOTES = [
    'I love you',
    'I adore you',
    'You are the love of my life',
    'I miss you',
    'Love you to the moon and back'
]

def load_state(config_path):
    global RANDOM_STATE_PATH

    # read config to get path to random state
    with open(config_path) as f:
        for line in f:
            d = line.strip().split(':')
            d = list(map(lambda x: x.strip(), d))
            assert len(d) == 2
            k, v = d
            if k == 'RANDOM_STATE':
                RANDOM_STATE_PATH = v

    assert(RANDOM_STATE_PATH is not None)

    state = None
    if os.path.exists(RANDOM_STATE_PATH):
        with open(RANDOM_STATE_PATH, 'rb') as f:
            state = pickle.load(f)
    else:
        random.seed(time.time())
        state = random.getstate()
        with open(RANDOM_STATE_PATH, 'wb') as f:
            print('writing state')
            pickle.dump(state, f)

    return state

@cron(30, 19, -1, -1, -1)
def save_state(_num=0):
    global HI_NOTE_IDX
    global LOVE_NOTE_IDX

    print('[*] save_state called')

    with open(RANDOM_STATE_PATH, 'wb') as f:
        state = random.getstate()
        pickle.dump(state, f)

    new_hi_note_idx = random.randint(0, len(HI_NOTES) - 1)
    while new_hi_note_idx == HI_NOTE_IDX:
        new_hi_note_idx = random.randint(0, len(HI_NOTES) - 1)
    HI_NOTE_IDX = new_hi_note_idx

    new_love_note_idx = random.randint(0, len(LOVE_NOTES) - 1)
    while new_love_note_idx == LOVE_NOTE_IDX:
        new_love_note_idx = random.randint(0, len(LOVE_NOTES) - 1)
    LOVE_NOTE_IDX = new_love_note_idx

def init():
    state = load_state('./conf.txt')
    save_state()
    assert(state is not None)
    try:
        random.setstate(state)
    except TypeError:
        print('[-] Failed to load random state')
        pass

def get_hi_note():
    return 'Hu ' + HI_NOTES[HI_NOTE_IDX]

def get_love_note():
    return LOVE_NOTES[LOVE_NOTE_IDX] + ' Anu'

init()
