#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Get and analyze the package dependency graph for Ubuntu packages.

It investigate the degree distribution and the clustering coefficient
distribution as the function of the degree.

"""

from __future__ import division
    
import pylab
import random
from time import localtime, time
from math import sqrt

powerlaw = lambda x, exponent, amplitude: amplitude * (x ** exponent)

def fit_powerlaw(x, y):
    """Return with exponent and the *a* coefficient of the power.
    
    powerlaw_function(x) = amplitude * x ** exponent
    
    >> fit_powerlaw([1,2,3], [1,4,9])
    exponent 2.000000, amplitude=1.000000
    >> fit_powerlaw([1,2,3], [5,20,45])
    exponent 2.000000, amplitude=5.000000
    >> fit_powerlaw([1,2,3], [24, 12, 8])
    exponent -1.000000, amplitude=24.000000

    """
    from scipy import optimize
    
    for i in x:
	if i == 0:
	    raise ValueError, "There is zero value in x"
    for i in y:
	if i == 0:
	    raise ValueError, "There is zero value in y"
	
    logx = pylab.log10(x)
    logy = pylab.log10(y)
    
    fitfunc = lambda p, x: p[0] + p[1] * x
    errfunc = lambda p, x, y: y-fitfunc(p, x)
    pinit = [0, -1]
    out = optimize.leastsq(errfunc, pinit, args=(logx, logy),
                  full_output=False)

    p_final = out[0]
    exponent = p_final[1]
    amplitude = 10**p_final[0]
    print "exponent %f, amplitude=%f" % (exponent, amplitude)
    return exponent, amplitude

def degree_distribution_from_degrees(degrees, savefig_file=None, savehist_file=None,direction=None, draw=False):
    """From the list of degrees of nodes it draw the loglog graph of
    the degree distribution. If savefig_file is given, it save into
    image as well."""
    
    #TODO: get out the save part

    degrees.sort()
    max_deg = degrees[-1]
    min_deg = degrees[0]
    hist = [degrees.count(i) for i in range(max_deg +1)]
    
    # An other histogram that is most appropriate for high x, I think
    hist_ = list(enumerate(hist))
    xmin0 =   [ x for (x,y) in hist_ if y == 0 ][0]
    hist_x = [ x for (x,y) in hist_ if y > 0 ]
    hist_y = [ y for (x,y) in hist_ if y > 0 ]
    hist_y0 = hist_y[:]
    del hist_
    
    x_lower = hist_x[xmin0-1] + 0.5
    for i in range(xmin0, len(hist_y)-1):  #????
	x_upper = sqrt(hist_x[i] * hist_x[i+1])
	hist_y[i] /= (x_upper - x_lower)
	x_lower = x_upper
    x_upper = hist_x[-1]** 2 / x_lower
    hist_y[-1] /= (x_upper - x_lower)
	
    exponent, a = fit_powerlaw(hist_x[:], hist_y[:])
    if draw:
	pylab.loglog(range(min_deg, max_deg+1), hist[min_deg:], "b+",
	    label="Degree distribution")
	pylab.loglog(hist_x, hist_y, "rx", hold = True)
	power_y = a*hist_x**exponent
	pylab.loglog(hist_x[1:], power_y[1:], "r--", hold = True)
	ytxt = "Number of nodes with %sdegree = %s" 
	if direction in [None, 'in_out']:
	    xtxt = "$k$"
	    ytxt = ytxt % ("", xtxt)
	elif direction in ['in', 'out']:
	    xtxt = "$k_{%s}$" % direction
	    ytxt = ytxt % (direction + '-', xtxt)
	pylab.ylabel(ytxt)
	pylab.xlabel( xtxt)
	if savefig_file is not None:
	    print _(" I will save file %s.") % savefig_file
	    pylab.savefig(savefig_file)
    if savehist_file is not None:
	print _(" I will save file %s.") % savehist_file
	f = open(savehist_file, 'a')
	f.writelines( ['\n\n',
		       ("%d-%2d-%2d\n" % localtime()[:3]),
		       "degree, corrected_number, original_number\n"]+
		       ["%6d %18.8f %8d\n" % zip_ for  zip_ in zip(hist_x, hist_y, hist_y0)])
	f.close()
	
    if draw:
	pylab.show()

    return exponent
    
if __name__ == "__main__":
    exponents = []
    for i in range(100):
	len_ = 500
	x=pylab.arange(1,len_+1, dtype="float")
	xx = x**(-0.6)
	degrees=[]
	for i in range(len(x)):
	    limit = random.random()
	    if xx[i] > limit:
		degrees.append(int(x[i]))
	print degrees
	#pylab.plot(xx, '.')
	#pylab.show()
	exponent = degree_distribution_from_degrees(degrees, savefig_file=None, savehist_file=None,direction=None)
	print exponent,

