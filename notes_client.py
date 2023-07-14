#!/usr/bin/env python3

import socket
import struct
import sys
import logging

logging.basicConfig(filename='/tmp/notes_client.log',
                    filemode='a',
                    level=logging.INFO)
logger = logging.getLogger('notes_client')

socket_path = '/tmp/notes_state.sock'

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    s.connect(socket_path)
except socket.error as msg:
    logger.info(msg)
    sys.exit(0)

msg = b''
msg += struct.pack('<I', 0xc0c0)
msg += struct.pack('<I', 1)

s.send(msg)
s.close()

logger.info('[+] Update success')
