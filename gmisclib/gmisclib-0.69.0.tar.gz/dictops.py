"""Operations on dictionaries."""


__version__ = "$Revision: 1.9 $"

def filter(d, l):
	"""Passes through items listed in l.
	@param l: list of keys to preserve
	@type l: list
	@param d: dictionary to copy/modify.
	@type d: mapping
	@return: a dictionary where all keys not listed in l are removed;
		all entries listed in l are copied into the (new)
		output dictionary.
	@rtype: dict
	"""
	# o = {}
	# for t in l:
		# o[t] = d[t]
	# return o
	return dict( [ (t, d[t]) for t in l ] )


def remove(d, l):
	"""Removes items listed in l.
	@param l: list of keys to remove
	@type l: list
	@param d: dictionary to copy/modify.
	@type d: mapping
	@return: a dictionary where all keys listed in l are removed;
		all entries not listed in l are copied into the (new)
		output dictionary.
	@rtype: dict
	"""
	o = d.copy()
	for t in l:
		if o.has_key(t):
			del o[t]
	return o



def rev1to1(d):
	"""Reverse a 1-1 mapping so it maps values to keys
	instead of keys to values.
	@type d: dict
	@rtype: dict
	@return: M such that if m[k]=v, M[v]=k
	@except ValueError: if the mapping is many-to-one.
	"""
	o = {}
	for (k, v) in d.items():
		if v in o:
			raise ValueError, 'Dictionary is not 1 to 1 mapping'
		o[v] = k
	return o


def compose(d2, d1):
	"""Compose two mappings (dictionaries) into one.
	@return: C{d} such that d[k] = d2[d1[k]]
	@rtype: L{dict}
	@param d2: second mapping
	@param d1: first mapping
	"""
	o = {}
	for (k, v) in d1.items():
		try:
			o[k] = d2[d1[k]]
		except KeyError:
			pass
	return o


class BadFileFormatError(Exception):
	"""This indicates a problem when reading in a dictionary via L{read2c}.
	"""

	def __init__(self, *s):
		Exception.__init__(self, *s)


def read2c(f):
	"""Read in a dictionary from a two-column file;
	columns are separated by whitespace.
	This is not a completely general format, because keys cannot contain
	whitespace and the values cannot start or end in whitespace.

	The format can contain comments at the top; these are
	lines that begin with a hash mark (#).  Empty lines are
	ignored.
	@param f: an open L{file}
	@return: a dictionary and a list of comments
	@rtype: tuple(dict(str:str), list(str))
	@note: You can get into trouble if you have a key that starts with
		a hash mark (#).  If it happens to be the first key,
		and if there are no comments or if it directly follows a
		comment, it will be interpreted as a comment.
		To avoid this possibility, begin your file with a comment
		line, then a blank line.
	"""
	o = {}
	comments = []
	in_hdr = True
	n = 0
	for l in f:
		n += 1
		if in_hdr:
			if l.startswith('#'):
				comments.append(l[1:].strip())
				continue
			in_hdr = False
			if l == '\n':
				continue
		if not l.endswith('\n'):
			raise BadFileFormatError("Last line is incomplete: %s" % getattr(f, "name", "???"))
		try:
			k, v = l.strip().split(None, 1)
		except ValueError:
			raise BadFileFormatError("File %s line %d: too few columns" %
							(getattr(f, "name", "???"), n)
							)
		if k in o:
			raise BadFileFormatError("File contains duplicate keys: %s on line %d and earlier" %
							(repr(k), n)
							)
		o[k] = v
	return o, comments


def argmax(d):
	"""For a dictionary of key=value pairs, return the key with the largest value.
	@note: When there are several equal values, this will return a single, arbitrary choice.
	@except ValueError: when the input dictionary is empty.
	"""
	kmax = None
	vmax = None
	firstpass = True
	for (k, v) in d.items():
		if firstpass or v>vmax:
			vmax = v
			firstpass = False
			kmax = k
	if firstpass:
		raise ValueError, "argmax is not defined for an empty dictionary"
	return kmax


def add_dol(dict, key, value):
	"""OBSOLETE: replace with class L{dict_of_lists}.
	Add an entry to a dictionary of lists.
	A new list is created if necessary; else the value is
	appended to an existing list.
	Obsolete: replace with dict_of_lists.
	"""
	try:
		dict[key].append(value)
	except KeyError:
		dict[key] = [ value ]


def add_doc(dict, key, value):
	"""OBSOLETE: replace with class L{dict_of_accums}.
	Add an entry to a dictionary of counters.
	A new counter is created if necessary; else the value is
	added to an existing counter.
	Obsolete: replace with dict_of_accums.
	"""
	try:
		dict[key] += value
	except KeyError:
		dict[key] = value


class dict_of_lists(dict):
	"""A dictionary of lists."""

	def add(self, key, value):
		"""Append value to the list indexed by key."""
		try:
			self[key].append(value)
		except KeyError:
			self[key] = [ value ]

	def addgroup(self, key, values):
		"""Append values to the list indexed by key."""
		try:
			self[key].extend(values)
		except KeyError:
			self[key] = values

	def add_ifdifferent(self, key, value):
		"""Append value to the list indexed by key."""
		try:
			v = self[key]
		except KeyError:
			self[key] = [value]
		else:
			if value not in v:
				v.append( value )

	def copy(self):
		"""This does a shallow copy."""
		return dict_of_lists(self)


	def merge(self, other):
		for (k, v) in other:
			self.addgroup(k, v)


class dict_of_sets(dict):
	"""A dictionary of lists."""
	def add(self, key, value):
		"""Append value to the set indexed by key."""
		try:
			self[key].add(value)
		except KeyError:
			self[key] = set([value])

	def addgroup(self, key, values):
		"""Append values to the list indexed by key."""
		try:
			self[key].update(values)
		except KeyError:
			self[key] = set(values)


	def copy(self):
		"""This does a shallow copy."""
		return dict_of_sets(self)


	def merge(self, other):
		for (k, v) in other:
			self.addgroup(k, v)


class dict_of_accums(dict):
	"""A dictionary of accumulators.
	Note that the copy() function produces a dict_of_accums."""

	def add(self, key, value):
		"""Add value to the value indexed by key."""
		try:
			self[key] += value
		except KeyError:
			self[key] = value


	def copy(self):
		return dict_of_accums(self)


	def merge(self, other):
		for (k, v) in other:
			self.add(k, v)


class dict_of_averages(dict):
	"""A dictionary of accumulators.
	Note that the copy() function produces a dict_of_averages."""

	def add(self, key, value, weight=1.0):
		"""Add value to the value indexed by key."""
		assert weight >= 0.0
		if key in self:
			self[key] += complex(value*weight, weight)
		else:
			self[key] = complex(value*weight, weight)

	def get_avg(self, key):
		vw = self[key]
		assert vw.imag > 0.0, "Weight for key=%s is nonpositive(%g)" % (key, vw.imag)
		return vw.real/vw.imag

	def get_avgs(self):
		o = {}
		for (k, vw) in self.items():
			assert vw.imag > 0.0, "Weight for key=%s is nonpositive(%g)" % (k, vw.imag)
			o[k] = vw.real/vw.imag
		return o

	def get_both(self, key):
		vw = self[key]
		return (vw.real, vw.imag)

	def copy(self):
		return dict_of_averages(self)


	def merge(self, other):
		for (k, v) in other:
			self.add(k, v)


class dict_of_maxes(dict):
	"""A dictionary of maxima.   Add a new number and the stored
	maximum will increase iff the new value is bigger.
	Note that the copy() function produces a dict_of_accums."""

	def add(self, key, value):
		"""Add value to the value indexed by key."""
		try:
			tmp = self[key]
			if value > tmp:
				self[key] = value
		except KeyError:
			self[key] = value


	def copy(self):
		return dict_of_maxes(self)


	def merge(self, other):
		for (k, v) in other:
			self.add(k, v)



class dict_of_X(dict):
	"""A dictionary of arbitrary things.
	Note that the copy() function produces a dict_of_X.
	"""

	def __init__(self, constructor, incrementer):
		self.constructor = constructor
		self.incrementer = incrementer

	def add(self, key, *value):
		"""Add value to the thing indexed by key."""
		try:
			self.incrementer(self[key], *value)
		except KeyError:
			self[key] = self.constructor(*value)


class list_of_dicts(list):
	def __init__(self, *arg):
		list.__init__(self, arg)
	
	def lookup1(self, key, value):
		for d in self:
			try:
				if d[key]==value:
					return d
			except KeyError:
				pass
