#!/usr/bin/python

"""This lets you compute on a computer without pylab/matplotlib,
but send simple plots to another computer where pylab is installed.
"""


Port = 8125
ID = 'pylab_server'
KEY = 'alfaljflajljljslfajsljalsfjalsqowrq nfnqn qkfqle'

PP = 2

import SocketServer
import codecs
import pylab
import cPickle
import md5
import sys
from gmisclib import die

class ServerClass(SocketServer.TCPServer,SocketServer.ForkingMixIn):
# class ServerClass(SocketServer.TCPServer):
	def verify_request(self, request, client_address):
		# print 'Client_address=', client_address
		return client_address[0] == '127.0.0.1'


def list_fcns(mod):
	o = []
	for nm in dir(mod):
		it = getattr(mod, nm)
		c_it = callable(it)
		if c_it:
			o.append( (nm, c_it) )
	return o


class ProtocolError(Exception):
	def __init__(self, s):
		Exception.__init__(self, s)

class EOF(ProtocolError):
	def __init__(self):
		ProtocolError.__init__(self, None)

class BadPrefixError(ProtocolError):
	def __init__(self, s):
		ProtocolError.__init__(self, s)

class HighProtocolError(ProtocolError):
	def __init__(self, s):
		ProtocolError.__init__(self, s)

class BadSpecial(ProtocolError):
	def __init__(self, s):
		ProtocolError.__init__(self, s)


class HandlerClass(SocketServer.StreamRequestHandler):
	def __init__(self, request, client_address, server):
		self.fromhex = codecs.getdecoder('hex_codec')
		self.tohex = codecs.getencoder('hex_codec')
		self.thash = md5.new()
		self.thash.update(KEY + '2')
		self.rhash = md5.new()
		self.rhash.update(KEY + '1')
		self.out = []
		SocketServer.StreamRequestHandler.__init__(self,
							request,
							client_address,
							server)

	def handle(self):
		print 'New handler'
		try:
			while self.handle_one():
				pass
		except ProtocolError, x:
			print "Error: %s" % x
			self.send('Z', 'ProtocolError: %s\n' % str(x))
			self.wclose()
		pylab.close('all')
		print 'Done'


	def get(self, prefix):
		tmp = self.rfile.readline()
		if tmp == '':
			raise EOF
		if tmp[0] != prefix:
			raise BadPrefixError, "Expected %s, got %s" % (prefix, tmp[0])
		tmp2 = self.fromhex(tmp[1:].strip())[0]
		self.rhash.update(tmp2)
		return tmp2


	def wclose(self):
		self.flush()
		self.wfile.close()


	def flush(self):
		if self.out:
			self.wfile.writelines( self.out )
			self.out = []
		self.wfile.flush()


	def send(self, prefix, s):
		self.out.append( '%s %s\n' % (prefix, self.tohex(s)[0]) )
		self.thash.update(s)
		if len(s) > 1000:
			self.flush()


	def handle_call(self):
		function = self.get('F')
		arg1 = self.get('A')
		arg2 = self.get('B')
		localhash = self.rhash.hexdigest()
		if self.get('H') != localhash:
			raise ProtocolError, 'Bad authentication'
		if self.get('E') != 'END':
			raise ProtocolError, 'No end'
		if not hasattr(pylab, function):
			self.report('AttributeError', function)
			return True

		print 'function=', function
		try:
			argt = cPickle.loads(arg1)
		except Exception, x:
			die.warn('Unpickling error: %s' % x)
			raise HighProtocolError, 'Unpickling problem: incompatible python or Numpy?'
			return False

		if not isinstance(argt, tuple):
			raise HighProtocolError, 'bad type 1'
			return False

		argd = cPickle.loads(arg2)
		if not isinstance(argd, dict):
			HighProtocolError, 'bad type 2'
			return False

		try:
			rv = getattr(pylab, function)(*argt, **argd)
		except Exception, x:
			self.report('Exception', (function, argt, argd, str(x)))
			return True

		self.report('OK', rv)
		return True

	def handle_list(self):
		localhash = self.rhash.hexdigest()
		if self.get('H') != localhash:
			raise ProtocolError, 'Bad authentication'
		if self.get('E') != 'END':
			raise ProtocolError, 'No end'
		self.report('list', list_fcns(pylab))
		return True


	def handle_exit(self):
		localhash = self.rhash.hexdigest()
		if self.get('H') != localhash:
			raise ProtocolError, 'Bad authentication'
		if self.get('E') != 'END':
			raise ProtocolError, 'No end'
		self.report('exit', None)
		return False


	def handle_one(self):
		try:
			id = self.get('I')
		except EOF:
			return False
		if id != ID:
			print 'ID=', id
			raise ProtocolError, 'ID mismatch'

		try:
			self.rqno = int( self.get('R') )
		except ValueError:
			raise ProtocolError, "Bad rqno."

		op = self.get('O')
		print 'op=', op

		if op == 'call':
			return self.handle_call()
		elif op == 'list':
			return self.handle_list()
		elif op == 'exit':
			return self.handle_exit()
		else:
			raise BadSpecial, 'No such op=%s' % op
		return False


	def report(self, code, rv):
		# print 'REPORT', code
		try:
			rvp = cPickle.dumps(rv, PP)
		except cPickle.UnpickleableError, x:
			rvp = cPickle.dumps(('UnpickleableError', str(x)), PP)
		except cPickle.PicklingError, x:
			rvp = cPickle.dumps(('PicklingError', str(x)), PP)
		self.send('i', ID)
		self.send('r', '%d' % self.rqno)
		self.send('c', code)
		self.send('v', rvp)
		self.send('h', self.thash.hexdigest() )
		self.send('e', 'END')
		self.flush()
		# print 'REPORTED'



if __name__ == '__main__':
	server_address = ('', Port)
	server = ServerClass(server_address, HandlerClass)
	print "Listening on port", server_address
	server.serve_forever()
