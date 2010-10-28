#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import time
import math
import random
import socket
import hashlib
import threading
import SocketServer

from gmisclib import die
from gmisclib import gpkmisc
from gmisclib import g_encode
from gmisclib import mcmc_cooperate as MC

Key = None
__version__ = MC.Barrier(0, 1, 0)
Verbose = False


class User(object):
	def __init__(self):
		self.barrier = MC.Barrier(0)
		self.info = {}
		self.reply = None


	def set_barrier(self, b):
		assert isinstance(b, MC.Barrier)
		self.barrier = b




class job(object):
	def __init__(self):
		self.vec = None
		self.vec_from = None
		self.logp = None
		self.users = {}
		self.size = None
		self.cache = {}
		self.c = threading.Condition()
		self.barrier = MC.Barrier(0)
		self._seed = 0

	def seed(self):
		self._seed += 1
		return self._seed
	

	def set_info(self, my_id, args):
		if len(args)<2 or len(args)%2 != 0:
			return ["Fail", "wrong number of args", len(args)]
		while args:
			value = args.pop()
			key = args.pop()
			self.users[my_id].info[key] = value
			self.cache[key] = {}
		return ["OK"]

	def get_info(self, args):
		if len(args) != 1:
			return ["Fail", "wrong number of args", len(args)]
		key = args[0]
		return ["OK"] + [q.info.get(key, '') for q in self.users.values()]

	def get_combined(self, operation, args):
		if len(args) != 2:
			return ["Fail", "wrong number of args", len(args)]
		key, operation = args
		try:
			return ["OK"] + self.cache[key][operation]
		except KeyError:
			pass
		tmp = [q.info[key] for q in self.users.values() if key in q.info]
		if not tmp:
			return ["Fail", "No info", key]
		if operation not in MC.Ops:
			return ["Fail", "No such operation", operation]
		rv = MC.Ops[operation](tmp)
		if key not in self.cache:
			self.cache[key] = {}
		self.cache[key][operation] = rv
		return ["OK"] + rv


	def T(self):
		try:
			return self.cache["T"]["_temperature"]
		except KeyError:
			pass
		tmp = [ float(q.info.get('T', '1')) for q in self.users.values()]
		if "T" not in self.cache:
			self.cache["T"] = {}
		T = gpkmisc.median(tmp)
		self.cache["T"]["_temperature"] = T
		return T


	def rank(self, my_id):
		with self.c:
			return sorted(self.users.keys()).index(my_id)

	def get_vector(self):
		with self.c:
			if self.vec is None:
				reply = ["Fail", "No vector"]
			else:
				reply = ["OK", self.logp, self.vec]
		return reply


	def set_vector(self, my_id, args):
		if len(args) != 3:
			return ["Fail", "wrong number of arguments", len(args)]
		with self.c:
			try:
				size = int(args[0])
			except ValueError:
				size = -1
			try:
				logp = float(args[1])
			except ValueError:
				logp = None
	
			if not (size > 0):
				reply = ["Fail", "Bad size", args[0]]
			elif logp is None:
				reply = ["Fail", "Bad logp", args[1]]
			elif self.size is not None and self.size!=size:
				self.size = None
				self.vec = None
				self.logp = None
				reply = ["Fail", "Size mismatch", args[0], "was", self.size]
			else:
				self.size = size
				if self.logp is None or logp > self.logp - random.expovariate(1.0/self.T()):
					reply = ["OK", "accepted", "was", self.logp]
					self.logp = logp
					self.vec = args[2]
					self.vecfrom = my_id
				else:
					reply = ["OK", "rejected", "was", "%g" % self.logp]
		return reply



	def pass_barrier(self, my_id, args):
		if len(args) != 2:
			return ["Fail", "wrong number of args", len(args)]
		try:
			nmin = int(args[1])
		except ValueError:
			nmin = -1
		if nmin < 0:
			return ["Fail", "bad nmin", args[1]]
		barrier = MC.Barrier(args[0])
		with self.c:
			if barrier < self.barrier:
				return ["Late", self.barrier]
			self.users[my_id].set_barrier(barrier)
			minb = None
			for (mid, u) in self.users.items():
				if minb is None or u.barrier<minb:
					minb = u.barrier
			if self.barrier is None or minb > self.barrier:
				self.c.notifyAll()
				self.barrier = minb
			
			while len(self.users)>=nmin and barrier>self.barrier:
				self.c.wait()
		return ["OK"]


def truncate(*a):
	o = []
	for (i,x) in enumerate(a):
		x = str(x)
		lmax = int(round(25/math.sqrt(2+i)))
		if len(x) < lmax:
			o.append(x)
		else:
			o.append(x[:lmax] + '...')
	return ' '.join(o)




class HandlerClass(SocketServer.StreamRequestHandler):
	lock = threading.Lock()
	olock = threading.Lock()
	s = {}
	e = MC.encoder
	_seed = hash(open("/dev/urandom", "r").read(16))

	def seed(self):
		return "%d.%d" % (self._seed, len(self.s))


	def __init(self, request, client_address, server):
		SocketServer.StreamRequestHandler.__init__(self,
							request,
							client_address,
							server)
	

	def handle(self):
		with self.olock:
			die.info("New handler")
		while True:
			data = [self.e.back(q) for q in self.rfile.readline().strip().split()]
			if not data:
				break

			reply = self.handler_guts(data)
			if reply is None:
				if Verbose:
					with self.olock:
						die.info("%s deferred" % truncate(*data))
				continue
			assert len(reply)>=1
			if Verbose:
				with self.olock:
					die.info("%s -> %s" % (truncate(*data), truncate(*reply)))
			self.wfile.write(' '.join([self.e.fwd(str(q)) for q in reply]) + '\n')
			self.wfile.flush()
			if len(reply)==2 and reply==("OK", "terminated"):
				break
		with self.olock:
			die.info("Handler done")


	def sleep(self):
		time.sleep(min(4.0, random.expovariate(1.0)))


	def _connect(self, job_id, seed, args):
		if hashlib.sha1('%s:%s:%s' % (Key, job_id, seed)).hexdigest() != args[0]:
			self.sleep()
			return ["Fail", "authentication"]

		with self.lock:
			try:
				j = self.s[job_id]
				die.info('Connected to existing job %s %s' % (job_id, j))
			except KeyError:
				j = job()
				self.s[job_id] = j
				die.info('Connected to new job %s %s' %(job_id, j))
			# No need to lock j because self.s is still locked, so no one else
			# can access it.
			my_id = hashlib.sha1('%s:%s:%s:%s:%s' % (Key, job_id, seed, self.seed(), j.seed())).hexdigest()
			assert my_id not in j.users
			j.users[my_id] = User()
			reply = ["OK", my_id]
		self.sleep()
		return reply




	def handler_guts(self, data):
		if not data:
			return ["Fail", "Empty request"]
		command = data[0]

		if command == "version":
			return ["OK", __version__, MC.__version__]

		if len(data) < 3:
			return ["Fail", "too few arguments", len(data)]
		job_id = data[1]
		my_id = data[2]
		args = data[3:]
		if command == "connect":
			return self._connect(job_id, my_id, args)

		with self.lock:
			try:
				j = self.s[job_id]
			except KeyError:
				die.warn("Missing job: %s %s %s %s %s" % (job_id, self.s.keys(), my_id, command, args))
				self.sleep()
				return ["Fail", "No such job", command, job_id]
			if my_id not in j.users:
				self.sleep()
				return ["Fail", "Not attached to", command, job_id]

		assert my_id in j.users
		assert job_id in self.s
		if command.startswith('*'):
			if j.users[my_id].reply:
				if Verbose:
					with self.olock:
						die.info("Ignoring *%s because of previous %s" % (command, truncate(j.users[my_id].reply)))
				return None
			command = command[1:]
			defer_reply = True
		else:
			r = j.users[my_id].reply
			if r:
				j.users[my_id].reply = None
				if Verbose:
					with self.olock:
						die.info("Ignoring %s because of previous %s" % (command, truncate(r)))
				return r
			defer_reply = False

		if command == "barrier":
			reply = j.pass_barrier(my_id, args)
		elif command == "leave":
			with self.lock:
				with j.c:
					j.users.pop(my_id, None)
					if not j.users:
						die.info("Deleting job %s" % job_id)
						self.s.pop(job_id, None)
				reply = ["OK", "terminated"]
		elif command == "shutdown":
			with self.lock:
				self.s.pop(job_id, None)
				reply = ["OK", "terminated"]
		elif command == "get_vector":
			reply = j.get_vector()
		elif command == "set_vector":
			reply = j.set_vector(my_id, args)
		elif command == "set_info":
			reply = j.set_info(my_id, args)
		elif command == "get_info_list":
			reply = j.get_info(args)
		elif command == "get_info_combined":
			reply = j.get_combined(my_id, args)
		elif command == "rank":
			with j.c:
				reply = ["OK", len(j.users), j.rank(my_id)]
		elif command == "list_ops":
			reply = ["OK"] + MC.Ops.keys()
		else:
			reply = ["Fail", "Unknown command", command]
			self.sleep()

		if defer_reply:
			if Verbose:
				with self.olock:
					die.info("Deferred %s -> %s" % (command, truncate(reply)))
			if reply[0] != "OK":
				j.users[my_id].reply = reply
			return None
		return reply
	

if __name__ == '__main__':
	import sys
	if sys.argv[1] == '-v':
		sys.argv.pop(1)
		Verbose = True
	Key = sys.argv[1]
	sys.argv[1] = "Key"
	HOST, PORT = "localhost", 8487
	server = SocketServer.ThreadingTCPServer((HOST, PORT), HandlerClass)
	server.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)
	server.serve_forever()
