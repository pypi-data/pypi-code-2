"""Defines array_window class."""

__version__ = "$Revision: 1.4 $"

class array_window:
	__doc__ = """Lets you reference 1-d array items relative to an arbitrary zero."""

	def __init__(self, array, zero):
		assert array is not None
		assert len(array) > 0
		assert zero >= 0 and zero < len(array)
		self.d = array
		self.zero = zero

	def __setattr__(self, name, value):
		if self.__dict__.has_key(name):
			raise AttributeError, "Can't re-set " + name
		if name == 'd' or name == 'zero':
			self.__dict__[name] = value
		else:
			raise AttributeError, "Can't set any attributes"

	def __delattr__(self, name):
		raise(AttributeError)

	def __getitem__(self, index):
		i = self.zero + index
		if i < 0:
			raise IndexError, 'negative index'
		return self.d[i]

	def __setitem__(self, index, value):
		index += self.zero
		if index < 0:
			raise IndexError, 'negative index'
		self.d[index] = value

	def __getslice__(self, i, j):
		i += self.zero
		j += self.zero
		if i < 0:
			i = 0
		if j < 0:
			j = 0
		return self.d[i, j]

	def __setslice__(self, i, j, sequence):
		i += self.zero
		j += self.zero
		if i < 0:
			i = 0
		if j < 0:
			j = 0
		self.d[i:j] = sequence

	def __str__(self):
		if self.zero <= 0:
			s = "*" + (-self.zero)*"." + str(self.d)
		elif self.zero > len(self.d):
			s = str(self.d) + (self.zero-len(self.d))*"." + "*"
		else:
			s = str(self.d[:self.zero]) + "*" + str(self.d[self.zero:])
		return "<array_window at %d of %d:" % (self.zero, len(self.d)) + s + ">"

	def __repr__(self):
		return self.__str__()

	def __len__(self):
		"""Of course, one can't assume that one can say x[i] for i in range(len(x))."""
		return len(self.d)


def test():
	x = [0, 2, 3, 4, 5, 6, 7, 8, 9]
	y = array_window(x, 3)
	assert y[0] == x[3]
	assert y[2] == x[5]

if __name__ == '__main__' :
	test()
	print "OK: passed tests"
