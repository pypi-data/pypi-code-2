"""This computes order statistics on data with weights.
"""

import numpy
from gmisclib import Num


def wp(data, wt, percentiles):
	"""Compute weighted percentiles.
	If the weights are equal, this is the same as normal percentiles.
	Elements of the C{data} and C{wt} arrays correspond to
	each other and must have equal length (unless C{wt} is C{None}).

	@param data: The data.
	@type data: A L{numpy.ndarray} array or a C{list} of numbers.
	@param wt: How important is a given piece of data.
	@type wt: C{None} or a L{numpy.ndarray} array or a C{list} of numbers.
		All the weights must be non-negative and the sum must be
		greater than zero.
	@param percentiles: what percentiles to use.  (Not really percentiles,
		as the range is 0-1 rather than 0-100.)
	@type percentiles: a C{list} of numbers between 0 and 1.
	@rtype: [ C{float}, ... ]
	@return: the weighted percentiles of the data.
	"""
	assert Num.alltrue(Num.greater_equal(percentiles, 0.0)), "Percentiles less than zero"
	assert Num.alltrue(Num.less_equal(percentiles, 1.0)), "Percentiles greater than one"
	data = Num.asarray(data)
	assert len(data.shape) == 1
	if wt is None:
		wt = Num.ones(data.shape, Num.Float)
	else:
		wt = Num.asarray(wt, Num.Float)
		assert wt.shape == data.shape
		assert Num.alltrue(Num.greater_equal(wt, 0.0)), "Not all weights are non-negative."
	assert len(wt.shape) == 1
	n = data.shape[0]
	assert n > 0
	i = Num.argsort(data)
	sd = Num.take(data, i, axis=0)
	sw = Num.take(wt, i, axis=0)
	aw = Num.add.accumulate(sw)
	if not aw[-1] > 0:
		raise ValueError, "Nonpositive weight sum"
	w = (aw-0.5*sw)/aw[-1]
	spots = Num.searchsorted(w, percentiles)
	o = []
	for (s, p) in zip(spots, percentiles):
		if s == 0:
			o.append(sd[0])
		elif s == n:
			o.append(sd[n-1])
		else:
			f1 = (w[s] - p)/(w[s] - w[s-1])
			f2 = (p - w[s-1])/(w[s] - w[s-1])
			assert f1>=0 and f2>=0 and f1<=1 and f2<=1
			assert abs(f1+f2-1.0) < 1e-6
			o.append(sd[s-1]*f1 + sd[s]*f2)
	return o



def wtd_median(data, wt):
	"""The weighted median is the point where half the weight is above
	and half the weight is below.   If the weights are equal, this is the
	same as the median.   Elements of the C{data} and C{wt} arrays correspond to
	each other and must have equal length (unless C{wt} is C{None}).

	@param data: The data.
	@type data: A L{numpy.ndarray} array or a C{list} of numbers.
	@param wt: How important is a given piece of data.
	@type wt: C{None} or a L{numpy.ndarray} array or a C{list} of numbers.
		All the weights must be non-negative and the sum must be
		greater than zero.
	@rtype: C{float}
	@return: the weighted median of the data.
	"""
	spots = wp(data, wt, [0.5])
	assert len(spots)==1
	return spots[0]


def wtd_median_across(list_of_vectors, wt):
	"""Takes a weighted component-by-component median of a sequence of vectors.
	@param list_of_vectors: the data to be combined
	@type list_of_vectors: any sequence of lists or numpy.ndarray.
		All the inside lists must be of the same length.
	@type wt: a vector of weights (one weight for each input vector) or None.
	@param wt: sequence of numbers or None
	@return: the median vector.
	@rtype: C{numpy.ndarray}
	"""
	lov = list(list_of_vectors)
	n = len(lov[0])
	for v in lov:
		if len(v) != n:
			for (i,vv) in enumerate(lov):
				if len(vv) != n:
					raise ValueError, "Vector lengths don't match: %d[0] and %d[%d]" % (n, len(vv), i)
	m = len(lov)
	tmp = numpy.zeros((m,))
	rv = numpy.zeros((n,))
	for i in range(n):
		for (j,v) in enumerate(lov):
			tmp[j] = v[i]
		rv[i] = wtd_median(tmp, wt)
	return rv
	


def test():
	assert Num.allclose(wp([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], None,
					[0.0, 1.0, 0.5, 0.51, 0.49, 0.01, 0.99]),
				[1.0, 10.0, 5.5, 5.6, 5.4, 1.0, 10.0], 0.0001)
	assert Num.allclose(wp([0, 1, 2, 3, 4], [0.1, 1.9, 1.9, 0.1, 1],
					[0.0, 1.0, 0.01, 0.02, 0.99]),
					[0.0, 4.0, 0.0, 0.05, 4.0], 0.0001)


def test_median():
	d = [1,1,1,1,2,2,2,2]
	w = [1,1,1,1,2,1,1,1]
	assert 1.0 <= wtd_median(d,w) <= 2.0
	d = [1.0,1,1,1, 2,2,2,2]
	w = [1,1.1,2,1, 2,1,1,1]
	assert 1.0 <= wtd_median(d,w) <= 2.0
	d = [1,1,1,1,2,3,3,3,3.0]
	w = [1,1,1,1,1.0,1,1,1,1]
	assert abs(wtd_median(d,w)-2.0) < 0.001
	d = [1,1,1,1,2,3,3,3,3.0]
	w = [1,1,1.1,1,1.0,1,1,1,1]
	assert 1.0 <= wtd_median(d,w) <= 2.0
	d = [1,1,1,1,2,3,3,3,3.0]
	w = [1.3,1.3,1.3,1.3,1.0,1,1,1,1]
	assert 1.0 <= wtd_median(d,w) <= 2.0
	d = [1,1,1,1,2,3,4,4.0]
	w = [1.,1.,1.,1.,0.0,1,2,2]
	assert abs(wtd_median(d,w)-3.0) < 0.001


if __name__ == '__main__':
	test_median()
	test()
