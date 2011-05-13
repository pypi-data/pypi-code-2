"""A multithreaded version of os.popen2().  Note that the argument list
isn't quite the same."""


import subprocess as S




class pfd(object):
	__doc__ = """Pseudo-file descriptor.  Just like a FD, except
		that it waits for the process at the end of the pipe
		to terminate when you close it.
		"""

	def __init__(self, p):
		self.fd = p.stdout
		assert p is not None
		self.p = p
		self.mode = "r"
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
	def flush(self):
		return

	# def fileno ... copied from file.fileno


	def xreadlines(self, sizehint=-1):
		return self.fd.xreadlines(sizehint)


	def close(self):
		if not self.closed:
			self.fd.close()
			self.closed = True
			self.p.wait()
		return self.p.returncode


	def __del__(self):
		self.close()


def popen2(path, args, bufsize=0):
	"""Forks off a process, and returns the processes
	input and output file descriptors.  The latter is really
	a pfd (defined above).

	Path and args are passed directly into os.execvp().
	"""

	p = S.Popen(args, executable=path,
			stdin=S.PIPE, stdout=S.PIPE, close_fds=True)
	return (p.stdin, pfd(p))


def test():
	si, so = popen2("sed", ["sed", "-e", "s/or/er/"])
	si.write("hello, world!\nsecond line\n")
	si.close()
	assert so.readline() == "hello, werld!\n"
	a = so.readlines()
	assert len(a) == 1
	assert a[0] == "second line\n"
	tmp = so.close()
	assert tmp is None, "tmp=%s" % tmp

if __name__ == '__main__':
	test()
	test()
