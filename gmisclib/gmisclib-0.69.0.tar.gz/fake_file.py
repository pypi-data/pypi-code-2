"""A class that implements a simple file in memory.
It's not an exact simulation of a real file:
it assumes that no seeking is done, and that
all reads are line-at-a-time.
It also (intentionally) allow reading from files opend
in mode 'r', and allows writing for files opened in mode
'w'."""

import types

__version__ = "$Revision: 1.4 $"

import StringIO

class file(StringIO.StringIO):
	def __init__(self, mode='rw', name=None):
		StringIO.StringIO.__init__(self)
		self.name = name


def open(name, mode):
	return file(name, mode)



if __name__ == '__main__':
	x = file("foo", "rw")
	x.write("Hello\n")
	x.write("foo\n")
	x.seek(0, 0)
	assert x.readline() == "Hello\n"
	assert x.readline() == "foo\n"
	assert x.readline() == ''
	assert x.readlines() == []

	x = file("foo", "rw")
	x.write("Hello\n")
	x.write("foo\n")
	x.seek(0, 0)
	assert x.readlines() == [ 'Hello\n', 'foo\n' ]
