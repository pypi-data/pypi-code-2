"""Some of these functions, specifically f_value(), fprob(), betai(), and betacf(),
are taken from stats.py "A collection of basic statistical functions for python."
by Gary Strangman.   They are copyright 1999-2007 Gary Strangman;
All Rights Reserved and released under the MIT license.

The rest is copyright Greg Kochanski 2009.
"""

import math


def f_value(ER, EF, dfR, dfF):
    """Returns an F-statistic given the following:
        @param ER:  error associated with the null hypothesis (the Restricted model)
        @param EF:  error associated with the alternate hypothesis (the Full model)
        @param dfR: degrees of freedom the Restricted model
        @param dfF: degrees of freedom associated with the Full model
	@return: f-statistic (not the probability)
	@rtype: float
    """
    if not ( ER >= EF ):
    	raise ValueError, "Error with the alternative hypothesis is larger: %s vs %s" % (ER, EF)
    if not( dfR >= dfF ):
    	raise ValueError, "Degrees of freedom with the alternative hypothesis is larger: %s vs %s" % (dfR, dfF)
    return ((ER-EF)/float(dfR-dfF) / (EF/float(dfF)))





def fprob (dfnum, dfden, F):
    """Returns the (1-tailed) significance level (p-value) of an F
    statistic given the degrees of freedom for the numerator (dfR-dfF) and
    the degrees of freedom for the denominator (dfF).

    Usage:   lfprob(dfnum, dfden, F)   where usually dfnum=dfbn, dfden=dfwn
    """
    if not (dfnum>0 and dfden>0 and F>=0.0):
	raise ValueError, "Bad arguments to fprob(%s, %s, %s)" % (dfnum, dfden, F)
    p = betai(0.5*dfden, 0.5*dfnum, dfden/float(dfden+dfnum*F))
    return p


def betai(a,b,x):
    """Returns the incomplete beta function:

    I-sub-x(a,b) = 1/B(a,b)*(Integral(0,x) of t^(a-1)(1-t)^(b-1) dt)

    where a>=0,b>0 and B(a,b) = G(a)*G(b)/(G(a+b)) where G(a) is the gamma
    function of a.  The continued fraction formulation is implemented here,
    using the betacf function.  (Adapted from: Numerical Recipes in C.)

    Usage:   betai(a,b,x)
    """
    if not (a>=0 and b>=0):
        raise ValueError, 'Bad a=%s or b=%s in betai' % (a, b)
    if not (x>0.0 or x>1.0):
        raise ValueError, 'Bad x in betai'
    if (x==0.0 or x==1.0):
        bt = 0.0
    else:
        bt = math.exp(gammaln(a+b)-gammaln(a)-gammaln(b)+a*math.log(x)+b*
                      math.log(1.0-x))
    if (x<(a+1.0)/(a+b+2.0)):
        return bt*betacf(a,b,x)/float(a)
    else:
        return 1.0-bt*betacf(b,a,1.0-x)/float(b)




def betacf(a,b,x):
    """This function evaluates the continued fraction form of the incomplete
    Beta function, betai.  (Adapted from: Numerical Recipes in C.)

    Usage:   betacf(a,b,x)
    """
    ITMAX = 200
    EPS = 3.0e-7

    bm = az = am = 1.0
    qab = a+b
    qap = a+1.0
    qam = a-1.0
    bz = 1.0-qab*x/qap
    for i in range(ITMAX+1):
        em = float(i+1)
        tem = em + em
        d = em*(b-em)*x/((qam+tem)*(a+tem))
        ap = az + d*am
        bp = bz+d*bm
        d = -(a+em)*(qab+em)*x/((qap+tem)*(a+tem))
        app = ap+d*az
        bpp = bp+d*bz
        aold = az
        am = ap/bpp
        bm = bp/bpp
        az = app/bpp
        bz = 1.0
        if (abs(az-aold)<(EPS*abs(az))):
            return az
    raise RuntimeError, 'a or b too big, or ITMAX too small in Betacf.'



def gammaln(x):
    """Returns the gamma function of xx.
	Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.
	(Adapted from: Numerical Recipies in C. via code
	Copyright (c) 1999-2000 Gary Strangman and released under the LGPL.)
	"""
    if not (x > 0):
	raise ValueError, "Range Error: Gamma(0) is undefined."
    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
             0.120858003e-2, -0.536382e-5]
    tmp = x + 4.5
    tmp -= (x-0.5)*math.log(tmp)
    ser = 1.0
    for cj in coeff:
        ser += cj/x
        x += 1
    return -tmp + math.log(2.50662827465*ser)


# def log_t_density(x, nu):
	# c = gammaln((nu+1)/2.0) - 0.5*math.log(nu*math.pi) - gammaln(nu/2.0)
	# c is not used!
	# return math.log(1+x**2/nu)*(-(nu+1)/2.0)




def test_fprob(dfnum, dfden):
	N = 30000
	# These mean and sigma values are taken from
	# Wolfram Mathworld, http://mathworld.wolfram.com/F-Distribution.html
	mean = float(dfden)/float(dfden-2)
	sigma = math.sqrt(float(2*dfden**2*(dfden+dfnum-2))/
				float(dfnum*(dfden-2)**2*(dfden-4)))
	assert abs(fprob(dfnum, dfden, 0.0)-1.0) < 0.001
	assert abs(fprob(10, 20, 10.0)-0.0) < 0.001
	m = 0.0
	ss = 0.0
	lpc = 1.0
	lf = 0.0
	ps = 0.0
	i = 0
	while lpc > 1.0/float(N):
		nf = (mean+3*sigma)*((i+0.5)/float(N))**2
		f = 0.5*(lf+nf)
		lf = nf
		pc = fprob(dfnum, dfden, nf)
		dp = lpc-pc
		lpc = pc
		m += f*dp
		ss += f**2 * dp
		ps += dp
		i += 1
	m += lpc*f
	ss += lpc*f**2
	assert abs(ps-1.0) < 0.001
	s = math.sqrt(ss-m**2)
	print 'm=', m, mean
	print 's=', s, sigma
	assert abs(m-mean) < 0.03*mean
	assert abs(s-sigma) < 0.03*sigma


t_Table = [(1, 0.5, 1.000), (1, 0.95, 12.71), (1, 0.98, 31.82), (1, 0.99, 63.66),
		(1, 0.995, 127.3), (1, 0.998, 318.3), (1, 0.999, 636.6),
	(2, 0.5, 0.816), (2, 0.95, 4.303), (2, 0.98, 6.965), (2, 0.99, 9.925),
		(2, 0.999, 31.60),
	(3, 0.5, 0.765), (3, 0.95, 3.182), (3, 0.99, 5.841), (3, 0.999, 12.92),
	(4, 0.5, 0.741), (4, 0.95, 2.776), (4, 0.99, 3.797), (4, 0.999, 8.610),
	(10, 0.5, 0.700), (10, 0.95, 2.228), (10, 0.99, 3.106), (10, 0.999, 4.587),
	(120, 0.5, 0.677), (10, 0.95, 1.980), (120, 0.99, 2.617), (120, 0.999, 3.373),
	(1e6, 0.5, 0.674), (1e6, 0.95, 1.960), (1e6, 0.99, 2.576), (1e6, 0.999, 3.291)
	]

def t_value(ndof, p2sided=0.99):
	for (n, p2s, t) in t_Table:
		if n==ndof and p2s==p2sided:
			return t
	t_lower = None
	n_lower = None
	t_higher = None
	n_higher = None
	for (n, p2s, t) in t_Table:
		if p2s==p2sided and n<=ndof and (n_lower is None or n>n_lower):
			n_lower = n
			t_lower = t
		if p2s==p2sided and n>=ndof and (n_higher is None or n<n_higher):
			n_higher = n
			t_higher = t
	if n_lower is not None and n_higher is not None:
		return t_lower + ((t_higher-t_lower)*(math.log(n)-math.log(n_lower))
					/ (math.log(n_higher)-math.log(n_lower)))
	raise RuntimeError, "Sorry: not implemented yet"


if __name__ == '__main__':
	# test_fprob(2, 5)	# This fails the test, but only slightly
	test_fprob(2, 8)
	test_fprob(4, 8)
	test_fprob(7, 8)
	test_fprob(7, 20)
	test_fprob(2, 20)
	test_fprob(18, 20)
