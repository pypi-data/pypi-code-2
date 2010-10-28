import Num
import math

# import sys
# sys.path.append('/home/gpk/djt_code/dpss')
import djt_spectrum


def _p(v, width, ctr, w, K):
	s = int(round(ctr - width/2.0))
	if s < 0:
		return 0
	e = s + width
	if e >= len(v):
		return 0
	p, lmbda = djt_spectrum.low_pass_power(v[s:e], w, K)
	assert lmbda[0]>0.7 and lmbda[-1]>0.7
	# print "lambda=", lmbda
	return p



def pwr_guts(v, dt, binw, w, K):
	"""Local power in a signal.
	dt and binw are measured in terms of the sampling interval of v.
	w is the bandwidth of the filter.
	K is the order of the prolate speroidal fcn.
	"""
	assert binw >= 1
	v = Num.asarray(v)
	nb = int(round(len(v)/dt))
	o = Num.zeros((nb,), Num.Float)
	bw = int(round(binw))
	for i in range(nb):
		o[i] = _p(v, bw, dt*i, w, K)
	return o


def pwr(v, dt, bandwidth, K):
	w = bandwidth
	binw = 0.5*float(K)/float(w)
	return pwr_guts(v, dt, binw, w, K)

def expand(r, a):
	n = len(a)
	nn = int(round(r * n))
	o = Num.zeros((nn,), Num.Float)
	last = 0
	for i in range(n):
		end = int(round((i+1)*r))
		o[last : end] = a[i]
		last = end
	return o


def pwrs(dt, harmonics, f0, signal, sig_dt, bandwidth):
	"""This is a classical synchronous demodulator, with
	DPSS windowing to get maximally steep skirts and
	out-of-band rejection.

	dt=output power measurement interval.
	harmonics = [ which harmonics to measure (multiples of f0) ]
	f0 = frequency as a function of time (measured at intervals of dt)
	signal = input signal to be demodulated
	sig_dt = sampling interval of signal.
	"""

	K = 3
	assert len(f0.shape) == 1
	assert bandwidth > 0
	f = expand(dt/sig_dt, f0)
	phase = Num.add.accumulate((2*math.pi*sig_dt)*f)
	f = None	# Reclaim memory
	o = []
	signal = signal[:len(phase)]
	for h in harmonics:
		mod = Num.exp((1j * h) * phase) * signal
		o.append(pwr(mod, dt/sig_dt, bandwidth*sig_dt, K))
	return o


def one_ampl(harmonics, phase, signal, binw, nbin=None):
	"""Everything measured in samples.  Phase and signal have same sampling rate."""
	import sharp_energy
	if nbin is None:
		nbin = 4
	if harmonics == "?data length":
		return sharp_energy.one_median(binw, "?data length", None, nbin)
	assert phase.shape[0] == signal.shape[0]
	center = 0.5 * signal.shape[0]
	o = []
	for h in harmonics:
		mod = Num.exp((1j * h) * phase) * signal
		m = sharp_energy.one_median(binw, center, mod, nbin)
		o.append(m)
	return o


def stepped_ampl(dt, harmonics, f0, signal, sig_dt, subwindow=0.010, nsubw = 4):
	"""signal -> amplitudes in specified harmonics
	dt=time interval of f0 samples = time interval of ampl measurements.
	"""
	assert len(f0.shape) == 1
	import sharp_energy
	f = expand(dt/sig_dt, f0)
	phase = Num.add.accumulate((2*math.pi*sig_dt)*f)
	f = None # Reclaim memory.
	o = []
	signal = signal[:len(phase)]
	for h in harmonics:
		mod = Num.exp((1j * h) * phase) * signal
		m = sharp_energy.stepped_median(dt/sig_dt, subwindow/sig_dt,
						mod, nsubw)
		o.append(m)
	return o



def test0():
	for period in range(6,50):
		t = Num.arrayrange(1000)
		f = 1.0/period
		s = Num.cos(t*f*2*math.pi)
		x = stepped_ampl(100, [1, 2], Num.array([f]*5), s, 1, 100, 4)
		print period, abs(x[0][2]), x[0][2], abs(x[1][2])



def test1():
	o = []
	for period in range(2, 200):
		t = Num.arrayrange(1000)
		s = Num.cos(t*2*math.pi/period)
		o.append(pwr(s, 100.0, 0.01, 4)[3])
	for period in range(3, 200):
		print period, o[period-1]



if __name__ == '__main__':
	test0()
	# test1()
