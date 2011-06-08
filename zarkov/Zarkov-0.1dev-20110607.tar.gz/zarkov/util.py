import json
import bson
import struct

def read_json(fp):
    s = fp.readline()
    if not s: return None
    obj_buf = fp.read(int(s))
    return json.loads(obj_buf)

def read_bson(fp):
    s = fp.read(4)
    if not s: return None
    length = struct.unpack('<I', s)[0]
    s = fp.read(length)
    return bson.BSON(s).decode()

def write_json(fp, obj):
    obj_buf = json.dumps(obj)
    fp.write(str(len(obj_buf)) + '\n')
    fp.write(obj_buf)
    fp.flush()
             
def write_bson(fp, obj):
    obj_buf = bson.BSON.encode(obj)
    fp.write(struct.pack('<I', len(obj_buf)))
    fp.write(obj_buf)
    fp.flush()

