import struct
from zlib import crc32

f = open('2MASS_k_new.png')
header = f.read(8)

while True:

    chunk_length = struct.unpack('>I', f.read(4))[0]
    print 'length', chunk_length
    chunk_type = f.read(4)
    print 'type', chunk_type
    chunk_data = f.read(chunk_length)
    chunk_crc = struct.unpack('>i', f.read(4))[0]
    print 'crc', chunk_crc
    print 'crc (check)', crc32(chunk_type + chunk_data)
    
    if chunk_type == 'IEND':
        break

# def writebytecrc(self,c):
# 
#     self.crc = crc32(chr(c),self.crc)
#     self.fd.write(chr(c))