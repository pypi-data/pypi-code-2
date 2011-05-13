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
	back.

	The request to the subprocess is a C{tuple(int, arbitrary)}.
	The L{int} is a task-ID number which must be returned with the answer.
	The C{arbitrary} is whatever information the subprocess needs to do its job.

	The subprocess responds with a 3-L{tuple}.   The first element of the
	tuple is either:
	
		- An instance of L{TooBusy}.  This causes the main process to
			put the task back on the queue and ignore this subprocess for
			a while.  The second element is printed; the third is ignored.
		- An instance of L{RemoteException}.   This leads to termination of
			the job and causes an exception to be raised on the main thread.
			The other two elements of the tuple are printed.
		- Anything else.   In that case, the first element is returned on the
			output list and the other two elements are printed.

	The subprocess loops in the running state.
	Normally, it should terminate when its standard input is closed.
	(It can terminate itself if it wishes by simply closing the standard output and exiting.)

	4. Shutdown state: The subprocess can produce anything it wants.   This will
	be collected up and returned to the caller of C{spread_jobs.main}.

	You can use this to run certain normal linux commands by not sending anything
	in the preparatory state or the running state.  You will then be handed
	the standard output as a list of strings.

Normally, the action happens in the running state.

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

@sort: main, replace, Replace, append
"""


from __future__ import with_statement

import re
import sys
import math
import time
import random
import cPickle as CP
import threading
import subprocess
import StringIO

from gmisclib import die
from gmisclib import gpkmisc
from gmisclib import dictops
from gyropy import g_mailbox as MB
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


class TooBusy(object):
	def __init__(self, delay):
		self.delay = delay



class PastPerformance(dictops.dict_of_averages):
	def __init__(self):
		dictops.dict_of_averages.__init__(self)
	
	def add_many(self, kvpairs):
		for (k, v) in kvpairs:
			self.add(k, v)
	
	def __call__(self, x):
		s = 0.5
		n = 1
		for t in x:
			try:
				sm, wts = self.get_both(str(t))
			except KeyError:
				sm, wts = 0.5, 1.0
			n += wts
			s += sm
		return -s/n


class Connection(object):
	"""This class represents a connection from the master process down to one of the slaves.
	It also keeps track of how often the slave reports that it is too busy to work.
	"""
	def __init__(self, arglist):
		"""
		@param arglist: an argument list to execute to start a subprocess.
		@type arglist: a sequence of anything that can be converted to strings.
		@note: This is where the arglist is finally converted to a list of strings.
		@except OSError: when connection cannot be set up.
		"""
		self.arglist = [str(q) for q in arglist ]
		self.OSError = OSError
		self.EOFError = EOFError
		self.SendError = (IOError, ValueError)
		self.lock = threading.Lock()
		self.uness = 1.0
	
	def send(self, todo):
		"""@except IOError: Trouble sending."""
		raise RuntimeError, "Virtual Method"

	def get(self):
		"""@return: (answer, standard_output, standard_error) or None.
		@except EOFError: No data available from slave.
		"""
		raise RuntimeError, "Virtual Method"

	def close(self):
		"""Closes the channel to the slave."""
		raise RuntimeError, "Virtual Method"

	def wait(self):
		"""Waits for the slave to terminate and closes the channel from the slave.
		@return: any final output.
		@rtype: list(str)
		"""
		raise RuntimeError, "Virtual Method"

	def argstring(self):
		return ' '.join(self.arglist)

	BUSYFAC1 = 0.85
	BUSY3 = 0.01
	BUSYFAC2 = (1-BUSYFAC1)/(1+BUSY3)
	
	def usefulness(self):
		with self.lock:
			assert 0 <= self.uness <= 1.0
			return self.uness

	def I_am_working(self, now):
		with self.lock:
			self.uness = self.uness*self.BUSYFAC1 + self.BUSYFAC2*(now + self.BUSY3)
			# The logic is that even if it's been busy 1000 times in a row,
			# there is always some chance that conditions will change and it
			# will become available for work.   So, usefulness should never
			# be zero unless it is shut down.

	def mystate(self, state):
		if state != "running":
			with self.lock:
				self.uness = 0.0

	def performance(self):
		u = self.usefulness()
		for arg in self.arglist:
			yield (arg, u)


class Connection_subprocess(Connection):
	"""This is a L{Connection} via stdin/stdout to a subprocess."""

	def __init__(self, arglist):
		Connection.__init__(self, arglist)
		self.p = subprocess.Popen(self.arglist, stdin=subprocess.PIPE,
						stdout=subprocess.PIPE, stderr=sys.stderr,
						close_fds=True
						)
	
	def send(self, todo):
		CP.dump(todo, self.p.stdin)
		self.p.stdin.flush()
		# sys.stdout.write('send - completed.\n')


	def get(self):
		while True:
			try:
				rv = CP.load(self.p.stdout)
				return rv
			except CP.UnpicklingError, y:
				die.warn("spread_jobs: Junk response: %s" % repr(y))
				die.info("spread_jobs: Junk remainder: %s" % self.p.stdout.readline())
				die.info("spread_jobs: Junk arglist: %s" % self.argstring())
				raise
		return None


	def close1(self):
		# die.info("Close stdin of subprocess")
		self.p.stdin.close()

	def close2(self):
		# die.info("Close stdout from subprocess")
		tmp = self.p.stdout.readlines()
		self.p.stdout.close()
		# die.info("Wait for subprocess")
		self.p.wait()
		return tmp


def delay_sanitize(x):
	return max(0.01, min(1000.0, float(x)))



class _ThreadJob(threading.Thread):

	def __init__(self, iqueue, oqueue, p, stdin, solock, wss):
		"""@param stdin: something to send at the start of the subprocess
			to get it going.   This is before the main processing starts.
		@type stdin: any iterable that yields something that can be
			given to L{cPickle.dumps}.
		@param p: The process to run.   It's already been started,
			but no input/output has occurred.
		@type p: L{Connection}
		@param solock: a lock to serialize the standard output
		@type solock: threading.Lock
		"""
		threading.Thread.__init__(self, name='spread_jobs%s' % id(self))
		self.iqueue = iqueue
		self.oqueue = oqueue
		self.wss = wss
		assert isinstance(p, Connection)
		self.p = p
		self.solock = solock
		try:
			for x in stdin:
				self.p.send(x)
		except self.p.SendError, x:
			die.info("I/O error in thread start-up: %s" % str(x))
			self.p.close1()


	def want_shutdown(self):
		# If it weren't for the fact that we use a maillist, and we start
		# with it filled, this could lead to premature termination of some
		# workers.
		#
		# Note that it is a mistake to shut down threads that aren't TooBusy.
		# If you're in a situation where some machines are heavily loaded and
		# never do any work, you will suffer severely if you accidentally shut
		# down the last thread that is actually doing any work.
		na, nlive = self.wss.num_active()
		return (na > 3+2*(len(self.iqueue)+1) and
			nlive*self.p.usefulness() < na
			)


	def compute_delay(self, qdelay, delta_t):
		"""The reason we have the dependence on nw and nq is that we want to
		shorten delays as the queue empties.   Basically, we don't want any
		processes sleeping when the queue is empty.   That would just waste
		time to no purpose.
	
		The reason we have the dependence on delta_t is that we want to limit
		the number of CPU cycles that are wasted in polling other machines to
		see if they are too busy.
		"""
		nw = self.wss.num_active()[0]
		nq = len(self.iqueue)
		delay = delay_sanitize(qdelay) * random.uniform(0.8, 1.4)
		delay1 = math.exp(1.0-self.p.usefulness())
		delay2 = max(0.1, float(nq+1)/float(nw))
		delay *= min(delay1, delay2)
		return math.sqrt(10*delta_t*delay) + delay

	
	def run(self):
		self.p.mystate("running")
		while True:
			# die.info("Waiting on iqueue")
			try:
				i, todo = self.iqueue.get()
			except MB.EOF:
				# die.info("Got EOF on iqueue")
				self.p.mystate("iqueue EOF")
				break
			t0 = time.time()
			try:
				self.p.send(todo)
			except self.p.SendError, x:
				die.warn("IO Error on send task %d to worker: %s" % (i, str(x)))
				self.iqueue.put((i, todo))
				self.p.mystate("SendError")
				break
			try:
				q, so, se = self.p.get()
			except (self.p.EOFError, CP.UnpicklingError, ValueError), x:
				die.warn("Exception %s when trying to read worker %s" % (x, self.p.argstring()))
				self.iqueue.put((i, todo))
				self.p.mystate("BadRead")
				break
			t2 = time.time()
			if isinstance(q, TooBusy):
				self.iqueue.put((i, todo))
				if self.want_shutdown():
					die.info("TooBusy: giving up on %s" % str(so))
					self.p.mystate("giving up")
					break
				else:
					tsleep = self.compute_delay(q.delay, t2-t0)
					die.info("TooBusy: sleeping %.3f for %s" % (tsleep, str(so)))
					self.p.I_am_working(0)
					time.sleep(tsleep)
				continue
			self.p.I_am_working(1)
			# die.info("Waiting on oqueue put")
			self.oqueue.put((i, t0, t2, q))
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
						j, todo = self.iqueue.get()
					except MB.EOF:
						self.p.mystate("RemoteException")
						break
					self.oqueue.put( (j, t0, t2, notComputed) )
		# die.info("Thread %s closing via %s" % (self, self.p))
		self.p.close1()
		# die.info("Thread %s closed" % self)

	def join(self, timeout=None):
		tmp = self.p.close2()
		threading.Thread.join(self, timeout=timeout)
		self.wss = None	# This breaks a loop of references.
		return tmp



_past_performance = PastPerformance()

def main(todo, list_of_args, connection_factory=Connection_subprocess,
		stdin=None, verbose=False, timing_callback=None, tail_callback=None,
		past_performance=_past_performance):
	"""Pass a bunch of work to other processes.
	@param stdin: a list of stuff to send to the other processes before the computation is
		properly commenced.
	@type stdin: list(whatever)
	@param todo: a sequence of tasks to do
	@type todo: sequence(whatever)
	@param list_of_args:
	@type list_of_args:  list(list(str))
	@param past_performance: a L{PastPerformance} object if you want the system to remember which
		machines were more/less successful last time and to start jobs on the more successful
		machines first.    L{None} if you don't want any memory.  The default is to have memory.
	@type past_performance: None or L{PastPerformance}.
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
	solock = threading.Lock()
	iqueue = MB.maillist(enumerate(todo))
	ntodo = len(iqueue)
	oqueue = MB.mailbox()
	ths = workers_c(connection_factory, list_of_args, iqueue, oqueue, stdin, solock,
				tail_callback=tail_callback, verbose=verbose,
				past_performance=past_performance
				)
	if verbose:
		die.info("%d jobs started" % len(ths))
	if not ths:
		raise RuntimeError, "No subprocesses started."

	oi = 0
	rv = [notComputed] * ntodo
	while oi < ntodo:
		try:
			i, ts, te, ans = oqueue.get()
		except MB.EOF:
			raise RuntimeError, "whoops"
		if timing_callback:
			timing_callback(ts, te)
		assert rv[i] is notComputed
		rv[i] = ans
		oi += 1
	# die.info("Closing iqueue and oqueue")
	iqueue.putclose()
	oqueue.putclose()
	if verbose:
		die.info("Joining %d jobs" % len(ths))
	ths.join()
	if past_performance is not None:
		ths.pass_performance(past_performance)
	return rv



class workers_c(object):
	"""This creates a group of worker threads that take tasks from the iqueue and put the
	answers on the oqueue.
	"""
	def __init__(self, connection_factory, list_of_args, iqueue, oqueue, stdin, solock,
			verbose=False, tail_callback=None, past_performance=None):

		self.tail_callback = tail_callback
		self.args = list_of_args
		self.ths = []
		self.verbose = verbose

		for args in sorted(list_of_args, key=past_performance):
			# There seems to be an issue with forking simultaneously
			# from many threads.   Since the file descriptors are
			# shared, various things get closed that should be left
			# open and vice versa.    See http://psf.upfronthosting.co.za/roundup/tracker/issue2320
			# and http://bugs.python.org/issue7213 .
			# So, we fork in the main thread and pass the process to the new thread.
			if self.verbose:
				die.info("Args= %s" % str(args))
			try:
				p = connection_factory(args)
			except p.OSError, x:
				die.warn("Cannot execute subprocess: %s on %s" % (x, args))
				continue
			t = _ThreadJob(iqueue, oqueue, p, stdin, solock, self)
			self.ths.append(t)
			t.start()

	def join(self):
		nj = len(self.ths)
		for t in self.ths:
			oo = t.join()
			if self.tail_callback:
				self.tail_callback(t.arglist, oo)
		if self.verbose:
			die.info("Joined %d jobs" % nj)

	def pass_performance(self, x):
		x.clear()
		for t in self.ths:
			x.add_many(t.p.performance())

	def __len__(self):
		return len(self.ths)
		# This doesn't count any workers that have terminated!
	

	def num_active(self):
		"""@return: total usefulness of all workers and the number of live workers
		@rtype: (float, int)
		"""
		na = 0.0
		nlive = 0
		# print 'act:', ','.join(['%.3f' % q.p.usefulness() for q in self.ths])
		for t in self.ths:
			tmp = t.p.usefulness()
			if tmp > 0.0:
				na += tmp
				nlive += 1
		return (na, nlive)



def test_worker(x):
	if x > 0 and random.random()<0.3:
		sys.exit(random.randrange(2))
	sys.stderr.write('test_worker starting\n')
	while True:
		sys.stderr.write('test_worker loop\n')
		try:
			txt = CP.load(sys.stdin)
		except EOFError:
			sys.stderr.write('test_worker got EOF\n')
			break
		if random.random() < 0.1:
			sys.stderr.write("Sending TooBusy")
			CP.dump((TooBusy(0.1), None, None), sys.stdout, CP.HIGHEST_PROTOCOL)
			sys.stdout.flush()
			continue
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


def test(script):
	for np in range(1, 5):
		print 'NP=%d' % np
		for i in range(1, 6):
			print 'ntasks=%d' % (i*5)
			x = ['a', 'b', 'c', 'd', 'e'] * i
			arglist = [ ['python', script, 'worker', str(j)] for j in range(np) ] 
			y = list(main(x, arglist, verbose=True))
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
	# assert isinstance(list_of_lists, list)
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
			for (i, t) in enumerate(tmp):
				if cpat.match(t):
					found = i
					break
			if found is not None:
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
	if len(sys.argv)==3 and sys.argv[1] == 'worker':
		test_worker(int(sys.argv[2]))
	else:
		test(sys.argv[0])
