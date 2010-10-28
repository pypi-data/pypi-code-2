"""This chooses samples such that the specified attributes are
broadly distributed.
"""

import math
import random
from gmisclib import dictops


def _entropy_of_list(a):
	s = 0
	for d in a:
		s += d
	e = 0.0
	for d in a:
		if d > 0:
			p = float(d)/float(s)
			e += p*math.log(p)
	# print '\t\tEOL=%g from %s' % (-e, a)
	return -e



class blue_attributes(object):
	def __init__(self, inspector, data):
		"""@param inspector: a function on a datum that returns a list of attributes."""
		self.inspector = inspector
		self.data = list(data)
		self.inspections = None
		self.counts = None
		self._peek = None
		self._haspeek = False
		self.na = None


	def pick(self, n):
		for i in range(n):
			yield self.pick_one()


	def pick_one(self):
		"""Pick one item from the data set.
		"""
		if self.inspections is None:
			self._initialize()
		if self._haspeek:
			self._haspeek = False
			return self._peek
		n = int(round(math.sqrt(len(self.data))))
		tmp = []
		assert len(self.inspections) == len(self.data)
		for j in random.sample(range(len(self.data)), n):
			# print 'Try %d=%s -> %s' % (j, self.data[j], self.inspections[j])
			tmp.append((self._entropy(self.inspections[j]), j))
		tmp.sort()
		e, j = tmp[-1]
		d = self.data.pop(j)
		ins = self.inspections.pop(j)
		self._add(ins)
		return d


	def _initialize(self):
		attr = self.inspector(self.data[0])
		self.na = len(attr)
		self.counts = [dictops.dict_of_accums() for q in attr]
		self.inspections = []
		for d in self.data:
			alist = self.inspector(d)
			assert len(alist) == self.na
			self.inspections.append(alist)
			for (i,a) in enumerate(alist):
				self.counts[i].add(a, 0)

	def _entropy(self, xtra):
		assert len(xtra) == self.na
		e = 0.0
		for i in range(self.na):
			tmp = self.counts[i].copy()
			tmp.add(xtra[i], 1)
			e += _entropy_of_list(tmp.values())
		# print '\t xtra=%s -> e=%g' % (xtra, e)
		return e

	def _add(self, xtra):
		assert len(xtra) == self.na
		for i in range(self.na):
			self.counts[i].add(xtra[i], 1)

	def peek(self):
		"""Inspect (but do not remove) the next item to be picked.
		@return: the next item to be picked.
		@rtype: whatever (not a list!)
		"""
		if not self._haspeek:
			self._peek = self.pick()
			self._haspeek = True
		return self._peek


	def add(self, datum):
		"""Add another datum to be sampled.
		@type datum: whatever
		@param datum: thing to be added.   It
			has a probability of C{1/len(self)} of being the next sample.
		"""
		self.data.append(datum)
		alist = self.inspector(datum)
		self.inspections.append(alist)
		self._haspeek = False
		assert len(alist) == self.na
		for (i,a) in enumerate(alist):
			self.counts[i].add(a, 0)


	def __len__(self):
		return len(self.data)


	def reset(self):
		"""Forget prior history of usage.   Choices after this
		call are uncorrelated with choices before this call."""




def test():
	x = ['a']*1000 + ['b']*100
	tmp = blue_attributes(lambda x: (x,), x)
	c = dictops.dict_of_accums()
	for i in range(20):
		c.add(tmp.pick(), 1)
	assert abs(c['a']-c['b']) <= 1
	for i in range(50):
		c.add(tmp.pick(), 1)
	assert abs(c['a']-c['b']) <= 2

if __name__ == '__main__':
	test()
