"""A multithreaded version of os.popen2().  Note that the argument list
isn't quite the same."""


import os




class pfd(object):
	__doc__ = """Pseudo-file descriptor.  Just like a FD, except
		that it waits for the process at the end of the pipe
		to terminate when you close it.
		"""

	def __init__(self, fd, cpid):
		self.fd = os.fdopen(fd, "r")
		self.cpid = cpid
		self.mode = "r"
		self.waitval = None
		self.closed = False

		self.readline = self.fd.readline
		self.next = self.fd.next
		self.flush = self.fd.flush
		self.__iter__ = self.fd.__iter__
		self.read = self.fd.read
		self.readlines = self.fd.readlines
		self.fileno = self.fd.fileno

	# def read ... copied from file.read
	def read(self):
		return self.fd.read()

	# def readline ... copied from file.readline
	def readline(self):
		return self.fd.readline()

	# def readlines ... copied from file.readlines
	def readlines(self):
		return self.fd.readlines()

	# def next ... copied from file.next
	def next(self):
		return self.fd.next()

	# def __iter__ ... copied from file.__iter__

	def __iter__(self):
		return self.fd.__iter__()

	# def flush ... copied from file.flush
	def flush():
		return

	# def fileno ... copied from file.fileno


	def xreadlines(self, sizehint=-1):
		return self.fd.xreadlines(sizehint)


	def close(self):
		if not self.closed:
			self.fd.close()
			self.closed = True
			pid, t2 = os.waitpid(self.cpid, 0)
			if t2 == 0:
				self.waitval = None
			else:
				self.waitval = t2
		return self.waitval


	def __del__(self):
		self.close()


def popen2(path, args):
	"""Forks off a process, and returns the processes
	input and output file descriptors.  The latter is really
	a pfd (defined above).

	Path and args are passed directly into os.execvp().
	"""

	rci, wci = os.pipe()
	rco, wco = os.pipe()

	cpid = os.fork()
	if cpid == 0:
		# child
		os.close(rco)
		os.close(wci)
		os.dup2(rci, 0)
		os.dup2(wco, 1)
		os.execvp(path, args)
		os._exit(127)

	os.close(rci)
	os.close(wco)
	return (os.fdopen(wci, "w"), pfd(rco, cpid))


def test():
	si, so = popen2("sed", ["sed", "-e", "s/or/er/"])
	si.write("hello, world!\nsecond line\n")
	si.close()
	assert so.readline() == "hello, werld!\n"
	a = so.readlines()
	assert len(a) == 1
	assert a[0] == "second line\n"
	tmp = so.close()
	assert tmp is None

if __name__ == '__main__':
	test()
	test()
