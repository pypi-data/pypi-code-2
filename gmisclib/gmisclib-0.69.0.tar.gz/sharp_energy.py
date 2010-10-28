import Num
import math
import cmath
import dpss
import gpkmisc




def complex_median(x):
	if x.typecode() == Num.Float:
		return gpkmisc.N_median(x)

	r1 = gpkmisc.N_median(x.real)
	i1 = gpkmisc.N_median(x.imag)
	phasor = cmath.exp(1j*math.pi/4)
	t = x*phasor
	r2 = gpkmisc.N_median(t.real)
	i2 = gpkmisc.N_median(t.imag)
	return 0.5*(complex(r1,i1) + complex(r2,i2)/phasor)


def one_median(binw, center, v, nbins=None):
	"""Local power in a signal.
	dt and binw are measured in bins.
	"""
	if nbins is None:
		nbins = 3
	assert type(binw) == type(1)
	assert binw>=1
	hbw = binw/2.0

	if center == "?data length":	# How much data do you need?
		return int(math.ceil(hbw*(4*nbins+1))) + binw

	w = 0.5/binw
	# print "binw=", binw, "1/w=", 1/w, "nbins=", nbins, "center=", center
	lmbda, window = dpss.dpsscache(w, 1, binw)
	assert lmbda[0]>0.7  and  lmbda[0]<=1.0
	v = Num.asarray(v)
	t = Num.zeros((4*nbins+1,), v.typecode())
	m = 0
	for k in range(-2*nbins, 2*nbins+1):
		ctr = center + hbw * k
		s = int(round(ctr - hbw))
		if s < 0:
			continue
		e = s + binw
		if e >= len(v):
			continue
		t[m] = Num.sum(v[s:e] * window[0])
		# print "bin", k, "s=", s, "e=", e, "t=", t[m]
		m += 1
	return complex_median(t[:m]) / Num.sum(window[0])



def stepped_median(dt, binw, v, nbins=None):
	"""Local power in a signal.
	dt and binw are measured in bins.
	"""
	binw = int(round(binw))
	v = Num.asarray(v)
	nb = int(round(len(v)/dt))
	o = Num.zeros((nb,), v.typecode())
	for i in range(nb):
		o[i] = one_median(binw, dt*i, v, nbins)
	return o


def pwr(dt, binw, v, nbins=3):
	v = Num.asarray(v, Num.Float)
	return stepped_median(dt, binw, Num.square(v), nbins)


if __name__ == '__main__':
	print pwr(1, 3, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
	# print pwr(1, 3, [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
	# print pwr(1, 3, [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1])
