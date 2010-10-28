from gmisclib import Num

"""Perceptual frequency scales."""
__version__ = "$Revision: 1.3 $"

if hasattr(Num, 'asinh'):
	asinh = Num.asinh
else:
	def asinh(x):
		tmp = Num.greater(x, 0)
		p = Num.log(x + Num.sqrt(x*x + 1))
		n = -Num.log(-x + Num.sqrt(x*x + 1))
		return tmp*p + (1-tmp)*n

def acosh(x):
	assert not Num.greater(x, 1)
	return Num.log(x - Num.sqrt(x*x-1))

def f_to_bark(f):
	"""frequency to critical band number.
	See Schroeder et al. (1979).
	"""
	return 7*asinh(Num.asarray(f)/650.0)

def bark_to_f(b):
	"""critical band number -> frequency
	M. R. Schroeder, B.S. Atal, J.L. Hall (1979), J.Acous.Soc.Am. 66(6) 1647-1652.
	Title: "Optimizing Digital Speech Coders by exploiting masking
	properties of the Human Ear."
	"""
	return 650*Num.sinh(Num.asarray(b)/7.0)


def cbw(b):
	"""Critical bandwidth (in Hz) at frequency b (barks)."""
	return (650.0/7.0)*Num.cosh(b/7.0)


if __name__ == "__main__":
	print f_to_bark(51)
	print f_to_bark(149)
