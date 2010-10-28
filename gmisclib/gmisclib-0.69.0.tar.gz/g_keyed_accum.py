from __future__ import division


class _keyed_thing:
	def __init__(self):
		self._s = {}
	
	def keys(self):
		return self._s.keys()
	
	def values(self):
		return [ self._out(v) for v in self._s.itervalues() ]
	
	def iterkeys(self):
		return self._s.iterkeys()
	
	def items(self):
		return [ (k, self._out(v)) for (k, v) in self._s.iteritems() ]
	
	def get(self, key):
		return self._out( self._s[key] )
	
	def __contains__(self, key):
		return key in self._s
	
	def clear(self):
		return self._s.clear()
	
	def has_key(self):
		return self._s.has_key()
	
	def __iter__(self):
		return self._s.iterkeys()
	
	def __len__(self):
		return len(self._s)
	
	def __delitem__(self, k):
		del self._s[k]
	


class keyed_avg(_keyed_thing):
	def __init__(self):
		_keyed_thing.__init__(self)
	
	def add(self, key, value):
		try:
			s, n = self._s[key]
		except KeyError:
			s = 0.0
			n = 0
		self._s[key] = (s+value, n+1)
	
	@staticmethod
	def _out(stored):
		s, n = stored
		return s/n


def test():
	x = keyed_avg()
	x.add('a', 1)
	x.add('a', 2)
	x.add('b', 2)
	print x.get('a')
	print x.keys()
	print x.values()

if __name__ == '__main__':
	test()
