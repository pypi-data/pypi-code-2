# coding: utf-8

import re

def _escape_cb(m):
    return '\x01' + chr(ord(m.group(0)) + 0x40)

def _escape(s, R=re.compile(r'[\x00-\x0f]')):
    return R.subn(_escape_cb, s)[0]

def _unescape_cb(m):
    return chr(ord(m.group(0)[1]) - 0x40)

def _unescape(s, R=re.compile(r'\x01.')):
    return R.subn(_unescape_cb, s)[0]

def _test_escape():
    s = 'a\x00b\x01c\x0fd\x10e'
    e = _escape(s)
    assert e == 'a\x01\x40b\x01\x41c\x01\x4fd\x10e'
    u = _unescape(e)
    assert u == s

def _build_line(columns):
    escaped = []
    for col in columns:
        if col is None:
            escaped.append('\0')
            continue
        if isinstance(col, unicode):
            col = col.encode('utf-8')
        else:
            col = str(col)
        col = _escape(col)
        escaped.append(col)
    return '\t'.join(escaped) + '\n'

def _parse_line(line):
    return [None if c =='\0' else _unescape(c)
                 for c in line.split('\t')]

class TransportError(Exception):
    pass

class RemoteError(Exception):
    pass

class Client(object):
    def __init__(self, host=None, port=None):
        import socket
        self.indexes = {}

        if port is None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect((host,))
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        self._conn = sock
        self._buf = []

    def _read_line(self):
        buf = self._buf
        while True:
            got = self._conn.recv(8096)
            if not got:
                raise TransportError("Can't read a line from connection.")
            p = got.find('\n')
            if p == -1:
                buf.append(got)
                continue
            if p > 0 and got[p-1] == '\r':
                head = got[:p-1]
            else:
                head = got[:p]
            tail = got[p+1:]

            buf.append(head)
            line = ''.join(buf)
            buf[:] = [tail]
            return head

    def _check_remote_error(self, columns):
        if columns[1] == '1' and len(columns) == 3:
            raise RemoteError("%s: %s" % (columns[0], columns[2]))

    def open_index(self, database, table, fields, index='PRIMARY',
                   index_no=None):
        """Open an index.

        :param  database:   database name
        :param  table:      table name
        :param  fields:     columns separeted by ','
        :param  index:      index name. (default: 'PRIMARY')
        :param  index_no:   Number assigned with the opened index. `None`
                            means assign automatically. (default: `None`)
        """
        if index_no is None:
            if self.indexes:
                index_no = max(self.indexes) + 1
            else:
                index_no = 1
        command = _build_line(('P', index_no, database, table, index,
            ','.join(fields)))
        #print command
        self._conn.sendall(command)

        line = self._read_line()
        #print line
        columns = _parse_line(line)
        if len(columns) < 2:
            raise TransportError("Unexpected format: %r" % (line,))
        if columns[0] == '0' and columns[1] == '1':
            self.indexes[index_no] = (database, table, index, fields)
            return index_no
        self._check_remote_error(columns) # may raise RemoteError
        raise TransportError("Unexpected format")

    def find(self, index_no, op, args, limit=None, offset=None):
        if offset:
            opt = (limit, offset)
        elif limit:
            opt = (limit,)
        else:
            opt = ()
        command = _build_line((str(index_no), op, str(len(args))) + args + opt)
        #print command
        self._conn.sendall(command)

        line = self._read_line()
        #print line
        columns = _parse_line(line)
        if len(columns) < 2:
            raise TransportError("Unexpected format")
        if columns[0] == '0':
            num_result = int(columns[1])
            if num_result == 0:
                return []
            tuple_size = (len(columns)-2) / num_result
            result = []
            for i in xrange(2, len(columns) - tuple_size + 1, tuple_size):
                result.append(columns[i:i+tuple_size])
            return result
        self._check_remote_error(columns) # may raise RemoteError
        raise TransportError("Unexpected format")
