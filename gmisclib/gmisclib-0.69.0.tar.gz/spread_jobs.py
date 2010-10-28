#! python

"""
A module that starts a bunch of subprocesses and distributes
work amongst them, then collects the results.

Subprocesses must follow a protocol: they must listen for commands
on the standard input (commands are encoded with C{cPickle}),
and they must produce C{cPickle}d tuples on their standard output.
NOTE: THEY CANNOT PRINT ANYTHING ELSE!  (But it's OK for subprocesses
to produce stuff on the standard error output.)

PROTOCOL:

	1. Execcing state: C{spread_jobs} execs a group of subprocesses.  You have
	full control of the argument list.

	2. Preparation state: C{spread_jobs} will send a list of C{cPickled} things,
	one at a time to the subprocess.   No explicit terminator
	is added, so the subprocess must either know how many things
	are coming or the list should contain some terminator.
	(E.g. the last item of the list could be L{None}, and the
	subprocess would wait for it.)
	In this state, the subprocess must not produce anything on
	the standard output.

	3. Running state: C{spread_jobs} will send one C{cPickled} thing to the
	subprocess and then wait for a C{cPickled} C{tuple} to come
	back.  The C{tuple} has three items: (0) is an arbitrary payload,
	(1) a list of strings to be printed to the main processes'
	L{sys}.C{stdout}, and (2) another list of strings to be printed to
	the main processes' L{sys}.C{stderr}.   The arbitrary payload is
	put on a list and (when all the subprocesses are finished) handed
	to whoever called C{spread_jobs.main2}.

	4. Shutdown state: The subprocess can produce anything it wants.   This will
	be collected up and returned to the caller of C{spread_jobs.main2}.

You can use this to run certain normal linux commands by not sending anything
in the preparatory state or the running state.  You will then be handed
the standard output as a list of strings.

Normally, however, the action happens in the running state.

Normally, the subprocess looks much like this::

	import cPickle
	while True:
		try:
			control = cPickle.load(stdin)
		except EOFError:
			break
		d, so, se = compute(control)
		cPickle.dump((d, so, se), stdout, CP.HIGHEST_PROTOCOL)
		stdout.flush()
	stdout.close()

@sort: main2, main, replace, Replace, append
"""


from __future__ import with_statement

import re
import sys
import time
import random
from gyropy import g_mailbox as MB
import cPickle as CP
import threading
import subprocess
import StringIO

from gmisclib import die
from gmisclib import gpkmisc
# from gyropy import g_mailbox as MB


class notComputed(object):
	"""A singleton marker for values that haven't been computed."""
	pass



class NoResponse(RuntimeError):
	def __init__(self, *s):
		RuntimeError.__init__(self, *s)


class RemoteException(Exception):
	"""An exception that corresponds to one raised by a subprocess.
	This is raised in the parent process.
	"""
	def __init__(self, *s):
		Exception.__init__(self, *s)
		self.index = ''
		self.comment = ''

	def __repr__(self):
		return '<%s.RemoteException: %s>' % (__name__, repr(self.args))

	def raise_me(self):
		raise self



def _merge_and_raise(otmp):
	"""Get the contents of the list.
	@raise AssertionError: raised if there are some unfilled
		gaps remaining.
	@raise RemoteException: this is raised if there is one or
		more L{remoteException} instances on the list.
		(Essentially, the L{remoteException} instances are
		requests to raise, and they actually happen when
		you call L{get}.
	@return: the list
	@rtype: list(something)
	"""
	lot = len(otmp)
	olist = [None] * lot
	oi = set()
	for (i,x) in otmp:
		oi.add(i)
		assert 0 <= i < lot
		if isinstance(x, RemoteException):
			x.raise_me()
		assert x is not notComputed
		olist[i] = x
	assert len(oi)==lot
	return olist


class _ThreadJob(threading.Thread):
	def __init__(self, iqueue, p, stdin, solock):
		"""@param stdin: something to send at the start of the subprocess
			to get it going.   This is before the main processing starts.
		@type stdin: any iterable that yields something that can be
			given to L{cPickle.dumps}.
		@param p: The process to run.   It's already been started,
			but no input/output has occurred.
		@type p: L{subprocess.Popen}
		@param solock: a lock to serialize the standard output
		@type solock: threading.Lock
		"""
		threading.Thread.__init__(self)
		self.timing = []
		self.iqueue = iqueue
		self.olist = []
		self.p = p
		self.solock = solock
		for x in stdin:
			self.send(x)
	

	def run(self):
		while True:
			try:
				i, todo = self.iqueue.get()
			except MB.EOF:
				break
			if i is None:	# No-op to ensure that jobs can be re-queued before it all shuts down.
				time.sleep(0.001)
				continue
			t0 = time.time()
			try:
				self.send(todo)
			except IOError, x:
				die.warn("IO Error on send %d to worker: %s" % (i, str(x)))
				self.iqueue.put((i, todo))
				break
			try:
				q, so, se = self.get()
			except EOFError, x:
				die.warn("EOF error when central process reads %d from worker: %s" % (i, str(x)))
				self.iqueue.put((i, todo))
				break
			t2 = time.time()
			self.timing.append(t2-t0)
			self.olist.append( (i, q) )
			with self.solock:
				if so:
					sys.stdout.writelines('#slot so%d ------\n' % i)
					sys.stdout.writelines(so)
					sys.stdout.flush()
				if se:
					sys.stderr.writelines('#slot se%d ------\n' % i)
					sys.stderr.writelines(se)
					sys.stderr.flush()
			if isinstance(q, RemoteException):
				die.info("Remote Exception info: %s" % str(q.args))
				die.warn("Exception from remote job (index=%d): %s" % (i, str(q)))
				q.index = "index=%d" % i
				q.comment = "so=%s # se=%s" % (gpkmisc.truncate(';'.join(so), 40),
									gpkmisc.truncate(';'.join(se), 40)
									)
				# Eat all remaining jobs
				while True:
					try:
						i, todo = self.iqueue.get()
					except MB.EOF:
						break
					if i is not None:
						self.olist.append( (i, notComputed) )
		self.close()


	def send(self, todo):
		CP.dump(todo, self.p.stdin)
		self.p.stdin.flush()
		# sys.stdout.write('send - completed.\n')


	def get(self):
		while True:
			try:
				q, so, se = CP.load(self.p.stdout)
				return (q, so, se)
			except CP.UnpicklingError, y:
				die.warn("spread_load: Junk response: %s" % str(y))
				die.info("Remainder: %s" % self.p.stdout.readline())
				continue
		return None


	def close(self):
		self.p.stdin.close()

	def wait(self):
		tmp = self.p.stdout.readlines()
		self.p.wait()
		self.p.stdout.close()
		return tmp


def main2(todo, list_of_args, stdin=None, verbose=False, timing_callback=None):
	"""Pass a bunch of work to other processes.
	@param stdin: a list of stuff to send to the other processes before the computation is
		properly commenced.
	@type stdin: list(whatever)
	@param todo: a list of work to do
	@type todo: list(whatever)
	@param list_of_args:
	@type list_of_args:  list(list(str))
	@rtype: C{tuple(list(whatever), list(list(str)))}
	@return: A 2-tuple.   The first item is
		a list of the results produced by the other processes.
		Items in the returned list correspond to items in the todo list.
		These are the stuff that comes out, pickled, on the standard
		output after each chunk of data is fed into the standard input.
		The second item is a list of the remaining outputs, as read
		by file.readlines(); these are one per process.
	"""
	# sys.stderr.write('main starting\n')
	if stdin is None:
		stdin = []
	ths = []
	solock = threading.Lock()
	iqueue = MB.mailbox()
	for args in list_of_args:
		# There seems to be an issue with forking simultaneously
		# from many threads.   Since the file descriptors are
		# shared, various things get closed that should be left
		# open and vice versa.    See http://psf.upfronthosting.co.za/roundup/tracker/issue2320
		# and http://bugs.python.org/issue7213 .
		# So, we fork in the main thread and pass the process to the new thread.
		p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr,
						close_fds=True
						)
		t = _ThreadJob(iqueue, p, stdin, solock)
		t.start()
		ths.append(t)
	for (i, job) in enumerate(todo):
		iqueue.put( (i,job) )
	for i in range(len(args)):
		# These are No-ops, just to give an opportunity for failed jobs to be re-queued.
		iqueue.put((None, None))
	iqueue.putclose()
	timing = []
	oo = []
	otmp = []
	for t in ths:
		t.join()
		timing.extend(t.timing)
		oo.append(t.wait())
		otmp.extend(t.olist)
	olist = _merge_and_raise(otmp)
	assert len(olist) == len(todo)
	if timing_callback is not None:
		timing_callback(timing)
	return (olist, oo)


def main(todo, list_of_args, stdin=None, verbose=False, timing_callback=None):
	"""Pass a bunch of work to other processes.
	@param stdin: a list of stuff to send to the other processes before the computation is
		properly commenced.
	@type stdin: list(whatever)
	@param todo: a list of work to do
	@type todo: list(whatever)
	@param list_of_args:
	@type list_of_args:  list(list(str))
	@rtype: list(whatever)
	@return: a list of the results produced by the other processes.
		Items in the returned list correspond to items in the todo list.
	"""
	return main2(todo, list_of_args, stdin, verbose, timing_callback)[0]




def test_worker():
	sys.stderr.write('test_worker starting\n')
	while True:
		sys.stderr.write('test_worker loop\n')
		try:
			txt = CP.load(sys.stdin)
		except EOFError:
			sys.stderr.write('test_worker got EOF\n')
			break
		if random.random() < 0.5:
			time.sleep(random.expovariate(30.0))
		sys.stderr.write('test worker control=%s\n' % txt)
		if txt is None:
			sys.stderr.write('test_worker got stop\n')
			break
		sys.stderr.write('test_worker dump %s\n' % txt)
		CP.dump((txt, ['stdout:%s\n' % txt], ['stderr\n']), sys.stdout, CP.HIGHEST_PROTOCOL)
		sys.stdout.flush()
	sys.stderr.write('test_worker finished\n')
	sys.stdout.close()


def test():
	for np in range(1, 5):
		print 'NP=%d' % np
		for i in range(1, 6):
			print 'ntasks=%d' % (i*5)
			x = ['a', 'b', 'c', 'd', 'e'] * i
			args = ['python', sys.argv[0], 'worker']
			y = main(x, [args]*np )
			assert x == y



class unpickled_pseudofile(StringIO.StringIO):
	"""For testing.
	"""

	def __init__(self):
		StringIO.StringIO.__init__(self)

	def close(self):
		self.seek(0, 0)
		while True:
			try:
				d, so, se = CP.load(self)
			except EOFError:
				break
			sys.stdout.write('STDOUT:\n')
			sys.stdout.writelines(so)
			sys.stdout.write('STDERR:\n')
			sys.stdout.writelines(se)
			sys.stdout.write('d=%s\n' % str(d))
			sys.stdout.flush()


def one_shot_test(input):
	stdin = StringIO.StringIO()
	CP.dump(input, stdin)
	stdin.flush()
	stdin.seek(0, 0)
	stdout = unpickled_pseudofile()
	return (stdin, stdout)



def replace(list_of_lists, *fr):
	assert isinstance(list_of_lists, list)
	frc = []
	while fr:
		frc.append( (re.compile(fr[0]), fr[1]) )
		fr = fr[2:]
	o = []
	for l in list_of_lists:
		assert isinstance(l, (tuple, list)), "List of lists contains %s within %s" % (repr(l), list_of_lists)
		tmp = []
		for t in l:
			for (find, repl) in frc:
				assert isinstance(t, str), "whoops! t=%s" % str(t)
				t = find.sub(repl, t)
			tmp.append(t)
		o.append(tmp)
	return o


def Replace(list_of_lists, pat, length, replacement):
	assert isinstance(replacement, list)
	assert length > 0
	cpat = re.compile(pat)
	o = []
	for l in list_of_lists:
		assert isinstance(l, (tuple, list)), "List of lists contains %s within %s" % (repr(l), list_of_lists)
		tmp = list(l)
		while tmp:
			found = None
			print 'X=', tmp
			for (i, t) in enumerate(tmp):
				if cpat.match(t):
					print 'MATCH %s to %s' % (t, pat)
					found = i
					break
			if found is not None:
				print 'REPLACE %s -> %s' % (str(tmp[i:i+length]), str(replacement))
				tmp[i:i+length] = list(replacement)
			else:
				break
		o.append(tmp)
	return o


def append(list_of_lists, *a):
	o = []
	for l in list_of_lists:
		tmp = tuple(l) + a
		o.append(tmp)
	return o


if __name__ == '__main__':
	if len(sys.argv)==2 and sys.argv[1] == 'worker':
		test_worker()
	else:
		test()
