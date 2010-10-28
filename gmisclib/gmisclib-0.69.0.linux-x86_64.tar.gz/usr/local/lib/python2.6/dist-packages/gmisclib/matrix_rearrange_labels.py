#!/usr/bin/env python

"""This module helps you plot confusion matrices or similar
images where the axis labels do not have a natural order.
So, the probability of confusing two phonemes is a perfect example:
phonemes do not naturally fall onto a 1-dimensional sequence,
so one is free to put them in any order one likes.
Given that, one might as well put them into an order that
reveals something interesting about the probabilities.

All the functions ending in "2" work on rectangular arrays.
All the functions without "2" work only on square arrays, and
they assume that that both axes remain in the same order.
"""

import numpy

import die
import blue_data_selector



def _mswap(sw1, sw2, m):
	"""Swap rows and columns in matrix m.
	Produces a copy of the matrix.
	@param m: matrix
	@param sw1: how to re-arrange first axis
	@param sw2: how to re-arrange second axis
	"""
	assert sw1.shape == (m.shape[0],)
	assert sw2.shape == (m.shape[1],)
	m1 = numpy.take(m, sw1, axis=0)
	tmp = numpy.take(m1, sw2, axis=1)
	return tmp


def _lswap(swv, m):
	"""Swap labels in list m, according to mapping swv.
	Produces a new list.
	"""
	assert swv.shape == (len(m),)
	return [ m[swv[i]] for i in range(len(m)) ]



class diagfom(object):
	"""A class that defines a figure-of-merit for a matrix.
		It tries to put the largest entries on the diagonal.
		Instances of this class are passed to L{symm_swap_toward_minimal_fom}.
	"""
	def __init__(self, n, sign=1):
		"""@param sign:
			- If sign=1, the f-o-m returned by L{eval}
				will be minimal when
				the most positive matrix elements are on the diagonal.
			- If sign=-1, you'll get minimal fom with the
				the most positive elements off diagonal.
		@type sign: int
		@param n: dimension of matrix.
		@type n: int
		"""
		ar = numpy.arange(n)
		self.weight = sign*numpy.absolute(ar[:,numpy.newaxis] - ar[numpy.newaxis,:])

	def eval(self, swv, m):
		"""Evaluate the figure of merit for a matrix m with the
		specified swap vector.
		@param m: matrix
		@param swv: swap vector
		@return: figure of merit
		@rtype: int or float (according to the type of m).
		"""
		m2 = _mswap(swv, swv, m)
		# return Num.sum(Num.ravel(m2*self.weight))
		tmp = numpy.sum(m2*self.weight)
		return tmp


class diagfom2(object):
	"""This tries to make your matrix approximately diagonal for rectangular matrices.
	"""
	def __init__(self, n1, n2):
		a1 = numpy.arange(n1)
		a2 = numpy.arange(n2)
		self.weight = numpy.absolute(a1[:,numpy.newaxis]/float(n1-1) - a2[numpy.newaxis,:]/float(n2-1))

	def eval(self, sw1, sw2, m):
		m2 = _mswap(sw1, sw2, m)
		# return Num.sum(Num.ravel(m2*self.weight))
		return numpy.sum(m2*self.weight)


class blockfom(object):
	"""This tries to make your matrix into a block form.
	The idea is to mimimize the sum of entry-to-entry differences along a row
	(same with columns).
	"""
	def __init__(self, n1, n2):
		pass

	def eval(self, sw1, sw2, m):
		m2 = _mswap(sw1, sw2, m)
		o = 0.0
		o += numpy.sum(numpy.absolute(m2[1:,:] - m2[:-1,:]))
		o += numpy.sum(numpy.absolute(m2[:,1:] - m2[:,:-1]))
		return o


def symm_swap_toward_minimal_fom(m, fom, maxtries):
	"""Used internally.  Finds an ordering of the labels that minimizes
	whatever C{fom} you supply.   Both axes will have the same order.
	"""
	n = m.shape[0]
	assert m.shape == (n, n)
	swv = numpy.arange(n)
	of = fom.eval(swv, m)
	sincelast = 0
	bds = blue_data_selector.bluedata( [ (i,j) for i in range(n) for j in range(n) if i!=j ] )
	if maxtries is None:
		maxtries = 2*n*n
	for (i,j) in bds:
		oswv = numpy.array(swv, numpy.int, copy=True)
		swv[i], swv[j] = (swv[j], swv[i])
		nf = fom.eval(swv, m)
		if nf < of:
			of = nf
			sincelast = 0
		else:
			swv = oswv
			sincelast += 1
		if sincelast > maxtries:
			break
	return swv


def swap_toward_minimal_fom(m, fom, maxtries):
	"""Used internally.  Finds an ordering of the labels that minimizes
	whatever C{fom} you supply.   The ordering of the two axes may be different.
	"""
	n1, n2 = m.shape
	assert m.shape == (n1, n2)
	sw1 = numpy.arange(n1)
	sw2 = numpy.arange(n2)
	of = fom.eval(sw1, sw2, m)
	sincelast = 0
	bd1 = blue_data_selector.bluedata( [ (i,j) for i in range(n1) for j in range(n1) if i!=j ] )
	bd2 = blue_data_selector.bluedata( [ (i,j) for i in range(n2) for j in range(n2) if i!=j ] )
	if maxtries is None:
		maxtries = 2*(n1*n1 + n2*n2)
	else:
		maxtries = 2*maxtries
	while True:
		i, j = bd1.pick(1)[0]
		osw1 = numpy.array(sw1, numpy.int, copy=True)
		sw1[i], sw1[j] = (sw1[j], sw1[i])
		nf = fom.eval(sw1, sw2, m)
		if nf < of:
			die.info('fom=%g->%g; sincelast=%d' % (of, nf, sincelast))
			of = nf
			sincelast = 0
		else:
			sw1 = osw1
			sincelast += 1

		i, j = bd2.pick(1)[0]
		osw2 = numpy.array(sw2, numpy.int, copy=True)
		sw2[i], sw2[j] = (sw2[j], sw2[i])
		nf = fom.eval(sw1, sw2, m)
		if nf < of:
			of = nf
			die.info('fom=%g->%g; sincelast=%d' % (of, nf, sincelast))
			sincelast = 0
		else:
			sw2 = osw2
			sincelast += 1

		i, j = bd1.pick(1)[0]
		osw1 = numpy.array(sw1, numpy.int, copy=True)
		sw1[i], sw1[j] = (sw1[j], sw1[i])
		i, j = bd2.pick(1)[0]
		osw2 = numpy.array(sw2, numpy.int, copy=True)
		sw2[i], sw2[j] = (sw2[j], sw2[i])
		nf = fom.eval(sw1, sw2, m)
		if nf < of:
			of = nf
			die.info('fom=%g->%g; sincelast=%d' % (of, nf, sincelast))
			sincelast = 0
		else:
			sw1 = osw1
			sw2 = osw2
			sincelast += 1

		if sincelast > maxtries:
			break
	return (sw1, sw2)



def swap_toward_diag(m, lbls, maxtries=None, sign=1):
	"""Swap the rows and columns of a matrix to bring it closer to a diagonal
	matrix: i.e. entries with large absolute values on the main diagonal and small entries
	away from the main diagonal.    Rows and columns are swapped together,
	so that the ordering or rows will match the ordering of columns.
	@param m: a 2-dimensional array
	@type m: numpy.ndarray
	@param lbls: a list of arbitrary labels for each row or column.
	@type lbls: C{list(anything)}
	@type maxtries: int or None
	@param maxtries: how hard to work at optimizing the matrix layout?
		None gives a resonable default value.    Appropriate values are
		a few times the number of elements in the matrix.
	@param sign: (default=1) if C{sign=-1}, do the opposite: put the small absolute
		values on the main diagonal.
	@type sign: int
	@return: A tuple containing the swapped matrix and a swapped list of values.
	@rtype: C{tuple(numpy.ndarray, list(something))}
	"""
	fom = diagfom(len(lbls), sign=sign)
	swv = symm_swap_toward_minimal_fom(numpy.absolute(m), fom, maxtries)
	return ( _mswap(swv, swv, m), _lswap(swv, lbls) )


def swap_toward_positive(m, lbls, maxtries=None, sign=1):
	"""Swap the rows and columns of a matrix to put the most positive values on the
	main diagonal.  Rows and columns are swapped together,
	so that the ordering or rows will match the ordering of columns.
	@param m: a 2-dimensional array
	@type m: numpy.ndarray
	@param lbls: a list of arbitrary labels for each row or column.
	@type lbls: C{list(anything)}
	@type maxtries: int or None
	@param maxtries: how hard to work at optimizing the matrix layout?
		None gives a resonable default value.    Appropriate values are
		a few times the number of elements in the matrix.
	@param sign: (default=1) if C{sign=-1}, do the opposite: put the negative entries
		on the main diagonal.
	@type sign: int
	@return: A tuple containing the swapped matrix and a swapped list of labels.
	@rtype: C{tuple(numpy.ndarray, list(something))}
	"""
	fom = diagfom(len(lbls), sign=sign)
	swv = symm_swap_toward_minimal_fom(m, fom, maxtries)
	return ( _mswap(swv, swv, m), _lswap(swv, lbls) )


def swap_toward_diag2(m, lbl1, lbl2, maxtries=None):
	"""Swap the rows and columns of a matrix to make it roughly
	diagonal:
	i.e. large entries on the main diagonal and small entries
	away from the main diagonal.   Note that this will work
	even if the matrix is not square.
	@param m: a 2-dimensional array
	@type m: numpy.ndarray
	@param lbl1: a list of arbitrary labels for the first index of the matrix C{m}.
	@type lbl1: C{list(anything)}
	@param lbl2: a list of arbitrary labels for the second index of the matrix C{m}.
	@type lbl2: C{list(anything)}
	@type maxtries: int or None
	@param maxtries: how hard to work at optimizing the matrix layout?
		None gives a resonable default value.    Appropriate values are
		a few times the number of elements in the matrix.
	@return: A tuple containing the swapped matrix and the two swapped lists of labels,
		one for the first and one for the second axis.
	@rtype: C{tuple(numpy.ndarray, list(something), list(something))}
	"""
	fom = diagfom2(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(numpy.absolute(m), fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )


def pos_near_diag2(m, lbl1, lbl2, maxtries=None):
	fom = diagfom2(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(m, fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )


def neg_near_diag2(m, lbl1, lbl2, maxtries=None):
	fom = diagfom2(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(-m, fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )


def swap_toward_blocks2(m, lbl1, lbl2, maxtries=None):
	"""Swap rows and columns of a matrix to bring it closer to a block
	form, where similar values occur together in blocks.
	@param m: a 2-dimensional array
	@type m: numpy.ndarray
	@param lbl1: a list of arbitrary labels for the first axis of m
	@type lbl1: C{list(anything)}
	@param lbl2: a list of arbitrary labels for the second axis of m
	@type lbl2: C{list(anything)}
	@type maxtries: int or None
	@param maxtries: how hard to work at optimizing the matrix layout?
		None gives a resonable default value.    Appropriate values are
		a few times the number of elements in the matrix.
	@return: A tuple containing the swapped matrix and the two swapped lists of values,
		one for the first and one for the second axis.
	@rtype: C{tuple(numpy.ndarray, list(something), list(something))}
	"""
	fom = blockfom(len(lbl1), len(lbl2))
	sw1, sw2 = swap_toward_minimal_fom(m, fom, maxtries)
	return ( _mswap(sw1, sw2, m), _lswap(sw1, lbl1), _lswap(sw2, lbl2) )

def swap_toward_blocks(m, lbls, maxtries=None):
	"""Swap rows and columns of a matrix to bring it closer to a block
	form, where similar values occur together in blocks.  It minimizes
	the sum of changes when proceeding along a row or column.
	@param m: a 2-dimensional array
	@type m: numpy.ndarray
	@param lbls: a list of arbitrary labels for the first axis of m
	@type lbls: C{list(anything)}
	@type maxtries: int or None
	@param maxtries: how hard to work at optimizing the matrix layout?
		None gives a resonable default value.    Appropriate values are
		a few times the number of elements in the matrix.
	@return: A tuple containing the swapped matrix and a swapped lists of values.
	@rtype: C{tuple(numpy.ndarray)}, list(something))
	"""
	fom = blockfom(len(lbls), len(lbls))
	swv = symm_swap_toward_minimal_fom(m, fom, maxtries)
	return ( _mswap(swv, swv, m), _lswap(swv, lbls) )


def test1():
	"""Two test cases on 2x2 matrices."""
	m = numpy.array([[0, 1], [1, 0]])
	lbls = ['zero', 'one']
	mswapped, lswapped = swap_toward_diag(m, lbls)
	assert lswapped == ['zero', 'one']
	assert numpy.equal(mswapped, numpy.array([[0, 1], [1, 0]])).all()
	# second test case:
	m = numpy.array([[1, 0], [0, 1]])
	lbls = ['zero', 'one']
	mswapped, lswapped = swap_toward_diag(m, lbls)
	assert lswapped == ['zero', 'one']
	assert numpy.equal(mswapped, numpy.array([[1, 0], [0, 1]])).all()


def test():
	test1()

if __name__ == '__main__':
	test()
