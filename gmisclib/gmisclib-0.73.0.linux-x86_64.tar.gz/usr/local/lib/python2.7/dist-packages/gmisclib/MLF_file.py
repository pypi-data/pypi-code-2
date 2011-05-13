class BadFormatError(RuntimeError):
	def __init__(self, *s):
		RuntimeError.__init__(self, *s)


class NotInMLFFile(KeyError):
	def __init__(self, *s):
		KeyError.__init__(self, *s)


class block_MLF_file(object):
	"""This class reads in and stores a MLF file.  It does not interpret the interior data,
	but rather just breaks it up into blocks, each corresponding to an utterance.
	"""
	Quantum = 1e-7
	
	def __init__(self, fname, preprocessor=None):
		"""Read in a MLF file and store the information in C{self.block}.
		@param fname: Filename to read
		@type fname: str
		@param preprocessor: A function to project the name of each block onto
			something that you want to use as an index of blocks.
			Typically, this function cleans up the names, removing asterisks
			and such.
		@type preprocessor: function str -> str
		"""
		if preprocessor is None:
			preprocessor = lambda x:x

		#: self.block is where all the data is kept.  This is a dictionary
		#: mapping from a file pattern (name, roughly) to a block of label
		#: information.   The block is a list of strings, one per line in the MLF file.
		#: The file pattern is the output of C{preprocessor}.
		#: dict(str: list(str))
		self.block = {}

		self.fname = fname	#: The name of the MLF file
		self.blockname = {}	#: Mapping from a file pattern to the name of the block.
		block = []
		fd = open(fname, 'r')
		if fd.readline() != '#!MLF!#\n':
			raise BadFormatError
		inblock = False
		fpattern = None
		blockname = None
		for line in fd.readlines():
			line = line.rstrip()
			if not inblock:
				assert line[0]=='"' and line[-1]=='"'
				blockname = line[1:-1]
				fpattern = preprocessor(blockname)
				inblock = True
			elif inblock and line=='.':
				inblock = False
				self.block[fpattern] = block
				self.blockname[fpattern] = blockname
				block = []
			else:	# in the block
				block.append(line)


	def get(self, key):
		"""Get a block of text from a MLF file.
		"""
		try:
			return self.block[key]
		except KeyError:
			raise NotInMLFFile(key, self.fname)


	def get3(self, key, n=3):
		"""Get a block of time-aligned labels from a MLF file and interpret it.
		@return: C{(start, end, label, ...)} tuples, with C{start} and C{end} in seconds,
			C{label} is a string indicating a phoneme or word or whatever.
			If there is more information on a line, it will be passed along in the tuple.
		@rtype: list(tuple(start, end, label, ...), ...)
		"""
		labels = []
		for (i,line) in enumerate(self.get(key)):
			a = line.split()
			if len(a) >= 3:
				try:
					a[0] = float(a[0]) * self.Quantum
					a[1] = float(a[1]) * self.Quantum
				except ValueError:
					raise BadFormatError, "Cannot parse line %s : %s : %d" % (self.fname, key, i+1)
				if len(a) > 3:
					try:
						a[3] = float(a[3])
					except ValueError:
						raise BadFormatError, "Cannot parse line %s : %s : %d" % (self.fname, key, i+1)
			labels.append( tuple(a[:n]) )
		labels.sort()
		return labels
