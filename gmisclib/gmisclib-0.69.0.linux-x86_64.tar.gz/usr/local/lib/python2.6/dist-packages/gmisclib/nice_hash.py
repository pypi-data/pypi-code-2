
class DontHashThis(Exception):
	"""If your trimmer funcion raises this exception, then the input
			to nice_hash.add() will be ignored."""

	def __init__(self):
		Exception.__init__(self)


class NotInHash(KeyError):
	def __init__(self, s):
		KeyError.__init__(self, s)




class simple(object):
	__doc__ = """This class generates a map from inputs to integers,
		where an equivalence class is defined by the trimmer function.
		It is just a stripped-down version of the L{hash} class
		defined above.   Faster and less memory consumption, if
		you don't need the rmap method.
		"""



	def __init__(self, trimmer=None):
		"""
		@param trimmer: Defines equivalence classes on list;
			it can be some sort of projection operation.
			The default (None) makes the identity class equal to the inputs.
			It can also specify which inputs to ignore by raising the
			L{DontHashThis} exception.
		"""
		self.trimmed_seen = {}
		self.n = 0
		if trimmer is None:
			def trimmer(x):
				return x
		self.trimmer = trimmer


	def add(self, x):
		"""Returns an integer which is shared among all x in the
		equivalence class, but different from all other x.
		If the trimmer function raises the DontHashThis exception,
		it will ignore the input and return None.
		@returns: int
		"""

		try:
			xt = self.trimmer(x)
		except DontHashThis:
			return None

		try:
			i = self.trimmed_seen[xt]
		except KeyError:
			i = self.n
			self.trimmed_seen[xt] = i
			self.n += 1
		return i


	def add_newonly(self, x):
		"""Similar to add, except it returns None if the equivalence
		class has already appeared.
		@returns: int or None
		"""

		try:
			xt = self.trimmer(x)
		except DontHashThis:
			return None

		if xt in self.trimmed_seen:
			return None

		i = self.n
		self.trimmed_seen[xt] = i
		self.n += 1
		return i
		

	def get_image(self, x):
		"""Returns an integer which is shared among all x in the
		equivalence class, but different from all other x.
		"""

		try:
			xt = self.trimmer(x)
		except DontHashThis:
			raise NotInHash('Trimmer raised DontHashThis')
		try:
			i = self.trimmed_seen[xt]
		except KeyError:
			raise NotInHash('Key: %s' % str(xt))
		return i


	def map(self):
		"""Return the map from classes (as returned by the trimmer function)
		to integers."""
		return self.trimmed_seen.copy()


	def classes(self):
		"""Return a list over all the classes that have been seen."""
		return list(self.trimmed_seen.keys())


	def classmap(self):
		"""Return the map from integers to classes.
		@return: [classname, classsname, ...]
		"""
		o = [None] * len(self.trimmed_seen)
		for (x, i) in self.trimmed_seen.iteritems():
			o[i] = x
		return  o


class hash(simple):
	def __init__(self, trimmer=None):
		"""This adds the L{rmap} method to the L{simple} class.
		"""
		simple.__init__(self, trimmer)
		self.seen = []


	def rmap(self):
		"""Returns the map from integers to inputs."""
		# o = [ [] for i in range(len(self.trimmed_seen)) ]
		o = [ [] for q in self.trimmed_seen.keys() ]
		for (x, cl) in self.seen:
			o[self.trimmed_seen[cl]].append(x)
		return o


	def test(self):
		map = self.map()
		rmap = self.rmap()
		for (intg, inpt) in rmap.iteritems():
			for s in inpt:
				assert map[s] == intg

	def add(self, x):
		"""Returns an integer which is shared among all x in the
		equivalence class, but different from all other x.
		If the trimmer function raises the DontHashThis exception,
		it will ignore the input and return None.
		Note that if you add an item twice, it will appear twice in rmap().
		@returns: int
		"""

		try:
			xt = self.trimmer(x)
		except DontHashThis:
			return None
		self.seen.append((x, xt))

		try:
			i = self.trimmed_seen[xt]
		except KeyError:
			i = self.n
			self.trimmed_seen[xt] = i
			self.n += 1
		return i


	def add_newonly(self, x):
		"""Similar to add, except it returns None if the equivalence
		class has already appeared.

		The list of classes seen (self.seen) then
		contains only the first item that was added in each class,
		so L{rmap}() will produce a dictionary containing single-item lists:
		C{{int1:[item1],int2:[item2],int3:[item3], ...}}.
		Calls to L{add}() and L{add_newonly}() can be intermixed safely,
		though the result of L{rmap}() will then not contain all added items.
		@returns: int or None
		"""

		try:
			xt = self.trimmer(x)
		except DontHashThis:
			return None

		if xt in self.trimmed_seen:
			return None

		self.seen.append((x, xt))
		i = self.n
		self.trimmed_seen[xt] = i
		self.n += 1
		return i



nice_hash = hash


def map(list, trimmer=lambda x:x):
	h = simple(trimmer)
	for x in list:
		h.add(x)
	return h.map()



if __name__ == '__main___':
	h = nice_hash(lambda x : x)
	assert h.add('foo') == 0
	assert h.add('bar') == 1
	assert h.add('gleep') == 2
	assert h.add('bar') == 1
	h.test()
	assert h.map()['bar'] == 1
	assert h.rmap()[0] == ['foo']
	assert h.classmap()[1] == 'bar'
