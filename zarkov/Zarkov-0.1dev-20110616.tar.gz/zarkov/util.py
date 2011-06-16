'''Utilities for reading and writing bson and json streams

JSON: objects are preceded by their length in bytes formatted as a decimal number
and a newline.

BSON: objects are preceded by their length in bytes in a packed little-endian
4-byte integer.
'''

import json
import bson
import struct
import logging


log = logging.getLogger(__name__)

def read_json(fp):
    '''Read a json doc from a file stream.'''
    s = fp.readline()
    if not s: return None
    obj_buf = fp.read(int(s))
    return json.loads(obj_buf)

def read_bson(fp):
    '''Read a bson doc from a file stream.'''
    s = fp.read(4)
    if not s: return None
    length = struct.unpack('<I', s)[0]
    s = fp.read(length)
    return bson.BSON(s).decode()

def write_json(fp, obj):
    '''Write a json doc to a file stream.'''
    obj_buf = json.dumps(obj)
    fp.write(str(len(obj_buf)) + '\n')
    fp.write(obj_buf)
    fp.flush()
             
def write_bson(fp, obj):
    '''Write a bson doc to a file stream.'''
    obj_buf = bson.BSON.encode(obj)
    fp.write(struct.pack('<I', len(obj_buf)))
    fp.write(obj_buf)
    fp.flush()

