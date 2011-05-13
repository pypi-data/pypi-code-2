# -*- coding: utf-8 -*-

import socket
import random
import hashlib
import cPickle

import g_encode



class Barrier(object):
	def __init__(self, *x):
		"""Constructs a barrier from a list of integers.
		"""
		if len(x)==1 and isinstance(x[0], str):
			self.x = tuple([int(q) for q in x[0].split('.')])
		else:
			self.x = tuple(x)
		for tmp in self.x:
			if not (tmp >= 0):
				raise ValueError, "Nonpositive component of Barrier: %s" % tmp
	
	def __cmp__(self, other):
		return cmp(self.x, other.x)


	def __iadd__(self, other):
		if len(other.x) > len(self.x):
			xl = list(other.x)
			for (i, x) in enumerate(self.x):
				xl[i] += x
		else:
			xl = list(self.x)
			for (i, x) in enumerate(other.x):
				xl[i] += x
		self.x = tuple(xl)
		return self

	def __repr__(self):
		return '.'.join([str(q) for q in self.x])

	def deepen(self, v):
		return Barrier( *(self.x + (v,)) )

assert Barrier(12) == Barrier(12)
assert Barrier(11) > Barrier(10)
assert Barrier(1, 3) > Barrier(1, 1)
assert Barrier(1, 3) > Barrier(1)
assert Barrier(2) > Barrier(1, 3)
assert Barrier(2, 1) > Barrier(1, 3)


class Oops(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)

class LateToBarrier(Oops):
	def __init__(self, *s):
		Oops.__init__(self, *s)


encoder = g_encode.encoder(regex=r"""[^a-zA-Z0-9<>?,./:";'{}[\]!@$^&*()_+=|\\-]""")


class connection(object):
	e = encoder

	def __init__(self, host, port, Key, jobid):
		self.my_id = None
		self.host = host
		self.port = port
		self.jobid = jobid
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)
		seed = hash(open("/dev/urandom", "r").read(16))
		x = hashlib.sha1('%s:%s:%s' % (Key, self.jobid, seed)).hexdigest()
		self.sf = self.sock.makefile("w", 4096)
		self.rf = self.sock.makefile("r", 4096)
		assert self.version()[1] == __version__
		self.send("connect", jobid, seed, x)
		self.flush()
		self.my_id = self.recv()[1]
	
	def send(self, *s):
		assert s
		self.sf.write(' '.join([self.e.fwd(str(q)) for q in s]) + '\n')
	
	def flush(self):
		self.sf.flush()
		
	def recv(self):
		tmp = [self.e.back(q) for q in self.rf.readline().strip().split()]
		if not tmp:
			raise Oops("Empty response")
		if tmp[0] == "Fail":
			raise Oops(*(tmp[1:]))
		return tmp
	
	def list_ops(self):
		self.send("list_ops", self.jobid, self.my_id)
		self.flush()
		return self.recv()[1:]

	def version(self):
		self.send("version")
		self.flush()
		return [Barrier(q) for q in self.recv()[1:]]
	
	def rank(self):
		"""@return: number_of_processes, rank_of_this_process
		@rtype: (int, int)
		"""
		self.send("rank", self.jobid, self.my_id)
		self.flush()
		a = self.recv()
		return (int(a[1]), int(a[2]))
	
	def close(self):
		self.send("leave", self.jobid, self.my_id)
		self.flush()
		self.recv()
		self.my_id = None
	
	def __del__(self):
		if self.my_id is not None:
			self.close()

	def barrier(self, b, nmin=0, exc=True):
		self.send("barrier", self.jobid, self.my_id, b, nmin)
		self.flush()
		x = self.recv()
		if exc and x[0]!="OK":
			raise LateToBarrier(x[1])
		if x[0]=="OK":
			return None
		return Barrier(x[1])

	def swap_vec(self, logp, v):
		"""@return: (logp, vector)
		"""
		size = v.shape[0]
		self.send("*set_vector", self.jobid, self.my_id, size, logp, cPickle.dumps(v))
		self.send("get_vector", self.jobid, self.my_id)
		self.flush()
		lp, v = self.recv()[1:]
		return (float(lp), cPickle.loads(v))

	def set(self, *kv):
		assert len(kv)>=2 and len(kv)%2 == 0
		self.send("set_info", self.jobid, self.my_id, *kv)
		self.flush()
		self.recv()
	
	def get_list(self, key):
		self.send("get_info_list", self.jobid, self.my_id, key)
		self.flush()
		return self.recv()[1:]

	def get_combined(self, key, operation):
		self.send("get_info_combined", self.jobid, self.my_id, key, operation)
		self.flush()
		return Unpack[operation](self.recv()[1])

	def spread(self, key, value, barrier, nmin=0):
		self.send("*barrier", self.jobid, self.my_id, barrier.deepen(0), nmin)
		self.send("*set_info", self.jobid, self.my_id, key, value)
		self.send("*barrier", self.jobid, self.my_id, barrier.deepen(1), nmin)
		self.send("get_info_list", self.jobid, self.my_id, key)
		self.flush()
		tmp = self.recv()
		return tmp[1:]


	def get_consensus(self, key, value, barrier, operation, nmin=0):
		self.send("*barrier", self.jobid, self.my_id, barrier.deepen(0), nmin)
		self.send("*set_info", self.jobid, self.my_id, key, value)
		self.send("*barrier", self.jobid, self.my_id, barrier.deepen(1), nmin)
		self.send("get_info_combined", self.jobid, self.my_id, key, operation)
		self.flush()
		return self.recv()[1]


def test0():
	import time
	test = connection(*test_args)
	test.set("a", "A")
	# test.barrier(Barrier(1))
	time.sleep(random.expovariate(1.0))
	test.set("a", "B")
	time.sleep(random.expovariate(1.0))
	test.barrier(Barrier(2))
	time.sleep(random.expovariate(1.0))
	for x in test.get_list("a"):
		assert x == "B"
	time.sleep(random.expovariate(1.0))
	test.barrier(Barrier(3))
	test.barrier(Barrier(4))
	test.set("a", "C")
	test.close()
	print "Test0 OK"


def test0s():
	import time
	test = connection(*test_args)
	test.set("a", "A")
	time.sleep(random.expovariate(1.0))
	test.barrier(Barrier(1))
	print "Barrier 1s"
	time.sleep(random.expovariate(1.0))
	test.barrier(Barrier(1, 3))
	print "Barrier1.3s"
	time.sleep(random.expovariate(1.0))
	tmp = test.spread("a", "x", Barrier(1, 3))
	print "test.spread 0s tmp=", tmp
	for x in test.get_list("a"):
		assert x == "x"
	time.sleep(random.expovariate(1.0))
	test.barrier(Barrier(3))
	test.set("a", "B")
	test.close()
	print "Test0s OK"

def test1():
	import time
	test = connection(*test_args)
	print "rank=", test.rank()
	test.set("key", "value")
	assert "value" in test.get_list("key")
	time.sleep(random.expovariate(100.0))
	test.set("k2", "2", "k", "wahoonie")
	test.barrier(Barrier(1))
	print 'Barrier 1'
	time.sleep(random.expovariate(100.0))
	test.barrier(Barrier(1, 1))
	time.sleep(random.expovariate(100.0))
	test.set("k2", "1", "k", "no_value")
	test.barrier(Barrier(2))
	print 'Barrier 2'
	time.sleep(random.expovariate(100.0))
	test.barrier(Barrier(2, 0, 1))
	tmp = test.get_list("k2")
	assert tmp[0] == "1", "tmp=%s" % tmp
	test.barrier(Barrier(2, 1))
	print 'Barrier 2.1'
	test.set("k2", "2", "k", "wahoonie")
	time.sleep(random.expovariate(100.0))
	test.barrier(Barrier(2, 1, 1))
	tmp = test.get_list("k")
	assert tmp[0] == "wahoonie", "tmp=%s" % tmp
	test.set("k3", "x y")
	assert "x y" in test.get_list("k3")
	time.sleep(random.expovariate(100.0))
	assert test.get_combined("k2", 'float_median') == 2.0
	test.barrier(Barrier(3))
	time.sleep(random.expovariate(100.0))
	test.barrier(Barrier(3))
	time.sleep(random.expovariate(100.0))
	assert test.barrier(Barrier(2), exc=False) == Barrier(3)
	time.sleep(random.expovariate(100.0))
	assert test.barrier(Barrier(1), exc=False) == Barrier(3)
	time.sleep(random.expovariate(100.0))
	assert test.barrier(Barrier(3)) is None
	time.sleep(random.expovariate(100.0))
	assert test.barrier(Barrier(4)) is None
	assert test.spread("k3", "x", Barrier(6))[0] == "x"
	time.sleep(random.expovariate(100.0))
	assert test.get_consensus("k3", "a", Barrier(6, 3), "string_median") == "a"
	test.barrier(Barrier(7))
	print "barrier 7"
	tmp = test.spread("k3", "x", Barrier(7, 3))
	assert tmp[0] == "x", "tmp= %s" % tmp
	time.sleep(random.expovariate(100.0))
	test.close()

def test_many(n, fcn):
	import threading
	t = []
	for i in range(n):
		t.append( threading.Thread(target=fcn) )
	for tt in t:
		tt.start()
	for tt in t:
		tt.join()


__version__ = Barrier(0, 1, 0)


def op_string_median(tmp):
	tmp.sort()
	n = len(tmp)
	if n%2 == 1:
		return [ tmp[n//2] ]
	return [ random.choice([tmp[(n-1)//2], tmp[n//2]]) ]


def op_float_median(tmp):
	try:
		tmp = sorted([float(q) for q in tmp])
	except ValueError, x:
		return "Bad data: %s" % str(x)
	n = len(tmp)
	if n%2 == 1:
		return [ tmp[n//2] ]
	return [ 0.5*(tmp[(n-1)//2] + tmp[n//2]) ]


Ops = {'string_median': op_string_median,
		'float_median': op_float_median
		}
Unpack = {'float_median': float, 'string_median': str}

test_args = ('localhost', 8487, "K", "job")

if __name__ == '__main__':
	test_many(2, test0s)
	# print 'Test_many(2s) OK'
	test_many(2, test0)
	# print 'Test_many(2) OK'
	test1()
	print 'Test1 OK'
	test_many(2, test1)
	test_many(11, test0s)
	test_many(11, test0)
	test_many(11, test1)
	# print "OK"
