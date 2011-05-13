"""This class works in concert with bin/pylab_server.py
to allow you to display simple pylab/matplotlib graphics
on another machine.   It's most useful if you need to do
plots from a machine where pylab isn't or cannot be installed.
"""

import os as _os



class _ProtocolError(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)

class _BadPrefixError(_ProtocolError):
	def __init__(self, *s):
		ProtocolError.__init__(self, *s)

class _SocketClosed(_ProtocolError):
	def __init__(self, *s):
		_ProtocolError.__init__(self, *s)


class _pylab_client(object):
	import socket as _s
	import codecs as _c
	import random as _r
	import cPickle as _p
	import md5 as _m

	ID = 'pylab_server'
	KEY = 'alfaljflajljljslfajsljalsfjalsqowrq nfnqn qkfqle'
	PP = 0

	def wclose(self):
		self.flush()
		self.sock.close()


	def flush(self):
		if self.out:
			# print 'SENDING', self.out
			self.sock.sendall( ''.join(self.out) )
			self.out = []


	def send(self, prefix, s):
		self.out.append( '%s %s\n' % (prefix, self.tohex(s)[0]) )
		# print 'out <= ', self.out[-1], len(self.out)
		self.thash.update(s)
		if len(s) > 1000:
			self.flush()


	def __init__(self, host, port):
		self.fromhex = self._c.getdecoder('hex_codec')
		self.tohex = self._c.getencoder('hex_codec')
		self.thash = self._m.new()
		self.rhash = self._m.new()
		self.thash.update(self.KEY + '1')
		self.rhash.update(self.KEY + '2')
		self.out = []
		self.rqno = None
		self.rfile = None
		self.open(host, port)


	def call(self, fnname, args, argdict):
		self.xmit_call(fnname, args, argdict)
		return self.recv()


	def xmit_call(self, fnname, args, argdict):
		self.send('I', self.ID)
		self.rqno  = self._r.getrandbits(31)
		self.send('R', '%d' % self.rqno)
		self.send('O', 'call')
		self.send('F', fnname)
		self.send('A', self._p.dumps(args, self.PP) )
		self.send('B', self._p.dumps(argdict, self.PP) )
		self.send('H', self.thash.hexdigest() )
		self.send('E', 'END')
		self.flush()
			

	def special(self, op):
		self.xmit_special(op)
		return self.recv()


	def xmit_special(self, op):
		self.send('I', self.ID)
		self.rqno  = self._r.getrandbits(31)
		self.send('R', '%d' % self.rqno)
		self.send('O', op)
		self.send('H', self.thash.hexdigest() )
		self.send('E', 'END')
		self.flush()


	def get(self, prefix):
		tmp = self.rfile.readline()
		if tmp == '':
			raise _SocketClosed
		x = self.fromhex(tmp[1:].strip())[0]
		if tmp[0] == 'Z':
			raise _ProtocolError, 'Remote: %s' % x
		if tmp[0] != prefix:
			raise _BadPrefixError, 'Expected %s, got %s' % (prefix, tmp[0])
		self.rhash.update(x)
		return x


	def recv(self):
		if self.get('i') != self.ID:
			raise _ProtocolError, 'ID mismatch'
		if int(self.get('r')) != self.rqno:
			raise _ProtocolError, 'Bad rqno.'
		code = self.get('c')
		v = self.get('v')
		localhash = self.rhash.hexdigest()
		if localhash != self.get('h'):
			raise _ProtocolError, 'Bad authentication'
		if self.get('e') != 'END':
			raise _ProtocolError, 'No end'

		rv = self._p.loads( v )

		if code == 'Exception':
			function, argt, argd, x = rv
			raise Exception(x, function, argt, argd)
		elif code == 'AttributeError':
			raise AttributeError, rv
		return rv


	def open(self, host, port):
		"""Connect to a host.
		Don't try to reopen an already connected instance.
		"""
		self.eof = 0
		self.host = host
		self.port = port
		msg = "getaddrinfo returns an empty list"
		for res in self._s.getaddrinfo(host, port, 0, self._s.SOCK_STREAM):
			af, socktype, proto, canonname, sa = res
			try:
				self.sock = self._s.socket(af, socktype, proto)
				self.sock.connect(sa)
			except self._s.error, msg:
				if self.sock:
					self.sock.close()
					self.sock = None
					continue
			break
		if not self.sock:
			raise self._s.error, '%s on (%s,%s,%s,%s,%s)' % (msg,
						af, socktype, proto, canonname, sa)
		self.rfile = self.sock.makefile('rb', -1)


	def close(self):
		if self.sock:
			# self.special('exit')
			self.sock.close()
			self.sock = None


	def __del__(self):
		self.close()

def _test():
	c = _pylab_client(_Host, _Port)
	print c.special('list')[:10]
	print c.call('plot', ([1,2,3,4], [1,2,4,1]), {})
	print c.call('show', (), {})
	c.close()



if 'PYLABDISP' in _os.environ:
	Host, Port = _os.environ.get('PYLABDISP', 'localhost:8125').split(':')
	_client = _pylab_client(Host, Port)
	_list = _client.special('list')
	for (_nm, _c) in _list:
		if _c:
			exec("def %s(*a, **b): _client.call('%s', a, b)" % (_nm, _nm))
else:
	from pylab import *

if __name__ == '__main__':
	plot([1,2,3,4], [1,2,4,1])
	show()
