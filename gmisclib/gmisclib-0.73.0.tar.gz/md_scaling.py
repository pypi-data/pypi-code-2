"""Find a set of points so that the distances between them match
a desired set of distances."""

import opt
import Numeric
import math
import RandomArray


EPS = 1e-3
G = 1

def _fcn(p, args, diffparam, diffctr, processor):
	assert p.shape[0] == G + args['np']*args['ndim']
	alpha = p[0]
	np = args['np']
	r = Numeric.zeros((np, np), Numeric.Float)
	c = Numeric.reshape(p[G:], (np, args['ndim']))
	dij = args['dij']
	dba = math.pow(args['dbar'], 1.0-alpha)
	print "_fcn, alpha=", alpha, "diffparam=", diffparam, "dba=", dba

	# Which residuals do I have to recalculate, if I'm changing parameter diffparam? :
	if diffparam is None or diffparam<G:
		rng = range(np)
	else:
		# rng = [ (diffparam-G)%np ] 	# --or--
		rng = [ (diffparam-G)/args['ndim'] ]
		r[:,:] = diffctr[:,:]
		print "# changing p", diffparam-G, "to", p[diffparam]

	# print "r.shape=", r.shape, "c.shape=", c.shape, "rng=", rng
	for i in range(np):
		for j in rng:
			r[i, j] = dba*(math.pow(_dist(c[i], c[j]), alpha)) - dij[i,j]
	if len(rng) < np:
		for i in rng:
			for j in range(np):
				r[i, j] = dba*(math.pow(_dist(c[i], c[j]), alpha)) - dij[i,j]

	ctrzero = Numeric.sum(c, axis=0)/(args['dbar']*math.sqrt(np))
	assert c.shape == (args['ndim'],)
	# Rotations, too! For first point, all but one coordinate is zero.  For second, all but two...
	rots = []
	for i in range(1, min(np, args['ndim'])):
		for j in range(args['ndim'] - i):
			rots.append(c[i-1, j])

	return (r, ctrzero)



def find_rep(dij, ndim):
	np = dij.shape[0]
	assert dij.shape == (np, np)

	dbar = math.sqrt(Numeric.sum(dij**2)/(np*np))
	print "# dbar=", dbar, "np=", np, "ndim=", ndim

	T = dbar*dbar/30

	nprm = np*ndim + G
	p = Numeric.zeros((nprm,), Numeric.Float)
	p[0] = 1.0
	p[G:] = RandomArray.random(np*ndim)

	o = opt.opt(p, T/20, _fcn, args=locals().copy())
	o.set_nthreads(1)
	o.working_precision = Numeric.Float32
	o.verbose = 1
	o.run(Ta=T)
	return (o.p.p[0], Numeric.reshape(o.p.p[G:], (np, ndim)))


def _dist(a, b):
	delta = a-b
	return Numeric.sum(delta**2)


def distances(xi):
	nx = xi.shape[0]
	nd = xi.shape[1]
	print "# nx=", nx, "nd=", nd
	assert xi.shape == (nx, nd)
	dij = Numeric.zeros((nx, nx), Numeric.Float)
	for i in range(nx):
		for j in range(nx):
			dij[i,j] = _dist(xi[i], xi[j])
	return dij


def test():
	y = Numeric.array([[-1,0], [1,0], [0,1], [0,-1]], Numeric.Float)
	print "y=", y
	dist = distances(y)
	print "dist=", dist
	alpha, x = find_rep(dist, 2)
	print "alpha=", alpha
	print "x=", x

if __name__ == '__main__':
	import gpkimgclass
	import sys
	import die
	arglist = sys.argv[1:]
	transpose = 0
	nd = 2
	while len(arglist)>0 and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '-d':
			nd = int(arglist.pop(0))
		elif arg == '-t':
			transpose = 1
		elif arg == '--':
			break
		else:
			die.die("Unrecognized argument: %s" % arg)
	print "# nd=", nd
	print "# transpose=", transpose
	f = arglist[0]
	data = gpkimgclass.read(f)
	if transpose:
		data.d = Numeric.transpose(data.d)
	dist = distances(data.d)
	alpha, x = find_rep(dist, nd)
	print "# alpha=", alpha
	assert x.shape[1] == 2
	for i in range(x.shape[0]):
		for j in range(nd):
			sys.stdout.write(" %g" % x[i,j])
		sys.stdout.write("\n")
		sys.stdout.flush()

