import time
import struct
import zlib

def gzcompress(data):
    _compress = zlib.compressobj(5, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    length = len(data)
    _size = length
    _crc = zlib.crc32(data)
    out = "\037\213\010\0%s\002\377%s%s%s%s"%(
        struct.pack('<L', long(time.time())),
        _compress.compress(data),
        _compress.flush(),
        struct.pack('<l', _crc),
        struct.pack('<L', _size & 0xffffffffL)
    )
    return out

def GzipMiddleware(func):
    def _func(request):
        result = func(request)
        if result:
            headers = request.res.headers
            result_len = len(result)
            if result_len > 4096 and ('gzip' in request.environ.get('HTTP_ACCEPT_ENCODING', '')):
                result = gzcompress(result)
                result_len = len(result)
                headers.add_header("Content-Encoding", "gzip")
                return result
            headers.add_header( 'Content-Length', str(result_len) )
        return result
    return _func