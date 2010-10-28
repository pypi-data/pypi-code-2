"""This makes a little 'star' of error bars, using pylab/matplotlib.
"""

import math

import pylab
import matplotlib

Grey = (0.7,0.7,0.7)

class errorbar_maker(object):
	"""This is a class that makes error bars, tilted at various angles."""

	def __init__(self, cx, cy, n, **kwargs):
		self.cx = cx
		self.cy = cy
		self.n = n
		self.kwargs = {'marker': 'o', 'linestyle': '-',
				'mec': 'r', 'color': 'k', 'zorder': 2
				}
		self.kwargs.update(kwargs)
	

	def make(self, i, xl, xc, xh, **kwargs):
		kwa = self.kwargs.copy()
		kwa.update(kwargs)
		assert xl <= xc <= xh
		theta = (math.pi/2.0) * (1 + (i-0.5*(self.n-1))/float(self.n))
		W = 0.12*(abs(xl)+abs(xh))/float(self.n)
		w = kwa.get('w', W)
		x1, y1 = self._xf(theta, (xl, 0.0), (xh, 0.0))
		x2, y2 = self._xf(theta, (xl, -w), (xl, w))
		x3, y3 = self._xf(theta, (xh, -w), (xh, w))
		if (xl>0)==(xh>0):
			zo = 2
		else:
			mcolor = kwa.get('mucolor', Grey)
			color = kwa.get('lucolor', Grey)
			zo = 1
		zorder = kwa['zorder']
		mcolor = kwa['mec']
		color = kwa['color']
		linestyle = kwa['linestyle']
		pylab.plot(x1, y1, linestyle=linestyle, color=color, zorder=zorder)
		pylab.plot(x2, y2, linestyle=linestyle, color=color, zorder=zorder)
		pylab.plot(x3, y3, linestyle=linestyle, color=color, zorder=zorder)
		if min(xl, xh) > 0.0:
			x5, y5 = self._xf(theta, (0.0, 0.0), (min(xl, xh), 0.0))
			pylab.plot(x5, y5, linestyle=':', color=color, zorder=100)
		if max(xl, xh) < 0.0:
			x5, y5 = self._xf(theta, (0.0, 0.0), (max(xl, xh), 0.0))
			pylab.plot(x5, y5, linestyle=':', color=color, zorder=100)
		x4, y4 = self._xf(theta, (xc, 0))
		pylab.plot(x4, y4, marker=kwa['marker'], linestyle='', mec=mcolor, mew=0.0,
				color=mcolor, zorder=zorder)


	def _xf(self, theta, *xy):
		ox = []
		oy = []
		for (x,y) in xy:
			xx = self.cx + math.cos(theta)*x - math.sin(theta)*y
			yy = self.cy + math.sin(theta)*x + math.cos(theta)*y
			ox.append(xx)
			oy.append(yy)
		return (ox, oy)



def grey_out(c):
	r, g, b = matplotlib.colors.colorConverter.to_rgb(c)
	return (0.2*r+0.6, 0.2*g+0.6, 0.2*b+0.6)



class errorbar(object):
	def __init__(self, l, c, h, dim=False, sortorder=None, **kwargs):
		self.l = l
		self.c = c
		self.h = h
		self.dim = dim
		self.order = sortorder
		self.kwargs = kwargs

	def __mul__(self, other):
		return errorbar(self.l*other, self.c*other, self.h*other, self.dim, **(self.kwargs))

	def __cmp__(self, other):
		return cmp(self.order, other.order)


def star(cx, cy, lch, lcolormap=None, mcolormap=None, dimmer=grey_out, **kwargs):
	"""This makes a star of error bars.
	@param cx: x-coordinate of the star center
	@param cy: y-coordinate of the star center
	@param lch: list of error bars to create about the center.
	@type lch: list(errorbar).
	"""
	e = errorbar_maker(cx, cy, len(lch), **kwargs)
	for (i, ebar) in enumerate(lch):
		kwa = {}
		if lcolormap is not None:
			kwa['color'] = lcolormap[i]
		elif mcolormap is not None:
			kwa['color'] = mcolormap[i]
		if mcolormap is not None:
			kwa['mec'] = mcolormap[i]
		elif lcolormap is not None:
			kwa['mec'] = lcolormap[i]
		kwa.update(ebar.kwargs)
		if ebar.dim:
			kwa['color'] = dimmer(kwa['color'])
			kwa['mec'] = dimmer(kwa['mec'])
			kwa['zorder'] = 1
		e.make(i, ebar.l, ebar.c, ebar.h, **kwa)
	# pylab.plot([cx], [cy], 'ro')


def plot(xlch, **kwargs):
	assert xlch
	sz = 0.0
	n = 0
	dx = 0.0
	xlast = None
	for (x, llch) in xlch:
		for lch in llch:
			if lch is not None:
				sz += max(abs(lch.l), abs(lch.h))**2
				n += 1
			if xlast is not None:
				dx += abs(x-xlast)
			xlast = x
	if n == 0:
		return
	f = 0.5*(dx/(len(xlch)-1))/math.sqrt(sz/float(n))
	for (x, llch) in xlch:
		star(x, 0.0,
			[lch*f for lch in llch if lch is not None ],
			 **kwargs)


if __name__ == '__main__':
	plot( [(0.0, [errorbar(0, 1, 2), errorbar(0, 2, 3), errorbar(0, 2, 3), errorbar(0, 1, 2)]),
		(1.0, [errorbar(0, 1, 2), errorbar(1, 2, 3), errorbar(1, 2, 3), errorbar(0, 1, 2)]),
		(2.0, [errorbar(-1, 1, 2, dim=True), errorbar(-1, 0, 1, dim=True), errorbar(-1, -0.5, 0), errorbar(-1, -0.5, -0.25)])
		],
		lcolormap = ['r', 'g', 'b', 'c', 'm', 'k']
		)
	pylab.show()
