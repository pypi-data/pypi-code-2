"""These are I/O routines to allow you to write stuff
like arrays and dictionaries (and arrays of dictionaries)
to a human-readable file.

The format is normally STARTMARKER LENGTH_INFO DATA ENDMARKER,
where STARTMARKER is something like C{"a{"},
that specifies you're at the beginning of an array.
LENGTH_INFO can depend on the data type, but it's normally
an integer.   Then comes the data, and finally as a check,
you encounter the ENDMARKER, which is normally C{"}"}.
All of this is recursive, of course.
"""

import string
import collections
import numpy

import g_encode

_e = g_encode.encoder(allowed=string.letters + string.digits + r"""<>?,./:";'{}[\]!@$^&*()_+=\|\\-""")
__version__ = "$Revision: 1.24 $"

def test_e():
	assert _e.fwd(' ') == '%S'
	assert _e.fwd('hello there') == 'hello%Sthere'
	assert not _e.fwd('#x').startswith('#')


class BadFileFormat(RuntimeError):
	def __init__(self, s):
		RuntimeError.__init__(self, s)

class chunk:
	__doc__ = """Low level file I/O operations.
		This class represents a sequence
		of white-space separated chunks of data.
		"""

	def __init__(self):
		"""Constructor."""
		pass


	def more(self):
		"""Returns zero if the data source is empty.
		Returns nonzero if there is more data.
		"""
		raise RuntimeError, 'Virtual Function'


	def readchunk(self):
		"""Read in the next white-space delimited chunk of text."""
		raise RuntimeError, 'Virtual Function'


	def read_float(self):
		tmp = self.readchunk()
		if tmp != 'f:':
			raise BadFileFormat, 'read_float: bad prefix'
		return float(self.readchunk())


	def read_array(self, fcn):
		"""Read an array of data values.  Raw text is converted to
		finished array values by the specified fcn."""
		
		return self.read_array_of( lambda s: fcn(s.readchunk()) )

	def read_tuple(self, fcn):
		"""Read a tuple of data values.  Raw text is converted to
		finished array values by the specified fcn."""
		
		return tuple( self.read_array_of( lambda s: fcn(s.readchunk()) ) )


	_array_prefix = 'a{'
	_lap = len(_array_prefix)

	def read_array_of(self, fcn):
		"""Read an array of data values.  Values are read
		in by the specified fcn."""
		
		tmp = self.readchunk()
		if tmp is None:
			return None
		if not tmp.startswith(self._array_prefix):
			raise BadFileFormat, 'Array initial'
		if len(tmp) > self._lap:
			n = int(tmp[self._lap:])
		else:
			n = int(self.readchunk())
		o = [ fcn(self) for i in range(n) ]
		if self.readchunk() != '}':
			raise BadFileFormat, 'Array final'
		return o


	def read_dict(self, fcn):
		"""Read a dictionary of data values.  Raw text is converted to
		finished values by the specified fcn. Keys are strings."""

		return self.read_dict_of( lambda self, ff=fcn: ff(self.readchunk()) )

	_dict_prefix = 'd{'
	_ldp = len(_dict_prefix)

	def read_dict_of(self, fcn):
		"""Read a dictionary of data values.
		Values are read in by the specified fcn.
		This allows dictionaries of X, where X can be a complex datatype
		like an array.  Keys are strings."""

		tmp = self.readchunk()
		if tmp is None:
			return None
		if not tmp.startswith('d{'):
			raise BadFileFormat, 'Dict initial'
		if len(tmp) > self._ldp:
			n = int(tmp[self._ldp:])
		else:
			n = int(self.readchunk())

		o = {}
		for i in range(n):
			k = self.readchunk()
			v = fcn(self)
			o[k] = v
		if self.readchunk() != '}':
			raise BadFileFormat, 'Dict final'
		return o


	def groupstart(self):
		tmp = self.readchunk()
		if not tmp.startswith('g{'):
			raise BadFileFormat, 'Group initial: "%s"' % tmp
		return self.readchunk()


	def groupend(self):
		if self.readchunk() != '}':
			raise BadFileFormat, 'Group final'


	def read_NumArray(self):
		tmp = self.readchunk()
		if tmp != 'N{':
			raise BadFileFormat, 'NumArray initial: "%s"' % tmp
		sz = tuple(self.read_array(int))
		n = 1
		for s in sz:
			assert s > 0  and  s < 100000
			n *= s
		try:
                	if len(sz) == 2:
				d = numpy.zeros(sz)
                        	for i in range(sz[0]):
                                	for j in range(sz[1]):
						d[i, j] = float(self.readchunk())
                	else:
				d = numpy.zeros((n,))
                        	for i in range(n):
					d[i] = float(self.readchunk())
				d = numpy.reshape(d, sz)
		except ValueError, x:
			if str(x).startswith('invalid literal for float'):
				raise BadFileFormat, 'Expected floats, got something else: %s' % str(x)
		assert d.shape == sz
		if self.readchunk() != '}':
			raise BadFileFormat, 'NumArray final'
		return d


class datachunk(chunk):
	__doc__ = """Low level file I/O operations.
		This class represents a file as a sequence
		of white-space separated chunks of data.
		"""

	def __init__(self, fd):
		"""Constructor."""
		chunk.__init__(self)
		# self.readiter = gpkmisc.threaded_readable_file(fd)
		self.readiter = fd
		self.next = collections.deque( self._get_next() )


	def _get_next(self):
		while True:
			nxt = self.readiter.readline()
			if nxt == '':
				return []
			if nxt.startswith('#'):
				continue
			nxt = nxt.strip()
			if nxt == '':
				continue
			return nxt.split()


	def more(self):
		"""Returns False if the data source is empty.
		@return: True if there is more data.
		"""
		if len(self.next):
			return True
		self.next.extend( self._get_next() )
		return len(self.next) > 0


	def readchunk(self):
		"""Read in the next white-space delimited chunk of text."""
		try:
			return _e.back( self.next.popleft() )
		except IndexError:
			self.next.extend( self._get_next() )
			if len(self.next) == 0:
				return None
		return _e.back( self.next.popleft() )


class stringchunk(chunk):
	__doc__ = """Low level operations: splitting a string into chunks.
		This class represents a string as a sequence
		of white-space separated chunks of data.
		"""

	def __init__(self, s):
		"""Constructor."""
		chunk.__init__(self)
		self.cache = s.split()
		self.i = 0


	def more(self):
		"""@return: zero if the data source is empty; nonzero if there is more data.
		"""
		return self.i < len(self.cache)-1


	def readchunk(self):
		"""Read in the next white-space delimited chunk of text."""
		try:
			tmp = _e.back(self.cache[self.i])
			self.i += 1
			return tmp
		except IndexError:
			return None



class chunk_w:
	def __init__(self):
		pass


	def _indent(self):
		pass


	def _dedent(self):
		pass


	def writechunk(self, ch, b=0):
		self.stringwrite(ch, b)
		return self


	def write(self, ch, b=0):
		raise RuntimeError, "Virtual function"


	def nl(self):
		raise RuntimeError, "Virtual function"


	def comment(self, comment):
		raise RuntimeError, "Virtual function"


	def close(self):
		raise RuntimeError, "Virtual function"


	def write_None(self):
		self.stringwrite("N")
		return self


	def write_array_of(self, data, writer, b=0):
		self.stringwrite("a{%d" % len(data), b)
		self._indent()
		for t in data:
			writer(self, t)
		self._dedent()
		self.stringwrite("}", b)
		return self


	def write_array(self, data, b=0, converter=str):
		return self.write_array_of(data,
				lambda s, x, cvt=converter: s.stringwrite(cvt(x)),
				b)


	def write_dict_of(self, data, writer, b=1):
		self.stringwrite("d{%d" % len(data), b)
		self._indent()
		for (k, v) in data.items():
			self.stringwrite(k)
			writer(self, v)
		self._dedent()
		self.stringwrite("}", b)
		return self


	def write_dict(self, data, b=0, converter=str):
		return self.write_dict_of(data,
				lambda s, v, c=converter: s.stringwrite(c(v)),
				b)
	

	def groupstart(self, contents, b=1, comment=None):
		"""The 'contents' argument is conventionally a string
		containing 'a' for an internal array, 'g' for a group,
		'd' for a dictionary...  It describes the contents of the group.
		This is just used by the application to check what is in the
		group, so it could contain any chunk.
		"""
		self.stringwrite("g{", b)
		self._indent()
		self.stringwrite(contents)
		if comment:
			self.comment(comment)
		return self


	def groupend(self, b=1):
		self.stringwrite("}", b)
		self._dedent()
		return self


        def write_NumArray(self, d, b=0, converter=str):
                self.stringwrite("N{", b)
                self.write_array(d.shape, b=0)
                if len(d.shape) == 2:
                        for i in range(d.shape[0]):
                                for j in range(d.shape[1]):
                                        self.stringwrite( converter(d[i, j]) )
				if d.shape[0] > 1:
                                	self.nl()
                else:
                        for t in numpy.ravel(d):
                                self.stringwrite( converter(t) )
                self.stringwrite("}", 0)
		return self
                                                                                            
	def write_float(self, d, b=0):
		self.stringwrite("f:", b)
		self.stringwrite(str(d), b=0)
		return self

	def stringwrite(self, ch, b=0):
		raise RuntimeError, 'Virtual Function'




class datachunk_w(chunk_w):
	__doc__ = """This writes stuff to a file."""


	def __init__(self, fd, width=80):
		chunk_w.__init__(self)
		self.fd = fd
		self.w = width
		self.i = 0
		self.indentlevel = 0
		self.dentstring = ' '


	def _indent(self):
		self.indentlevel += 1


	def _dedent(self):
		assert self.indentlevel > 0
		self.indentlevel -= 1


	def stringwrite(self, ch, b=0):
		"""ch is the chunk of text.  b=1 to begin a new line."""
		assert isinstance(ch, str), "Non-string to stringwrite: <%s>" % str(ch)
		n = len(ch)
		if self.i == 0:
			pass
		elif b or (self.i > 0  and  n+self.i > self.w):
			self.nl()
		else:
			self.fd.write(' ')
			self.i += 1
		if self.i == 0:
			self.fd.write(self.dentstring * self.indentlevel)
		tmp = _e.fwd(ch)
		self.fd.write(tmp)
		self.i += len(tmp)


	def nl(self):
		self.fd.write('\n')
		self.i = 0


	def comment(self, comment):
		if self.i > 0:
			self.nl()
		idl = max(0, self.indentlevel-1)
		self.fd.write('#' + self.dentstring * idl + comment + '\n')


	def close(self):
		if self.i > 0:
			self.nl()
		self.fd.flush()
		# os.fsync(self.fd.fileno())
		self.fd = None	# This will normally close the fd,
				# unless it is held open by some other
				# use.


	def __del__(self):
		if self.fd is not None:
			self.close()




class chunkstring_w(chunk_w):
	__doc__ = """This accumulates stuff in memory, and returns a string
		when close() is called."""

	def __init__(self):
		chunk_w.__init__(self)
		self.buf = []


	def stringwrite(self, ch, b=0):
		self.buf.append(_e.fwd(ch))


	def nl(self):
		pass


	def comment(self, comment):
		pass


	def close(self):
		o = ' '.join(self.buf)
		self.buf = []
		return o



def test():
# print chunkstring_w().write_array([1.3, 2.2], str).close()
	assert stringchunk(chunkstring_w().writechunk('Hoo!#\n').close()).readchunk() == 'Hoo!#\n'
	tmp = numpy.array([[1.0, -1.0], [1.6, 0.0], [2.0, 3.0]], numpy.float)
	tmp1 = chunkstring_w().write_NumArray(tmp).close()
	retmp = stringchunk(tmp1).read_NumArray()
	assert retmp.shape == tmp.shape
	diff = retmp - tmp
	assert numpy.absolute(numpy.ravel(diff)).sum() < 1e-6


if __name__ == '__main__':
	test_e()
	test()
