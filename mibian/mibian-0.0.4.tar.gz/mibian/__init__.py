'''
Mibian.py - Options Pricing Open Source Library - http://code.mibian.net/
Copyright (C) 2011 Yassine Maaroufi -  <yassinemaaroufi@mibian.net>
Distributed under GPLv3 - http://www.gnu.org/copyleft/gpl.html
'''
from math import log, e
try:
	from scipy.stats import norm
except:
	print 'Mibian requires scipy to be installed to work properly'

# WARNING: All numbers should be floats -> x = 1.0

def N(x):
	''' Normal Cumulative Distribution Function'''
	return norm.cdf(x)

def countDigits(x):
	return len(str(x).split('.')[1])

def prepArgs(S, rd, rf, o, T):
	S = float(S)
	rd = float(rd) / 100
	rf = float(rf) / 100
	o = float(o) / 100
	T = float(T) / 360
	return [S, rd, rf, o, T]

# Arguments: f: function, args: function arguments, p: position of the target in the argument array, target, high, low
def solve(f, args, p, target, high, low):
	r = countDigits(target)
	mid = (high - low) / 2
	#estimate = 0.0
	while True:
		#estimate = self.price(S, K, rd, rf, mid, T)[0]
		args[p] = mid
		estimate = apply(f, args)[0]
		if round(estimate, r) == target: return mid
		elif estimate > target: high = mid
		elif estimate < target: low = mid
		mid = low + ((high - low) / 2)


class GK:
	'''Garman-Kohlhagen'''

	def price(self, S, K, rd, rf, o, T):
		'''Option price

		Arguments:
		S: Underlying Price
		K: Strike Price
		rd: Domestic Interest Rate
		rf: Foreign Interest Rate
		o: Volatility
		T: Nb of Days to Maturity

		Returns [Call price, Put price]
		'''
		[S, rd, rf, o, T] = prepArgs(S, rd, rf, o, T)
	
		a = o * T**0.5
		d1 = (log(S/K) + (rd - rf + (o**2)/2) * T) / a
		d2 = (log(S/K) + (rd - rf - (o**2)/2) * T) / a
		#d2 = d1 - a
		C = e**(-rf * T) * S * N(d1) - e**(-rd * T) * K * N(d2)		# Call
		P = e**(-rd * T) * K * N(-d2) - e**(-rf * T) * S * N(-d1)	# Put
		return [C, P]

	def delta(self, S, K, rd, rf, o, T):
		'''Option Delta

		Arguments:
		S: Underlying Price
		K: Strike Price
		rd: Domestic Interest Rate
		rf: Foreign Interest Rate
		o: Volatility
		T: Nb of Days to Maturity

		Returns [Call delta, Put delta]
		'''
		[S, rd, rf, o, T] = prepArgs(S, rd, rf, o, T)
	
		a = o * T**0.5
		d1 = (log(S/K) + (rd - rf + (o**2)/2) * T) / a
		b = e**-(rf*T)
		C = N(d1) * b
		P = -N(-d1) * b
		return [C, P]

	# Implied Volatility
	# S: underlying price, K: strike, rd: domestic interest rate, rf: Foreign interest rate, p: option price, T: nb of days to maturity
	def vol(self, S, K, rd, rf, p, T):
		'''Returns the implied volatility for a given option price'''
		return solve(self.price, [S, K, rd, rf, 0, T], -2, p, high=50.0, low=0.0)

class BS:
	'''Black-Scholes'''
	# S: underlying price, K: strike, r: interest rate, o: volatility, T: nb of days to maturity
	def price(self, S, K, r, o, T):
		'''Returns the option price: [Call price, Put price]'''
		[S, r, rf, o, T] = prepArgs(S, r, 0, o, T)

		a = o * T**0.5
		d1 = (log(S/K) + (r + (o**2)/2) * T) / a
		d2 = (log(S/K) + (r - (o**2)/2) * T) / a
		#d2 = d1 - a
		#C = S * N(d1) - e**(-r * T) * K * N(d2)
		C = S * N(d1) - K * e**(-r * T) * N(d2)
		#P = e**(-r * T) * K * N(-d2) - S * N(-d1)
		P = K * e**(-r * T) * N(-d2) - S * N(-d1)
		#return [round(C,4), round(P,4)]
		return [C, P]

	def vol(self, S, K, r, p, T):
		'''Returns the implied volatility for a given option price'''
		return solve(self.price, [S, K, r, 0, T], -2, p, high=50.0, low=0.0)
