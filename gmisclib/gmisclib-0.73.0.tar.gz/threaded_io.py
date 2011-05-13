"""This is designed to let you do asynchronous I/O conveniently.
"""

from __future__ import with_statement

import sys
import threading
import system_load as SL

Lock = threading.Lock

class CaughtException(object):
	def __init__(self, x):
		self.ex_type, self.ex_value, self.ex_traceback = x

	def __repr__(self):
		return "CaughtException: %s" % str(self.ex_value)

	def reraise(self):
		raise self.ex_type, self.ex_value, self.ex_traceback


class threading_with_result(threading.Thread):
	def __init__(self, tag=None, group=None, target=None, name=None, args=(), kwargs={}):
		threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs)
		self.rv = None
		self.rvset = False
		self.tag = tag

	def run(self):
		try:
			self.rv = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
		except:
			self.rv = CaughtException(sys.exc_info())
		self.rvset = True

	def get(self):
		assert self.rvset
		check_n_raise(self.rv)
		return self.rv



def to_be_joined(tlist):
	"""Pick a ripe thread for joining.
	@type tlist: list(L{threading.Thread})
	@param tlist: a list of threads.
	@return: a thread that is either finished and ready to be joined,
		or (if none are ready yet) the oldest thread.
	@rtype: L{threading.Thread}
	"""
	for (i, t) in enumerate(tlist):
		if not t.isAlive():
			return tlist.pop(i)
	return tlist.pop(0)


class Thread_poolW(object):
	"""Here, you have a pool of n threads.   You can call
	C{x.start(function, args, kwargs)} to start something running
	(perhaps a write to a file), and then go off and compute
	something else while the I/O completes.
	If you need to wait for completion, call C{x.join()}.

	This class is not designed to return values from the function.
	"""

	def __init__(self, n=None):
		if n is None:
			n = SL.ncpu()
		if not ( n > 0 ):
			raise ValueError, "n(processors) must be positive."
		self.n = n
		self.t = []


	def start(self, fn, args=None, kwargs=None):
		while len(self.t) >= self.n:
			to_be_joined(self.t).join()
		t = threading.Thread(target=fn, args=args, kwargs=kwargs)
		t.start()
		self.t.append(t)


	def join(self):
		while self.t:
			self.t.pop(0).join()


Thread_poolNR = Thread_poolW	# Obsolete


def check_n_raise(x):
	if isinstance(x, CaughtException):
		x.reraise()
	return x


class Thread_poolR(object):
	"""Here, you have a pool of n threads.   You can call
	C{x.start(function, args, kwargs)} to start something running
	(perhaps a write to a file), and then go off and compute
	something else while the I/O completes.
	If you need to wait for completion, call C{x.join()}.

	This class is designed to return values from the function via
	C{get()} or C{getany()}.
	"""

	def __init__(self, n=None):
		if n is None:
			n = SL.ncpu()
		if not ( n > 0 ):
			raise ValueError, "n(processors) must be positive."
		self.n = n
		self.t = []
		self.lock = threading.Lock()
		self.answers = []


	def start(self, tag, fn, args=None, kwargs=None):
		with self.lock:
			if len(self.t) >= self.n:
				self.__join_one()
			t = threading_with_result(tag=tag, target=fn, args=args, kwargs=kwargs)
			t.start()
			self.t.append(t)


	def __join_one(self):
		if self.t:
			t = to_be_joined(self.t)
			t.join()
			self.answers.append( (t.tag, t.get()) )
		else:
			raise StopIteration



	def getany(self):
		"""
		@return: the first available answer, as a (tag, value) pair.   The tag was set
			in the call to C{start} and the value is the result of the computation.
			If the computation raised an exectption, C{getany} will return a CaughtException
			object instead.
		@rtype: a tuple(whatever, whatever) pair from a computation or a L{CaughtException}
		"""
		with self.lock:
			if not self.answers:
				self.__join_one()
			return self.answers.pop(0)


	def get(self, tag):
		"""
		@rtype: whatever or a L{CaughtException}
		"""
		with self.lock:
			i = 0
			while i < len(self.answers):
				tg,v = self.answers[i]
				if tg == tag:
					del self.answers[i]
					return v
				else:
					i += 1
			i = 0
			while i < len(self.t):
				t = self.t[i]
				if t.tag == tag:
					t.join()
					del self.t[i]
					return t.get()
				else:
					i += 1
			raise KeyError, "Tag %s has not yet been started." % tag


	def has_answer(self):
		"""Is there an answer ready?"""
		with self.lock:
			return len(self.answers)


	def loaded(self):
		"""Have we loaded up all the processors?"""
		with self.lock:
			return len(self.t) >= self.n

	def join(self):
		while self.t:
			self.__join_one()


def pairmap(fn, inlist, *args, **kwargs):
	tp = Thread_poolR(kwargs.get('_poolsize', None))
	no = 0
	s = 0
	for (j,xi) in enumerate(inlist):
		tp.start(xi, fn, (xi,)+args, kwargs)
		s += 1
		if tp.loaded():
			no += 1
			yield tp.getany()
	while no < s:
		yield tp.getany()
		no += 1
	

def testmap():
	q = list(pairmap(lambda x:x, range(10)))
	assert len(q)==10
	seen = set()
	for (i,j) in q:
		assert i==j
		seen.add(i)
	assert sorted(seen)==range(10)


if __name__ == '__main__':
	testmap()
