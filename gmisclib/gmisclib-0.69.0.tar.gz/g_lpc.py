"""Linear prediction of signals"""

import numpy
import lapack_dgesv




def lp1_fit(y, x, indices, noise=0.0):
	"""Predicts y[i] in terms of the set of x[i+q] for q in indices."""
	y = numpy.asarray(y, numpy.float)
	x = numpy.asarray(x, numpy.float)
	m = x.shape[0]
	assert x.shape == (m,)
	assert y.shape == (m,)
	idx = indices[:]
	idx.sort()
	nix = len(idx)
	imin = idx[0]
	imax = idx[-1]
	noise2 = noise*noise
	n = len(indices)
	phi = numpy.zeros((n,n), numpy.double)
	phistar = numpy.zeros((n,1), numpy.double)
	s = max(-imin, 0)
	e = min(m - imax - 1, m-1)
	mm = e - s + 1
	fmm = float(mm)
	for i in range(nix):
		ii = idx[i]
		for j in range(nix):
			jj = idx[j]
			phi[i,j] = numpy.dot(x[s+ii:s+ii+mm], x[s+jj:s+jj+mm])/fmm
		phi[i,i] += noise2
		phistar[i,0] += numpy.dot(y[s:s+mm], x[s+ii:s+ii+mm])/fmm
	# print "phistar=", phistar
	# print "phi=", phi
	coef = lapack_dgesv.dgesv(phi, phistar)
	return (coef[:,0], idx)



def add_sloppy(a, b, offset):
	"""Accumulate b onto a.
	Allow b to be smaller (fill with zeros), or larger (drop)."""
	n = a.shape[0]
	m = b.shape[0]
	if offset < 0:
		b0 = -offset
		a0 = 0
	else:
		b0 = 0
		a0 = offset
	ae = n
	be = m
	if ae-a0 > be-b0:
		ae = a0 + (be-b0)
	if be-b0 > ae-a0:
		be = b0 + (ae-a0)
	# print "a=", a0, ae, "b=", b0, be
	# print "a.shape=", a.shape, "b.shape=", b.shape
	numpy.add(a[a0:ae], b[b0:be], a[a0:ae])



def lp1_run(x, coef, indices):
	idx = indices[:]
	idx.sort()
	x = numpy.asarray(x, numpy.double)
	n = x.shape[0]
	o = numpy.zeros((n,), numpy.double)
	for j in range(len(idx)):
		add_sloppy(o, x*coef[j], -idx[j])
	return o



if __name__ == '__main__':
	di = [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
	d = [0, 0.5, 1, 0.5, 0.5, 1, 0.5, 0.5, 1, 0.5, 0.5, 1, 0.5,
		0, 0.5, 1, 0.5, 0, 0, 0.5, 1, 0.5, 0, 0]
	
	coef, idx = lp1_fit(d, di, [-1, 0, 1], 0.0001)
	tmp = lp1_run(di, coef, idx)
	assert numpy.absolute(numpy.ravel(tmp-d)) < 0.0001

	coef, idx = lp1_fit(di[1:], di[:-1], [-1, 0, 1], 0.0001)
	tmp = lp1_run(di[:-1], coef, idx)
	assert numpy.absolute(numpy.ravel(tmp-di[1:])) < 0.0001
