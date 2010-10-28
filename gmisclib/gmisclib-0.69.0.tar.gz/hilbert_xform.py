import Num


def nextpow2(i):
	j = 1
	while j <= i:
		j *= 2
	return j


def hilbert(x, cutoff):
	"""This is a Hilbert transform when cutoff=0."""

	xx = Num.asarray(x, Num.Float)
	np2 = nextpow2(x.shape[0])
	x = Num.zeros((np2,), Num.Float)
	x[:xx.shape[0]] = xx
	assert len(x.shape) == 1
	n = x.shape[0]
	xt = Num.FFT.fft(x)
	tmp = Num.arrayrange(n)
	f = Num.minimum(tmp, n-tmp) * (1 - 2*Num.greater(tmp, n-tmp))
	window = 1.0 + Num.tanh(f/cutoff)
	Num.multiply(xt, window, xt)
	return Num.FFT.inverse_fft(xt)



if __name__ == '__main__':
	import gpkimgclass
	x = gpkimgclass.read('/home/gpk/voicing/mimic.1.1.d')
	print "0"
	DT = 0.030
	y = hilbert(x.d[:,0], DT/x.dt())
	print "F", y.shape
	tmp = gpkimgclass.gpk_img({'CDELT2': x.dt(), 'HILBERT_CUTOFF': DT,
					'BITPIX': -32,
					'CRPIX2': 0, 'CRVAL2': 0.0},
		Num.absolute(y))
	tmp.write("foo.d")
