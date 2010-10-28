
"""ERB Perceptual frequency scale."""

import math
import Num

__version__ = "$Revision: 1.6 $"

def f_to_erb(f):
	"""Frequency to ERB band number.
	http://ccrma-www.stanford.edu/~jos/bbt/Equivalent_Rectangular_Bandwidth.html
	"""
	return Num.log(0.00437*f+1)*(21.4/math.log(10.0))

def erb_to_f(e):
	"""ERB number -> frequency
	"""
	return (10.0**(e/21.4)-1)/0.00437


def ebw(e):
	"""Critical bandwidth (in Hz) at frequency e (erbs)."""
	return 0.108*erb_to_f(e) + 24.7


if __name__ == "__main__":
	print f_to_erb(51)
	print f_to_erb(149)
