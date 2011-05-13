#!/usr/bin/env python
"""
You can control the axis tick and grid properties
"""
import pylab
import sys
import Num

def plot_oneaxis(dlist):
	"""dlist is a list  of (label, (ctr, uerr, derr))."""
	pylab.figure()
	ax = pylab.subplot(111)
	ax.set_yticks( [ pos[0] for (lab,pos) in dlist ] )
	ax.set_yticklabels( [ lab for (lab,pos) in dlist ] )
	ax.set_xticks( [] )
	ax.set_xticklabels( [] )
	regions = []
	y = []
	err = []
	x = []
	for (lab, (ctr, uerr, derr)) in dlist:
		y.append(ctr)
		err.append((derr,uerr))
		xj = 0.5
		for (l,h,xi) in regions:
			if l <= ctr <= h:
				xj += 1
		regions.append((ctr-1.3*derr, ctr+1.3*uerr, xj))
		x.append(xj)
	pylab.errorbar(x=Num.array(x), y=Num.array(y),
				yerr=Num.array(err)
				)





if __name__ == '__main__':
	(d,c,x) = process(sys.stdin)

	plot_oneaxis(dlist)
	pylab.show()
