# Copyright (c) 1999-2000 Gary Strangman; All Rights Reserved.
#
# This software is distributable under the terms of the GNU
# General Public License (GPL) v2, the text of which can be found at
# http://www.gnu.org/copyleft/gpl.html. Installing, importing or otherwise
# using this module constitutes acceptance of the terms of this License.
#
# Disclaimer
# 
# This software is provided "as-is".  There are no expressed or implied
# warranties of any kind, including, but not limited to, the warranties
# of merchantability and fittness for a given application.  In no event
# shall Gary Strangman be liable for any direct, indirect, incidental,
# special, exemplary or consequential damages (including, but not limited
# to, loss of use, data or profits, or business interruption) however
# caused and on any theory of liability, whether in contract, strict
# liability or tort (including negligence or otherwise) arising in any way
# out of the use of this software, even if advised of the possibility of
# such damage.
#
# Comments and/or additions are welcome (send e-mail to:
# strang@nmr.mgh.harvard.edu).
# 
import math
import numpy as N

def fprob (dfnum, dfden, F):
    """
Returns the (1-tailed) significance level (p-value) of an F
statistic given the degrees of freedom for the numerator (dfR-dfF) and
the degrees of freedom for the denominator (dfF).

Usage:   lfprob(dfnum, dfden, F)   where usually dfnum=dfbn, dfden=dfwn
"""
    p = betai(0.5*dfden, 0.5*dfnum, dfden/float(dfden+dfnum*F))
    return p


def betai(a,b,x):
    """Returns the incomplete beta function::

	I-sub-x(a,b) = 1/B(a,b)*(Integral(0,x) of t^(a-1)(1-t)^(b-1) dt)

	where a,b>0 and B(a,b) = G(a)*G(b)/(G(a+b)) where G(a) is the gamma
	function of a.  The continued fraction formulation is implemented here,
	using the betacf function.  (Adapted from: Numerical Recipies in C.)

	Usage:   lbetai(a,b,x)
"""
    if (x<0.0 or x>1.0):
        raise ValueError, 'Bad x in lbetai'
    if (x==0.0 or x==1.0):
        bt = 0.0
    else:
        bt = math.exp(gammln(a+b)-gammln(a)-gammln(b)+a*math.log(x)+b*
                      math.log(1.0-x))
    if (x<(a+1.0)/(a+b+2.0)):
        return bt*betacf(a,b,x)/float(a)
    else:
        return 1.0-bt*betacf(b,a,1.0-x)/float(b)




def betacf(a,b,x):
    """
This function evaluates the continued fraction form of the incomplete
Beta function, betai.  (Adapted from: Numerical Recipies in C.)

Usage:   lbetacf(a,b,x)
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
    print 'a or b too big, or ITMAX too small in Betacf.'


def gammln(xx):
    """Returns the gamma function of xx.
	Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.
	(Adapted from: Numerical Recipies in C.)
	@param xx: float
	@rtype: float
	"""

    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
             0.120858003e-2, -0.536382e-5]
    x = xx - 1.0
    tmp = x + 5.5
    tmp = tmp - (x+0.5)*math.log(tmp)
    ser = 1.0
    for j in range(len(coeff)):
        x = x + 1
        ser = ser + coeff[j]/x
    return -tmp + math.log(2.50662827465*ser)


def agammln(xx):
    """Returns the gamma function of xx.
    C{Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt}.
    Adapted from: Numerical Recipies in C.  Can handle multiple dims ... but
    probably doesn't normally have to.

    Usage:   agammln(xx)
    """
    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
             0.120858003e-2, -0.536382e-5]
    x = xx - 1.0
    tmp = x + 5.5
    tmp = tmp - (x+0.5)*N.log(tmp)
    ser = 1.0
    for j in range(len(coeff)):
        x = x + 1
        ser = ser + coeff[j]/x
    return -tmp + N.log(2.50662827465*ser)

