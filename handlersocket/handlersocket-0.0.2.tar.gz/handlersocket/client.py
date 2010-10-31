# coding: utf-8

import re
from cStringIO import StringIO
from collections import deque


def _escape_cb(m):
    return '\x01' + chr(ord(m.group(0)) + 0x40)

def _escape(s, _sub=re.compile(r'[\x00-\x0f]').subn):
    return _sub(_escape_cb, s)[0]

def _unescape_cb(m):
    return chr(ord(m.group(0)[1]) - 0x40)

def _unescape(s, _sub=re.compile(r'\x01.').subn):
    return _sub(_unescape_cb, s)[0]

def _build_line(columns):
    escaped = []
    append = escaped.append
    for col in columns:
        if col is None:
            append('\0')
            continue
        if isinstance(col, unicode):
            col = col.encode('utf-8')
        else:
            col = str(col)
        append(_escape(col))
    return '\t'.join(escaped) + '\n'

def _parse_line(line):
    return tuple(None if c =='\0' else _unescape(c) for c in line.split('\t'))

class TransportError(Exception):
    pass

class RemoteError(Exception):
    pass

class Client(object):
    """HandleSocket client.

    >>> import handlersocket
    >>> client = handlersocket.Client('hostname', 8899)
    >>> # id is the primary key.
    >>> index = client.open_index('dbname', 'tblname', 'id,col1,col2')
    >>> # fetch row by id=3.
    >>> row = client.find(index, '=', (3,))
    >>> print row
    """
    def __init__(self, host=None, port=None):
        import socket
        self.indexes = {'Dummy': 0} # start indexid from 1.

        if port is None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect((host,))
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        self._conn = sock
        self._buf = StringIO()
        self._recieved_lines = deque()

        self._batch = False
        self._outbuf = []

    def _read_line(self):
        recv_lines = self._recieved_lines
        if recv_lines:
            return recv_lines.popleft()
        buf = self._buf
        while True:
            got = self._conn.recv(16*1024)
            if not got:
                raise TransportError("Can't read a line from connection.")
            buf.write(got)
            num_lines = got.count('\n')
            if num_lines:
                break;
        got = got[got.rfind('\n')+1:]
        buf.reset()
        for _ in xrange(num_lines):
            recv_lines.append(buf.readline().rstrip('\r\n'))
        buf.reset()
        buf.truncate()
        buf.write(got)
        return recv_lines.popleft()

    def _check_remote_error(self, columns):
        if columns[1] == '1' and len(columns) == 3:
            raise RemoteError("%s: %s" % (columns[0], columns[2]))

    def open_index(self, database, table, fields, index='PRIMARY'):
        """Open an index and returns indexid.

        :param  database:   database name
        :param  table:      table name
        :param  fields:     columns separeted by ',' (ex. 'id,name,age')
        :param  index:      index name. (default: 'PRIMARY')
        """
        key = (database, table, index, fields)
        if key in self.indexes:
            return self.indexes[key]

        indexid = len(self.indexes)
        command = _build_line(('P', indexid) + key)
        #print command
        self._conn.sendall(command)
        line = self._read_line()
        #print line
        columns = _parse_line(line)
        if len(columns) < 2:
            raise TransportError("Unexpected format: %r" % (line,))
        if columns[0] == '0' and columns[1] == '1':
            self.indexes[key] = indexid
            return indexid
        self._check_remote_error(columns) # may raise RemoteError
        raise TransportError("Unexpected format")

    def start_batch(self):
        self._batch = True

    def execute_batch(self):
        num = len(self._outbuf)
        self._conn.sendall(''.join(self._outbuf))
        del self._outbuf[:]
        return [self._read_line() for i in xrange(num)]

    def find(self, indexid, op, args, limit=None, offset=None):
        if offset:
            opt = (limit, offset)
        elif limit:
            opt = (limit,)
        else:
            opt = ()
        command = _build_line((indexid, op, len(args)) + args + opt)
        if self._batch:
            self._outbuf.append(command)
            return None
        #print command
        self._conn.sendall(command)
        line = self._read_line()
        #print line
        columns = _parse_line(line)
        if len(columns) < 2:
            raise TransportError("Unexpected format")
        if columns[0] == '0':
            row_size = int(columns[1])
            result = []
            for i in xrange(2, len(columns) - row_size + 1, row_size):
                result.append(columns[i:i+row_size])
            return result
        self._check_remote_error(columns) # may raise RemoteError
        raise TransportError("Unexpected format")
