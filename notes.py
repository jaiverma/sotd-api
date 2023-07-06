import random
import pickle
import time

RANDOM_STATE_PATH = None

def load_state(config_path):
    global RANDOM_STATE_PATH

    # read config to get path to random state
    with open(config_path) as f:
        for line in f:
            d = line.strip().split(':')
            d = list(map(lambda x: x.strip(), d))
            assert len(d) == 2
            k, v = d
            if k == 'RANDOM_STATE'
                RANDOM_STATE_PATH = v

    state = None
    with open(RANDOM_STATE_PATH, 'rb') as f:
        state = pickle.load(f)
    return state

def save_state(state):
    with open(RANDOM_STATE_PATH, 'wb') as f:
        pickle.dump(state, f)

def init():
    state = load_state('./conf.txt')
    if state is not None:
        random.setstate(state)
    else:
        random.seed(time.time())
        save_state(random.getstate())

def get_hi_note():
    pass

def get_love_note():
    pass
