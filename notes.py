import random
import pickle
import time
import pytz
import os
from datetime import datetime, timedelta
from threading import Timer

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

class Repeat(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

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
            pickle.dump(state, f)

    return state

def save_state(state=random.getstate()):
    global HI_NOTE_IDX
    global LOVE_NOTE_IDX

    print('save_state called from timer!')

    with open(RANDOM_STATE_PATH, 'wb') as f:
        pickle.dump(state, f)

    HI_NOTE_IDX = random.randint(0, len(HI_NOTES) - 1)
    LOVE_NOTE_IDX = random.randint(0, len(LOVE_NOTES) - 1)

def init():
    state = load_state('./conf.txt')
    save_state()
    assert(state is not None)
    random.setstate(state)

    # setup timer to generate new random number
    # every day, and to save random state
    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    next_time = current_time.replace(day=current_time.day, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=10)
    # next_time = current_time + timedelta(seconds=10)
    delta = next_time - current_time
    t = Repeat(interval=delta.total_seconds(), function=save_state)
    t.start()

def get_hi_note():
    return 'Hu ' + HI_NOTES[HI_NOTE_IDX]

def get_love_note():
    return LOVE_NOTES[LOVE_NOTE_IDX] + ' Anu'

init()
