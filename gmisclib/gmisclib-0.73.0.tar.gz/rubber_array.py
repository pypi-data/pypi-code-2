


"""This acts like a dictionary, but indexed by integers and
stored rather more efficiently, at least in terms of memory.
It is designed for very sparse arrays.
"""

import Num

class ext_block(object):
	def __init__(self, n, vtype=Num.Float):
		self.v = Num.zeros((n,), vtype)
		self.mask = Num.zeros((n,), Num.bool_)

	def set(self, k, v):
		self.v[k] = v
		self.mask[k] = 1


	def get(self, k, IdxErrArg):
		if self.mask[k]:
			return self.v[k]
		else:
			raise IndexError, IdxErrArg


		def unset(self, key):
			self.mask[key] = 0
			return Num.sum(self.mask) == 0


	def contains(self, value):
		return value in self.v.take(indices=self.mask)
		
class extensible_array(object):
	def __init__(self, bsz=300):
		self.x = {}
		self.sz = bsz
		self._len = 0

	def __len__(self):
		return self._len

	def __setitem__(self, k, v):
		"""Doesn't do slice objects."""
		iblock = k//self.sz
		try:
			block = self.x[iblock]
		except KeyError:
			block = ext_block(self.sz)
			self.x[iblock] = block
		self._len = max(self._len, k)
		block.set(k - iblock*self.sz, v)


	def __getitem__(self, k):
		iblock = k//self.sz
		try:
			block = self.x[iblock]
		except KeyError:
			raise IndexError, k
		return self.get(k - iblock*self.sz, k)
	

	def unset(self, key):
		iblock = key//self.sz
		try:
			block = self.x[iblock]
		except KeyError:
			return
		if block.unset(key - iblock*self.sz):
			del self.x[iblock]


	def __contains__(self, item):
		for b in self.x.itervalues():
			if b.contains(item):
				return True
		return False

	def __iter__(self):
		for b in self.x.itervalues():
			nz = Num.nonzero(b.mask)
			v = b.v
			for i in nz:
				yield v[i]
