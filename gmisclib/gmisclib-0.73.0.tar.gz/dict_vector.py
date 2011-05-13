"""Vectors of numbers, but indexed as a dictionary.
"""

import math
import operator
import __builtin__
from gmisclib import gpkmisc
from gmisclib import dictops


class dict_vector(dict):
	SCALARS = (int, float)
	ZERO = 0

	def copy(self):
		return dict_vector(self)


	def incr(self, k, v):
		if k in self:
			self[k] += v
		else:
			self[k] = v


	def __add__(self, other):
		tmp = self.copy()
		if isinstance(other, self.SCALARS):
			for k in tmp.keys():
				tmp[k] += other
		else:
			for (k, v) in other.items():
				try:
					tmp[k] += v
				except KeyError:
					tmp[k] = v
		return tmp


	def __gt__(self, other):
		tmp = dict_vector()
		if isinstance(other, self.SCALARS):
			for (k, v) in self.items():
				tmp[k] = v > other
		else:
			for (k, v) in self.items():
				tmp[k] = v > other.get(k, self.ZERO)
			for (k, v) in other.items():
				if k not in tmp:
					tmp[k] = self.get(k, self.ZERO) > v
		return tmp


	def __lt__(self, other):
		tmp = dict_vector()
		if isinstance(other, self.SCALARS):
			for (k, v) in self.items():
				tmp[k] = v < other
		else:
			for (k, v) in self.items():
				tmp[k] = v < other.get(k, self.ZERO)
			for (k, v) in other.items():
				if k not in tmp:
					tmp[k] = self.get(k, self.ZERO) < v
		return tmp


	def __ge__(self, other):
		tmp = dict_vector()
		if isinstance(other, self.SCALARS):
			for (k, v) in self.items():
				tmp[k] = v >= other
		else:
			for (k, v) in self.items():
				tmp[k] = v >= other.get(k, self.ZERO)
			for (k, v) in other.items():
				if k not in tmp:
					tmp[k] = self.get(k, self.ZERO) >= v
		return tmp


	def __le__(self, other):
		tmp = dict_vector()
		if isinstance(other, self.SCALARS):
			for (k, v) in self.items():
				tmp[k] = v <= other
		else:
			for (k, v) in self.items():
				tmp[k] = v <= other.get(k, self.ZERO)
			for (k, v) in other.items():
				if k not in tmp:
					tmp[k] = self.get(k, self.ZERO) <= v
		return tmp




	def __mul__(self, other):
		tmp = dict_vector()
		if isinstance(other, self.SCALARS):
			tmp = self.copy()
			for (k, v) in self.items():
				tmp[k] = v * other
		else:
			for (k, v) in other.items():
				tmp[k] = self.get(k, self.ZERO) * v
			for (k, v) in self.items():
				if k not in tmp:
					tmp[k] = v * other.get(k, self.ZERO)
		return tmp



	def __div__(self, other):
		if isinstance(other, self.SCALARS):
			if other == self.ZERO:
				raise ZeroDivisionError, "float denominator"
			else:
				tmp = dict_vector()
				for (k, v) in self.items():
					tmp[k] = v / other
		else:
			tmp = dict_vector()
			for (k, v) in other.items():
				if v != self.ZERO:
					tmp[k] = self.get(k, self.ZERO) / v
				else:
					raise ZeroDivisionError, "denom[%s]=%s" % (str(k), str(v))
			for (k, v) in self.items():
				if k not in tmp:
					try:
						tmp[k] = v / other[k]
					except KeyError:
						raise ZeroDivisionError, "denom[%s] is empty" % str(k)
		return tmp


	def __iadd__(self, other):
		if isinstance(other, self.SCALARS):
			for k in self.keys():
				self[k] += other
		else:
			for (k, v) in other.items():
				try:
					self[k] += v
				except KeyError:
					self[k] = v
		return self


	def __isub__(self, other):
		if isinstance(other, self.SCALARS):
			for k in self.keys():
				self[k] -= other
		else:
			for (k, v) in other.items():
				try:
					self[k] -= v
				except KeyError:
					self[k] = -v
		return self


	def __sub__(self, other):
		tmp = self.copy()
		if isinstance(other, self.SCALARS):
			for k in tmp.keys():
				tmp[k] -= other
		else:
			for (k, v) in other.items():
				try:
					tmp[k] -= v
				except KeyError:
					tmp[k] = -v
		return tmp


	__radd__ = __add__
	__rmul__ = __mul__


	def __rsub__(self, other):
		tmp = self.copy()
		if isinstance(other, self.SCALARS):
			for k in tmp.keys():
				tmp[k] = other - tmp[k]
		else:
			for (k, v) in other.items():
				try:
					tmp[k] = v - tmp[k]
				except KeyError:
					tmp[k] = v
		return tmp

	
	def __abs__(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			tmp[k] = __builtin__.abs(v)
		return tmp



	def __invert__(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			tmp[k] = -v
		return tmp


	def sum(self):
		return reduce(operator.add, self.values())


	def median(self):
		return gpkmisc.median(self.values())


	def all(self):
		for v in self.values():
			if not v:
				return False
		return True


	def float(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			tmp[k] = float(v)
		return tmp


	def int(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			tmp[k] = int(v)
		return tmp


	def iint(self):
		for k in self.keys():
			self[k] = int(tmp[v])


	def ifloat(self):
		for k in self.keys():
			self[k] = float(tmp[v])


	def sign(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			if v > self.ZERO:
				tmp[k] = 1
			elif v < self.ZERO:
				tmp[k] = -1
			else:
				tmp[k] = self.ZERO
		return tmp


	def round(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			tmp[k] = __builtin__.round(v)
		return tmp


	def iround(self):
		for k in self.keys():
			self[k] = __builtin__.round(tmp[v])


	def idropzero(self):
		drops = []
		for (k, v) in self.items():
			if v == self.ZERO:
				drops.append(k)
		for k in drops:
			del self[k]

	def dropzero(self):
		tmp = dict_vector()
		for (k, v) in self.items():
			if not v == self.ZERO:
				tmp[k] = v
		return tmp

def round(x):
	return x.round()


def log(x):
	tmp = dict_vector()
	for (k, v) in x.items():
		tmp[k] = math.log(v)
	return tmp



def min_within(x):
	best = None
	vmin = None
	first = True
	for (k, v) in x.items():
		if first or v < vmin:
			vmin = v
			best = k
			first = False
	if first:
		raise ValueError, "Empty input sequence"
	return (best, vmin)


def max_within(x):
	best = None
	vmin = None
	first = True
	for (k, v) in x.items():
		if first or v > vmin:
			vmin = v
			best = k
			first = False
	if first:
		raise ValueError, "Empty input sequence"
	return (best, vmin)


def min_between(*x):
	tmp = dictops.dict_of_lists()
	scalars = []
	for xx in x:
		if isinstance(xx, (int, float)):
			scalars.append(xx)
		else:
			for (k, v) in xx.items():
				tmp.add(k, v)
	rv = dict_vector()
	for (k, vlist) in tmp.items():
		rv[k] = min(vlist + scalars)
	return rv


def max_between(*x):
	tmp = dictops.dict_of_lists()
	scalars = []
	for xx in x:
		if isinstance(xx, (int, float)):
			scalars.append(xx)
		else:
			for (k, v) in xx.items():
				tmp.add(k, v)
	rv = dict_vector()
	for (k, vlist) in tmp.items():
		rv[k] = max(vlist + scalars)
	return rv
