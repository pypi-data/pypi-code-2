"""Find different permutations of an array."""

import Num

def _next_guts(a, n):
	"""Increments the array."""
	o = Num.array(a, copy=True)
	o[0] += 1
	for i in range(len(o)):
		if o[i] >= n:
			o[i] = 0
			if i+1 >= n:
				return None
			else:
				o[i+1] += 1
	return o

def _good(p):
	"""Tests if the array is a valid permutation."""
	used = Num.zeros(p.shape, Num.Int)
	for i in p:
		if used[i]:
			return 0
		used[i] = 1
	return 1


def next(a, n):
	"""Finds the first valid permutation of n items after a.
	A valid permutation is an array of length n which
	contains values from 0 to n-1, once each.
	This function returns the lexicographically next permutation;
	it's input need not be a valid permutation, but all the
	entries of a should be in the range 0 to n-1, inclusive.
	"""
	while 1:	# Klugey, slow implementation.
		a = _next_guts(a, n)
		if a is None or _good(a):
			return a
	return None

def factorial(n):
	if n == 1:
		return 1
	return n * factorial(n-1)

def permutations(n):
	"""Returns an array of all the n! permutations of n objects."""
	o = []
	p = Num.zeros((n,), Num.Int)
	if _good(p):
		o.append(p)	# Only for n==0
	while 1:
		p = next(p, n)
		if p is None:
			assert len(o)==factorial(n)
			return o
		o.append(p)
	return None


if __name__ == '__main__':
	assert factorial(5) == 120
	p1 = permutations(1)
	assert len(p1) == 1
	assert len(p1[0]) == 1
	assert p1[0][0] == 0
	p2 = permutations(2)
	assert len(p2)==2
	assert len(p2[0]) == 2
	assert p2[0][0] == 1
	assert p2[0][1] == 0
	assert p2[1][0] == 0
	assert p2[1][1] == 1
