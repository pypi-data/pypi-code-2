#!/usr/bin/env python


import g_pipe
import math


IB = 0.7

def addcurve( xyee, x_range, y_range, bexp, brms, imopfd, xsz, ysz ):
	if len(xyee) == 0:
		return
	xmin, xmax = x_range
	sx = xsz/float(xmax - xmin)
	ymin, ymax = y_range
	sy = ysz/float(ymax - ymin)
	bs2 = 0.0
	for (x, y, ex, ey, wt) in xyee:
		iex = math.hypot(ex*sx, IB)
		iey = math.hypot(ey*sy, IB)
		area = iex*iey
		b = wt * area**(-bexp)
		bs2 += b*b
	if not ( bs2 > 0.0):
		return
	bfac = brms / math.sqrt(bs2/len(xyee))
	for (x, y, ex, ey, wt) in xyee:
		iex = math.hypot(ex*sx, IB)
		iey = math.hypot(ey*sy, IB)
		area = iex*iey
		b = bfac * wt * area**(-bexp)
		xscaled = (x-xmin)*sx
		yscaled = (y-ymin)*sy
		r = math.sqrt(iex * iey)
		ecc = math.sqrt(1 - min(iex, iey)/max(iex, iey))
		pa = 90
		if abs(iey) < abs(iex):
			pa = 0
		imopfd.writelines('%.2f %.2f %.3f %g %g %d addGaussGal\n'
					% (xscaled, yscaled, b, r, ecc, pa))
		# imopfd.flush()




if __name__ == '__main__':
	H = 600
	W = 900
	si, so = g_pipe.popen2("imop", ['imop', '-write16', '-stdin' ])
	x_range = (0, 1)
	y_range = (0, 1)
	xyee = []
	for i in range(10):
		x = 0.1*i
		y = x - 2*x*x*x + 2*x*x*x*x*x
		ex = 0.05 - 0.02*x
		ey = 0.01 + 0.1*y
		xyee.append( (x, y, ex, ey, 1.0) )
	si.writelines('%d %d alloc\n' % (H, W))
	addcurve(xyee, x_range, y_range, 0.5, 200, si, W, H)
	si.writelines('= foo.fits')
	si.close()
	so.close()
