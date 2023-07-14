import random
import pickle
import time
import pytz
import os
import threading
import select
import socket
import struct
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
            pickle.dump(state, f)

    return state

def save_state(state=random.getstate()):
    global HI_NOTE_IDX
    global LOVE_NOTE_IDX

    print('[*] save_state called')

    with open(RANDOM_STATE_PATH, 'wb') as f:
        pickle.dump(state, f)

    new_hi_note_idx = random.randint(0, len(HI_NOTES) - 1)
    while new_hi_note_idx == HI_NOTE_IDX:
        new_hi_note_idx = random.randint(0, len(HI_NOTES) - 1)
    HI_NOTE_IDX = new_hi_note_idx

    new_love_note_idx = random.randint(0, len(LOVE_NOTES) - 1)
    while new_love_note_idx == LOVE_NOTE_IDX:
        new_love_note_idx = random.randint(0, len(LOVE_NOTES) - 1)
    LOVE_NOTE_IDX = new_love_note_idx

# handle client data
# - [0:4] : c0 c0 00 00
# - [5]   : 01
# - [6:8] : 00 00 00
def handle_client_msg(msg):
    if len(msg) != 8:
        return False

    magic = struct.unpack('<I', msg[:4])[0]
    if magic != 0xc0c0:
        return False

    toggle = struct.unpack('<I', msg[4:])[0]
    if toggle != 1:
        return False

    save_state()
    return True

def state_listener():
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_path = '/tmp/notes_state.sock'

    # clean up existing socket if it may exist
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    server.setblocking(0)
    server.bind(socket_path)
    server.listen(5)

    inputs = [server]

    while True:
        readable, _, err = select.select(inputs, [], inputs, 0.5)
        for s in readable:
            if s is server:
                connection, client_info = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
            else:
                # this is a connected client
                data = s.recv(1024)
                handle_client_msg(data)
                inputs.remove(s)
                s.close()

        for s in err:
            inputs.remove(s)
            s.close()

def init():
    state = load_state('./conf.txt')
    save_state()
    assert(state is not None)
    random.setstate(state)

    t = threading.Thread(target=state_listener)
    t.start()

def get_hi_note():
    return 'Hu ' + HI_NOTES[HI_NOTE_IDX]

def get_love_note():
    return LOVE_NOTES[LOVE_NOTE_IDX] + ' Anu'

init()
