# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import time
import errno
import socket
import select
import struct

from koboldfs import protocol

from threading import local

try:
    from hashlib import md5
except:                         #pragma NO COVER
    from md5 import md5         #pragma NO COVER

try:
    import transaction
except ImportError:             #pragma NO COVER
    pass                        #pragma NO COVER


class Client(object):
    """Client for the koboldfs distributed filesystem"""

    def __init__(self, domain, servers, timeout=2.0):
        self.domain = str(domain)
        self.servers = tuple(servers)
        self.timeout = timeout
        self._dead_servers = {}
        self._socket_cache = None

    def _socket(self, timeout=None, servers=None):
        if servers is None and self._socket_cache is not None:
            return self._socket_cache
        now, dead_servers = time.time(), self._dead_servers
        _servers = servers or self.servers
        _timeout = timeout or self.timeout
        for s in _servers:
            dead = dead_servers.get(s)
            if dead is not None:
                if now - dead < 10:
                    continue
                else:
                    del dead_servers[s]
            host, port = s.split(':', 1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = sock.connect_ex((host, int(port)))
            if not r:
                if servers is None:
                    self._socket_cache = sock
                sock.settimeout(_timeout)
                return sock
            if r == errno.EINPROGRESS:
                if select.select([], [sock], [], 3)[1:]:
                    r = sock.connect_ex((host, int(port)))
                    if not r or r == errno.EISCONN:
                        if servers is None:
                            self._socket_cache = sock
                        sock.settimeout(_timeout)
                        return sock
            dead_servers[s] = now
        return None

    def _read(self, sock, count):
        output = ""
        while len(output) < count:
            try:
                data = sock.recv(count - len(output))
            except socket.timeout:
                self.close()
                return None
            if not data:
                self.close()
                return None
            output += data
        return output

    def _write(self, sock, data):
        try:
            sock.sendall(data)
        except socket.error, e:
            if e[0] == errno.EPIPE:
                return False
            raise
        else:
            return True

    def _request(self, command, args=[]):
        parts = [command, struct.pack('B', len(args))]
        for arg in args:
            parts.extend((struct.pack('I', len(arg)), arg))
        return ''.join(parts)

    def ping(self, retry=True):
        sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_PING)
        if not self._write(sock, request):
            return False
        ret = self._read(sock, 1)
        if ret is None and retry:
            return self.ping(retry=False)
        return ret == protocol.RES_OK

    def put(self, key, source, retry=True):
        close = False
        if not hasattr(source, 'read'):
            source = open(source, 'rb')
            close = True
        source.seek(0, 2)
        size = source.tell()
        source.seek(0)
        sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_PUT, args=(self.domain, key,))
        if not self._write(sock, request):
            return False
        ret = self._read(sock, 1)
        if ret is None and retry:
            return self.put(key, source, retry=False)
        elif ret != protocol.RES_WAITING:
            return False
        if not self._write(sock, struct.pack('I', size)):
            return False
        digest = md5()
        while True:
            data = source.read(protocol.BLOCKSIZE)
            if not data:
                break
            if not self._write(sock, data):
                return False
            digest.update(data)
        if close:
            source.close()
        if not self._write(sock, digest.hexdigest()):
            return False
        return self._read(sock, 1) == protocol.RES_OK

    def get(self, key, destination, sock=None, retry=True):
        if sock is None:
            sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_GET, args=(self.domain, key))
        if not self._write(sock, request):
            return False
        ret = self._read(sock, 1)
        if ret is None and retry:
            return self.get(key, destination, sock=sock, retry=False)
        elif ret == protocol.RES_REDIRECT:
            size = struct.unpack('I',  self._read(sock, 4))[0]
            server = self._read(sock, size)
            sock = self._socket(servers=[server])
            if sock is None:
                return False
            return self.get(key, destination, sock)
        elif ret != protocol.RES_TRANSFER:
            return False
        position = 0
        size = struct.unpack('I',  self._read(sock, 4))[0]
        digest = md5()
        while position < size:
            remaining = size - position
            data = self._read(sock, min(protocol.BLOCKSIZE, remaining))
            if not data:
                break
            destination.write(data)
            digest.update(data)
            position += len(data)
        checksum = self._read(sock, 32)
        if checksum != digest.hexdigest():
            return False
        return True

    def get_url(self, key, retry=True):
        sock = self._socket()
        if sock is None:
            return None
        request = self._request(protocol.CMD_GET_URL, args=(self.domain, key))
        if not self._write(sock, request):
            return None
        ret = self._read(sock, 1)
        if ret is None and retry:
            return self.get_url(key, retry=False)
        elif ret != protocol.RES_TRANSFER:
            return None
        size = struct.unpack('I',  self._read(sock, 4))[0]
        return self._read(sock, size)

    def delete(self, key, retry=True):
        sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_DELETE, args=(self.domain, key))
        if not self._write(sock, request):
            return False
        ret = self._read(sock, 1)
        if ret is None and retry:
            return self.delete(key, retry=False)
        return ret == protocol.RES_OK

    def close(self):
        if self._socket_cache is not None:
            self._socket_cache.close()
            self._socket_cache = None

    def prepare(self):
        sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_PREPARE)
        if not self._write(sock, request):
            return False
        return self._read(sock, 1) == protocol.RES_OK

    def commit(self):
        sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_COMMIT)
        if not self._write(sock, request):
            return False
        return self._read(sock, 1) == protocol.RES_OK

    def abort(self):
        sock = self._socket()
        if sock is None:
            return False
        request = self._request(protocol.CMD_ABORT)
        if not self._write(sock, request):
            return False
        return self._read(sock, 1) == protocol.RES_OK


clients = local()

class ClientPool(object):
    """Thread-safe koboldfs client"""

    def __init__(self, domain, servers, timeout=2.0):
        self.domain = str(domain)
        self.servers = tuple(servers)
        self.timeout = timeout

    @property
    def client(self):
        global clients
        pool = getattr(clients, 'pool', None)
        if pool is None:
            clients.pool = pool = {}
        key = hash((self.domain, self.servers))
        client = pool.get(key)
        if client is None:
            client = Client(self.domain, servers=self.servers,
                timeout=self.timeout)
            pool[key] = client
        return client

    def ping(self):
        return self.client.ping()

    def put(self, key, source):
        return self.client.put(str(key), source)

    def get(self, key, destination):
        return self.client.get(str(key), destination)

    def get_url(self, key):
        return self.client.get_url(str(key))

    def delete(self, key):
        return self.client.delete(str(key))

    def close(self):
        global clients
        pool = getattr(clients, 'pool', None)
        if pool is not None:
            key = hash((self.domain, self.servers))
            client = pool.get(key)
            if client is not None:
                client.close()
                clients.client = None

    def prepare(self):
        return self.client.prepare()

    def commit(self):
        return self.client.commit()

    def abort(self):
        return self.client.abort()


class TransactionalClientPool(ClientPool):
    """Transactional client pool"""

    def __init__(self, *args, **kw):
        self._commands = []
        self._twophase = kw.get('twophase', False)
        if 'twophase' in kw:
            del kw['twophase']
        super(TransactionalClientPool, self).__init__(*args, **kw)

    def delete(self, key):
        self.join()
        return super(TransactionalClientPool, self).delete(key)

    def get(self, key, destination):
        self.join()
        return super(TransactionalClientPool, self).get(key, destination)

    def get_url(self, key):
        self.join()
        return super(TransactionalClientPool, self).get_url(key)

    def put(self, key, source):
        self.join()
        return super(TransactionalClientPool, self).put(key, source)

    def join(self):
        if not getattr(self.client, 'transaction', None):
            tx = transaction.get()
            tx.join(DataManager(self.client, tx, twophase=self._twophase))


class DataManager(object):
    """Data manager"""

    def __init__(self, client, transaction, twophase=False):
        self.client = client
        self.client.transaction = transaction
        self._twophase = twophase

    @property
    def transaction_manager(self):
        return getattr(self.client, 'transaction', None)

    def abort(self, transaction):
        self.client.transaction = None
        return self.client.abort()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_vote(self, transaction):
        if self._twophase and not self.client.prepare():
            raise ValueError('Remote server refused to commit the transaction')

    def tpc_finish(self, transaction):
        self.client.transaction = None
        return self.client.commit()

    def tpc_abort(self, transaction):
        return self.abort()

    def sortKey(self):
        return str(id(self))
