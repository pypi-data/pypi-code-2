"""Fiatio reads and writes an extension of the
FIAT file format originally defined by David Wittman (UC Davis).
This reads and writes the FIAT 1.2 format, defined at U{http://kochanski.org/gpk/papers/2010/fiat.pdf}.
(FIAT 1.0 is defined at U{http://dls.physics.ucdavis.edu/fiat/fiat.html}.)

Nice FIAT features:
	- header information looks like a comment
	to most programs, so they will treat a FIAT file as
	simple multi-column ASCII.

	- since it has column names in the header, you can add
	columns at will, and your existing scripts will continue
	to run.

	- Simple to parse.

	- Easy to generate.


This describes fiat 1.2 format, which is nearly 100%
upwards compatible with fiat 1.0 format.
It is defined as follows:

	1. Lines are separated by newlines.

	2. All values are encoded by replacing newline and other difficult
	characters by a percent character (%) followed by a hex code
	on writing, and the reverse on reading.   (There are also
	some more human-friendly codes which can be used, instead
	of pure hex:
	see L{g_encode._specials} for their definitions.   Notably,
	C{%S} is space, C{%L} is newline, C{%R} is carriage return,
	C{%t} is tab, and C{%T} is percent.)

	3. At the top of the file, you have a line identifying the format: "# fiat 1.2"
	(regexp: C{"# fiat 1\.[0-9.]+"}).

	4. Then, you typically have a number of header lines beginning with "#".
	Header lines are in the form C{# attribute = value} (where
	white space is optional and can be a mixture of spaces and tabs).
	The attribute must match the regular expression C{[a-zA-Z_][a-zA-Z_0-9]*} .
	The value is whatever follows the equals sign, after leading and following
	white space is stripped.  If the value begins and ends with
	the same quote character, either C{'} or C{"}, the quotes are also stripped off.
	Values may contain any character except newline and the chosen quote.

		- Note that you must quote or encode a value if it begins or ends with whitespace.

		- Note also that header lines can also appear further down in the file;
			they are not restricted to the top.

		- Any other header lines are just treated as comments and ignored.

	6. There may be header lines of the form
	"# TTYPE1 = name" or "#ttype4 = name"
	which name the columns of the data (the leftmost column is TTYPE1).
	If you don't name the Ith column, its name will be C{I}.
	When writing, this module adds an attribute
	COL_SEPARATOR which contains the numeric code(s)
	(ASCII) of the column separator character(s).  This defaults to 9,
	ASCII tab.
	The module also adds a COL_EMPTY attribute with the string used to mark an
	blank (nonexistant) item.  (This defaults to C{%na}.)  Note that nonexistant
	is not the same as a zero-length string.

		- These lines may also appear anywhere in the file.   They take
			effect immediately.

		- All attributes and names are optional.

	7. Typically, the header is followed by multicolumn ASCII data.
	Columns are separated (by default) with any white space,
	but if there is a COL_SEPARATOR attribute, it is used instead.
	Empty entries for columns should be indicated by whatever code is specified
	in COL_EMPTY, if that is set.
	Otherwise, if COL_SEPARATOR is set, COL_SEPARATOR strings separate items,
	some of which may simply be empty.
	(In all cases, a completely blank line is treated as a datum which has all
	columns blank (nonexistant).)

If there is no DATE attribute, the write routine adds one, using the current date
and time, in the form ccyy-mm-ddThh:mm:ss (as defined in the NASA FITS format).
Note that all attributes are optional.

This is not quite David Wittman FIAT (1.0), which forces value to either be quoted
or to contain no white space. Dwittman FIAT will take a line
in the form "#a=b c", and interpret c as a comment, whereas
fiat 1.2 will interpret the value as "b c".
However, almost all files will be interpreted the same way as Fiat 1.0.

Here's an example::

	# fiat 1.2
	# TTYPE1 = b
	# TTYPE2 = a
	# SAMPRATE = 2.3
	# DATE = 2001-09-21T21:32:32
	# COL_EMPTY = "%na"
	# COL_SEPARATOR = "9"
	# Comment1
	# Comment2
	# b	a
	2	1
	3	2
	3	%na
	%na	3
	%na	%na
	0	1
"""


import re
import types
import string
import warnings

# from gmisclib:
import gpk_writer
import g_encode

TABLEN = 8

class FiatioWarning(UserWarning):
	def __init__(self, *s):
		UserWarning.__init__(self, *s)



def _alph(s):
	n = min(len(s), 8)
	o = 0.0
	f = 1.0
	# Not OK for unicode. Sigh.
	for i in range(n):
		f = f/256.0
		o += f * ord(s[i])
	return -o


# def col_order(a, b):
	# lc = cmp(len(str(a[0]))+a[1], len(str(b[0]))+b[1])
	# if lc != 0:
		# return lc
	# return cmp(str(a[0]), str(b[0]))

def col_order(a, b):
	sa = str(a)
	sb = str(b)
	lc = cmp(len(sa), len(sb))
	if lc != 0:
		return lc
	return cmp(sa, sb)


_autogen = re.compile("COL_SEPARATOR$", re.IGNORECASE)
_drop = re.compile("(__NAME_TO_COL|__COLUMNS)$")


def write_array(fd, adata, columns=None, comments=None, hdr=None, sep='\t', numeric=False):
	"""Write a rectangular array in FIAT format.
	Adata is a 2-D numpy array or a sequence of sequences.
	"""
	w = writer(fd, sep=sep)

	if columns is not None:
		w.add_cols(columns)
	if hdr is not None:
		w.headers(hdr)
	if comments is not None:
		for c in comments:
			w.comment(c)
	for i in range(len(adata)):
		w.datavec( adata[i], numeric=numeric )


_autogen = re.compile("TTYPE[0-9]+|COL_EMPTY|COL_SEPARATOR", re.IGNORECASE)

def write(fd, ldata, comments=None, hdr=None, sep='\t', blank='%na', fixed_order=0):
	"""Write a file in FIAT format.
			Ldata is a list of dictionaries.  Each dictionary
			corresponds to one line in the file.   Each
			unique key generates a column, and the values
			are printed in the data section of the FIAT file.
			Note that the TTYPE header lines will be automatically
			generated from ldata.
			Hdr is a dictionary of information that will be
			put in the header.
			Comments is a list of comment lines for the header.
			Fd is a file descriptor where the data should be
			written.
			Sep is a string used to separate data columns.
			Blank is a string to use when a data value is missing.
		"""
	w = writer(fd, sep=sep, blank=blank)
	if comments is not None:
		for com in comments:
			w.comment(com)
	if hdr is not None:
		w.headers(hdr)
	for d in ldata:
		w.datum(d)
	fd.flush()


class writer(gpk_writer.writer):
	"""Write a file in FIAT format.   This class represents an open file,
	and you call member functions to write data into the file.
	This automatically generates much of the header information.
	
	Column names are set from the keys passed in the C{datum()} method.
	Each unique key generates a column, and the values
	are printed in the data section of the FIAT file.
	The TTYPE header lines will also be automatically generated.
	"""

	def comment(self, comment):
		"""Add a comment to the data file.
		@param comment: the comment
		@type comment: str
		"""
		if '\n' in comment:
			raise ValueError, "No newline allowed in comments for fiatio."
		self.fd.write("# %s\n" % comment)


	def header(self, k, v):
		"""Add a single C{key=value} line to the header of the data file.
		@param k: key
		@param v: value
		@type k: str
		@type v: str
		"""
		if _autogen.match(k):
			warnings.warn("Hdr specifies information that is automatically generated: %s" % k, FiatioWarning)
		elif _drop.match(k):
			return
		self.__write_header(k, v)
	

	def __init__(self, fd, sep='\t', blank='%na'):
		"""@param fd: where to write the data
		@type fd: L{file}
		@param sep: what separates columns?
		@type sep: str
		@param blank: what marks a spot where there isn't data?
		@type blank: str
		"""
		gpk_writer.writer.__init__(self, fd)
		self.enc = _encoder(sep)
		self.blank = blank
		self.sep = sep
		self.map = {}
		self.columns = []
		fd.write("# fiat 1.2\n")
		fd.write("# I/O code: gmisclib.fiatio.py in speechresearch project on http://sourceforge.org\n")
		fd.write("# Format definition: http://kochanski.org/gpk/papers/2010/fiat.pdf\n")
		self.__write_header('COL_EMPTY', self.blank)
		self.__write_header('COL_SEPARATOR', 
		 		' '.join([str(ord(sc)) for sc in self.sep])
				)

	def add_cols(self, colnames):
		n = len(self.map)
		for c in colnames:
			self.map[c] = n
			self.columns.append( c )
			self.fd.write("# TTYPE%d = %s\n" % (n+1, c))
			n += 1
	
	def __hline(self, o):
		"""o is not used, except to help set the width of each field.
		"""
		ostart = 0
		hstart = 1	# The comment symbol.
		ls = len(self.sep)
		hline = []
		for (cn, val) in zip(self.columns, o):
			w = max(1, len(val) + (ostart - hstart)/2)
			ostart += len(val) + ls
			cn = str(cn)
			hstart += len(cn) + ls
			hline.append(cn.center(w))
		self.fd.write('#' + self.sep.join(hline) + '\n')


	def __write_header(self, k, v):
		v = '%s' % v
		if '\n' in v or v[0] in string.whitespace or v[-1] in string.whitespace:
			v = '|%s|' % self.enc.fwd(v)
		self.fd.write("# %s = %s\n" % (k, v))


	def datum(self, data_item):
		"""Write a line into a fiat file.   They column names will be set from
		the keys.
		@param data_item: a dictionary of C{key=value} pairs.
		@type data_item: C{dict(str: anything)}
		"""
		o = [ self.blank ] * len(self.map)
		# o = [ self.blank for q in self.map.keys() ]
		try:
			# This is the path for most calls.
			for (k, v) in data_item.iteritems():
				o[self.map[k]] = self.enc.fwd(str(v))
		except KeyError:
			# This is the path the first time, when self.map
			# doesn't yet exist.
			add = []
			for (k, v) in data_item.iteritems():
				if isinstance(k, types.StringType):
					pass
				elif isinstance(k, types.IntType) and k>=0:
					pass
				else:
					raise TypeError, ("Key is not a string or non-negative integer", k)
				if not k in self.map:
					# add.append( (k, len(str(v))) )
					add.append( k )
			add.sort(col_order)
			# self.add_cols([ t[0] for t in add ])
			self.add_cols( add )
			o = [ self.blank ] * len(self.map)
			# o = [ self.blank for q in self.map.keys() ]
			for (k, v) in data_item.iteritems():
				o[self.map[k]] = self.enc.fwd(str(v))
			self.__hline(o)
		self.fd.write(self.sep.join(o) + '\n')


	def datavec(self, vector, numeric=False):
		"""This assumes that you've already called add_cols() to set the
		column names.   It is an error to have a vector whose length doesn't
		match the number of column names.
		"""
		lv = len(vector)
		lc = len(self.columns)
		assert lv >= lc, "vector length=%d but %d columns" % (lv, lc)
		if lc < lv:
			self.add_cols( [ '%d' % q for q in range(lc, lv) ] )
		if numeric:
			self.fd.write( self.sep.join([str(q) for q in vector]) + '\n' )
		else:
			self.fd.write( self.sep.join([self.enc.fwd(str(q)) for q in vector]) + '\n' )


class merged_writer(writer):
	"""Assumes that the data will be read with read_merged(), so that
	header values will supply default values for each column.
	"""

	def __init__(self, fd, sep='\t', blank='%na'):
		writer.__init__(self, fd, sep, blank)
		self._hdr = {}
	
	def header(self, k, v):
		self._hdr[k] = v
		writer.header(self, k, v)

	def datum(self, data_item):
		"""Assumes that the data will be read with read_merged(), so that
		header values will supply default values for each column.
		This writes a line in the fiat file, but first it deletes any values
		that alread exist as a header item of the same name.
		"""
		tmp = {}
		for (k, v) in data_item.items():
			if k not in self._hdr or v!=self._hdr[k]:
				tmp[k] = v
		writer.datum(self, tmp)


def shared_data_values(data_items):
	"""Takes a list of data and pulls out all the items that have
	the same value in each line.    The idea is that you can then
	put them into the header via::

	hdr, data, c = read(fd)
	htmp, data = shared_data_values(data)
	hdr.update(htmp)

	@type data_items: C{list(dict(str: anything))}
	@return: It returns a tuple of (1) a dictionary of header items,
		and (2) a list of data.  The list has the same length as
		C{data_items}, but the dictionaries within it may have fewer entries.
	@rtype: C{tuple(dict(str:anything), list(dict(str:anything)))}
	"""
	data_items = list(data_items)
	values = None
	for datum in data_items:
		if values is None:
			values = datum.copy()
		for (k, v) in datum.items():
			if k in values and v!=values[k]:
				del values[k]
	assert values is not None
	outdata = []
	for datum in data_items:
		tmp = {}
		for (k, v) in datum.items():
			if k not in values:
				tmp[k] = v
			else:
				assert v == values[k]
		outdata.append(tmp)
	return (values, outdata)


BadFormatError = g_encode.BadFormatError
FiatError = BadFormatError


class ConflictingColumnSpecification(BadFormatError):
	def __init__(self, s):
		FiatError.__init__(self, s)



def _check_last_comment(comment, names):
	"""Check to see if the last comment is just a list of column names.
	This is what write() produces.   If so, it can be safely deleted.
	"""
	# print "SORTED NAMES=", sorted_names
	# print "LAST COMMENT", comment.split()
	return comment.split() == names



_encoder_cache = {}
def _encoder(sep):
	CACHELEN = 30
	if sep not in _encoder_cache:
		if len(_encoder_cache) > CACHELEN:
			_encoder_cache.pop()
		notallowed = '%#=\n\r'
		if sep is '':
			notallowed += ' \t\f\v'
		else:
			if sep in notallowed:
				raise ValueError, "Illegal separator: {%s}" % sep
			notallowed += sep
		_encoder_cache[sep] = g_encode.encoder(notallowed=notallowed)
	return _encoder_cache[sep]


class _rheader(object):
	"""This class is private.  It processes and accumulates header information
	as a FIAT file is read in.
	It represents the header information of a fiat file.
	"""

	LTTYPE = len('TTYPE')

	def __init__(self):
		self.sep = None
		self.blank = '%na'
		self.comments = []
		self.name_to_col = {}
		self.header = {}
		# self.header = {'__COLUMNS': {}, '__NAME_TO_COL': {}
				# }
		self.enc = _encoder('')
		self.icol = []
		self.colmap = {}

	def dequote(self, s):
		"""Remove quotes from a value."""
		ss = s.strip()
		if len(ss) < 2:
			return ss
		elif ss[0] in '\'"|' and ss[0]==ss[-1]:
			if ss[0] == '|':
				return self.enc.back(ss[1:-1])
			return ss[1:-1]
		return ss
	
	def parse(self, s):
		"""Parse a line of text and store the information.
		@type s: str
		"""
		l = s[1:].strip()
		a = l.split('=', 1)
		if len(a) > 1 and len(a[0].split()) == 1:
			attr = a[0].strip()
			val = self.dequote(a[1])
			if attr.upper().startswith('TTYPE'):
				ic = int(attr[self.LTTYPE:])-1
				if ic in self.colmap and self.colmap[ic]!=val:
					raise ConflictingColumnSpecification, 'column=%d: "%s" vs. "%s"' % (
										ic, val, self.icol[ic]
										)
				if val in self.name_to_col and self.name_to_col[val] != ic:
					raise ConflictingColumnSpecification, 'val="%s": columns %d vs. %d' % (
										val, ic, self.icol[ic]
										)
				self.extend_icol(ic+1)
				self.icol[ic] = val
				self.colmap[ic] = val
				self.name_to_col[val] = ic
			elif attr == 'COL_EMPTY':
				self.blank = val
			elif attr == 'COL_SEPARATOR':
				self.sep = ''.join( [chr(int(q)) for q in val.split() ] )
				self.enc = _encoder(self.sep)
			else:
				self.header[attr] = val
		elif not _check_last_comment(l, self.icol):
			self.comments.append(l)


	def extend_icol(self, la):
		if len(self.icol) < la:
			self.icol.extend( range(len(self.icol), la) )

	def dump(self, d):
		hdr = self.header
		com = self.comments
		self.header = {}
		self.comments = []
		return (hdr, d, com)

	def dumpx(self, d):
		"""Two special entries are added to header: __COLUMNS points to a mapping
		from column numbers (the order in which they appeared in the file,
		left to right, starting with 0) to names,
		and __NAME_TO_COL is the reverse mapping.
		"""
		hdr = self.header
		hdr['__NAME_TO_COL'] = self.name_to_col
		hdr['__COLUMNS'] = self.colmap
		com = self.comment
		self.header = {}
		self.comment = []
		return (hdr, d, com)


def read(fd):
	"""Read a fiat format data file.
	Each line in the FIAT file is represented by a dictionary that maps
	column name into the data (data is a string).
	Lines without data in a certain column will not have the corresponding
	entry in the dictionary for that line.

	You can use this function as follows::

		hdr, data, comments = read(fd)
		for datum in data:
			print datum['X']

	@return: Three items: header, data, and comments.
		Header is the collected dictionary of header information
		data is a list of dictionaries, one for each line in the file,
		and comments is a list of strings.
	@rtype: tuple(dict, list(dict(str:str)), list(str))
	@param fd: The data source: typically a file descriptor.
	@type fd: An iterator that generates strings.  Typically a L{file} object.
	"""
	out = []
	hdr = {}
	comments = []
	for (h, d, c) in readiter(fd):
		hdr.update(h)
		comments.extend(c)
		if d is not None:
			out.append(d)
	return (hdr, out, comments)


def read_merged(fd):
	"""Read in a fiat file and return a list of dictionaries,
	one for each line in the file.  (Also a list of comment lines.)
	Each line in the input FIAT file is represented by a dictionary that maps
	column name into the data (data is a string).
	The header data in the FIAT file is merged into the per-column data,
	so that the header data is used as a default value for the column of the same name.
	As a result, all the information in the file (both header and data) is in the
	resulting list of dictionaries.
	
	NB: this is a bit of a specialized routine.   Normally, one uses L{read}.
	
	E.g. if there is a header line "# X = Y" and
	no data column called "X", then this will succeed::
	
		data, comments = read_merged(fd):
		for datum in data:
			assert datum['X']=='Y'

	That this routine does not require header lines to precede data lines.
	If header lines appear in the middle, then a new column will be created from
	that point onwards.
	@return: (data, comments)
	@rtype: (list(dict), list(str))
	@param fd: The data source: typically a file descriptor.
	@type fd: An iterator that generates strings.  Typically a L{file} object.
	"""
	out = []
	comments = []
	hdr = {}
	for (h, d, c) in readiter(fd):
		comments.extend(c)
		if d is not None:
			hdr.update(h)
			tmp = hdr.copy()
			tmp.update(d)
			out.append(tmp)
	return (out, comments)



def readiter(fd):
	"""Read in a fiat file.
	Each line in the file is represented by a dictionary that maps
	column name into the data (data is a string).
	Lines without data in a certain column will not have an entry in that line's
	dictionary for that column name.

	Lines beginning with '#' are either header or comment lines.
	A fiat file can mix header lines amongst the data lines.   (Although, typically, all
	the header info is at the top.)

	You can use this function as follows::

		for (hdr, datum, comments) in readiter(fd):
			print datum['X']

	NB: this is a bit of a specialized routine.   Normally, one uses L{read}.

	@param fd: The data source: typically a L{file}.  Not a filename.
	@type fd: Anything that supports iteration. Typically a L{file} object.
	@return: Three items: header, data, and comments.
		Header is the collected dictionary of header information
		since the last iteration,
		data is a dictionary of the data on the current line,
		and comments is a list of comment string seen so far.
		The end of the file yields None for the last data,
		along with any header info or comments after the last datum.
	@rtype: (dict(str:str), dict(str:str), list(str))
	"""
	hobj = _rheader()
	i = 0
	for line in fd:
		if not line.endswith('\n'):	# Incomplete final line.
			if i == 0:
				raise BadFormatError, "Empty file"
			else:
				warnings.warn('fiatio.readiter(): ignoring line without newline.', FiatioWarning)
			break
		line = line.rstrip('\r\n')
		if not line:		# empty line
			yield hobj.dump({})
		elif line.startswith('#'):
			if i==0 and line.startswith('# fiat'):
				continue
			hobj.parse(line)
		else:
			a = line.split(hobj.sep)
			if len(hobj.icol) < len(a):
				hobj.extend_icol(len(a))
			tmp = {}
			for (ic, ai) in zip(hobj.icol, a):
				if ai != hobj.blank:
					tmp[ic] = hobj.enc.back(ai)
			yield hobj.dump(tmp)
		i += 1
	yield hobj.dump(None)



def read_as_float_array(fd, loose=False, baddata=None):
	"""Read in a fiat file. Return (header, data, comments),
	where header is a dictionary of header information,
	data is a numpy array, and comments is a list of strings.
	Two special entries are added to header: __COLUMNS points to a mapping
	from column numbers (the order in which they appeared in the file,
	left to right, starting with 0) to names, and
	_NAME_TO_COL holds the reverse mapping.

	Empty values are set to NaN.

	If loose==False, then all entries must be either floating point numbers
	or empty entries or equal to baddata (as a string, before conversion
	to a float).
	If loose==True, all non-floats will simply be masked out.
	"""
	import Num
	import fpconst

	if loose:
		def float_or_NaN(s):
			if s == baddata:
				tmpd = NaN
			else:
				try:
					tmpd = float(s)
				except ValueError:
					tmpd = NaN
			return tmpd
	else:
		def float_or_NaN(s):
			if s == baddata:
				tmpd = NaN
			else:
				tmpd = float(s)
			return tmpd



	NaN = fpconst.NaN
	hobj = _rheader()

	data = []
	maxcols = None
	for (i,line) in enumerate(fd):
		if i==0 and line.startswith('# fiat'):
			continue
		line = line.rstrip('\r\n')

		if line.startswith('#'):
			hobj.parse(line)
		else:
			a = line.split(hobj.sep)
			if len(hobj.icol) < len(a):
				hobj.extend_icol(len(a))
			tmpd = Num.array( [ float_or_NaN(q) for q in a ], Num.Float)
			data.append(tmpd)

	# Now, if the length has expanded between the beginning and the end,
	# go back and fill out the data with NaNs to a uniform length.
	if data and data[0].shape[0] < data[-1].shape[0]:
		NaNs = Num.zeros((maxcols,), Num.Float) + NaN
		assert not Num.sometrue(Num.equal(NaNs, NaNs))
	i = 0
	while i<len(data) and data[i].shape[0]<maxcols:
		data[i] = Num.concatenate((data[i], NaNs[:maxcols-data[i].shape[0]]))
		i += 1

	return (hobj.header, data, hobj.comments)



def _hcheck(a, b):
	# del a['__NAME_TO_COL']
	# del a['__COLUMNS']
	assert abs(float(a['SAMPRATE'])-float(b['SAMPRATE'])) < 1e-8
	del a['SAMPRATE']
	del b['SAMPRATE']
	assert a == b


def _dcheck(a, b):
	for (ax, bx) in zip(a, b):
		tmp = {}
		for (k, v) in bx.items():
			tmp[k] = str(v)
		assert ax == tmp


def test1():
	fd = open("/tmp/fakeZZZ.fiat", "w")
	data = [{'a':1, 'b':2},
			{'a':2, 'b':3},
			{'b':3},
			{'a':3},
			{},
			{'a':1, 'b':0}
		]
	comments = ['Comment1', 'Comment2']
	header = {'SAMPRATE': 2.3, 'DATE':'2001-09-21T21:32:32'}
	write(fd, data, comments, header)
	fd.flush()
	fd.close()
	fd = open("/tmp/fakeZZZ.fiat", "r")
	h, d, c = read(fd)
	_hcheck(h, header)
	_dcheck(d, data)
	assert c == comments


def test2():
	fd = open("/tmp/fakeZZZ.fiat", "w")
	data = [{}, {'a': 111},
			{'a':1, 'b':2},
			{'a':2, 'b':3},
			{'b':3},
			{'a':3},
			{},
			{'a':1, 'b':0}
		]
	comments = ['Comment1', 'Comment2']
	header = {'SAMPRATE': 2.3, 'DATE':'2001-09-21T21:32:32'}
	write(fd, data, comments, header)
	fd.flush()
	fd.close()
	fd = open("/tmp/fakeZZZ.fiat", "r")
	h, d, c = read(fd)
	_hcheck(h, header)
	_dcheck(d, data)
	assert c == comments



def test3():
	fd = open("/tmp/fakeZZ1.fiat", "w")
	comments = ['Comment1', 'Comment2']
	header = {'SAMPRATE': 2.3, 'DATE':'2001/09/21', 'nasty': '\033\032\011\rxebra'}
	data = [
		{'a':101, 'bljljlj':2, 'fd': 33341, 'q': 12},
		{'a':10, 'bljljlj':2, 'fd': 3334111, 'q': 12},
		{'a':10, 'bljljlj':21, 'fd': 3331, 'q': 12},
		{'a':1, 'bljljlj':4, 'fd': 3334122, 'q': 12},
		{'a':1, 'bljljlj':3, 'fd': 333, 'q': 12}
		]
	write(fd, data, comments, header,
		blank = 'NA'
		)
	fd.flush()
	fd.close()
	fd = open("/tmp/fakeZZ1.fiat", "r")
	h, d, c = read(fd)
	_hcheck(h, header)
	_dcheck(d, data)
	assert c == comments


def test4():
	import Num
	fd = open("/tmp/fakeZZ1.fiat", "w")
	adata = Num.zeros((4,7), Num.Float)
	for i in range(adata.shape[0]):
		for j in range(adata.shape[1]):
			adata[i,j] = i**2 + 2*j**2 - 0.413*i*j - 0.112*float(i+1)/float(j+2)
	comments = ['C1']
	hdr = {'foo': 'bar', 'gleep':' nasty\n value\t'}
	columns = ['A', 'b', 'C', 'd']
	write_array(fd, adata, columns=columns,
			comments=comments, hdr=hdr, sep='\t')
	fd = open("/tmp/fakeZZ1.fiat", "r")
	h, adtest, c = read_as_float_array(fd, loose=False, baddata=None)
	assert c == comments
	for (k,v) in hdr.items():
		assert h[k] == v
	# for (i,cname) in enumerate(columns):
		# assert h['__COLUMNS'][i] == cname
		# assert h['__NAME_TO_COL'][cname] == i
	if Num.sum(Num.absolute(adtest-adata)) > 0.001:
		raise AssertionError('Bad array recovery')

def test():
	test1()
	test2()
	test3()
	test4()

if __name__ == '__main__':
	test()

