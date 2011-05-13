#!/usr/bin/env python

import Num
import math


class boxc(object):
	def __init__(self, xc, yc, xw, yw):
		self._xc = xc
		self._yc = yc
		self._xw = xw
		self._yw = yw
	
	def xmin(self):
		return self._xc - self._xw/2.0

	def xmax(self):
		return self._xc + self._xw/2.0

	def ymin(self):
		return self._yc - self._yw/2.0

	def ymax(self):
		return self._yc + self._yw/2.0
	
	def w(self):
		return self._xw
	
	def h(self):
		return self._yw

	def yc(self):
		return self._yc

	def xc(self):
		return self._xc

	def shift(self, x, y):
		return boxc(self._xc+x, self._yc+y, self._xw, self._yw)


class text_template(object):
	def __init__(self, text, H, W):
		"""(0,0) is the lower left corner of the block of text."""
		self.lines = []
		self.txt = []
		la = text.split('\n')
		n = len(la)
		for (i, l) in enumerate(la):
			self.addline(0.0, H*(n-1-i), W*len(l), H, l)
	
	def addline(self, x0, y0, xlength, yht, txtline):
		"""Specify LLC."""
		self.lines.append(boxc(x0+xlength/2.0, y0+yht/2.0,
					xlength, yht)
					)
		self.txt.append(txtline)

	def nlines(self):
		return len(self.lines)


def Gauss(y, ybar, yvar):
	arg = (y-ybar)**2/(2*yvar)
	return Num.exp(-Num.minimum(arg, 100.0))/math.sqrt(2*math.pi*yvar)

def gauss(y, ybar, yvar):
	arg = (y-ybar)**2/(2*yvar)
	return math.exp(-arg)/math.sqrt(2*math.pi*yvar)

def q_gauss(y, ybar, yvar):
	return gauss(y, ybar, yvar) - 0.3*gauss(y, ybar, 40*yvar)
	


class viewport(boxc):
	def __init__(self, fracCharHt, fracCharW, xmin, xmax, ymin, ymax):
		self.H = fracCharHt
		self.W = fracCharW
		self.datasets = []
		self.avoidlist = []
		boxc.__init__(self, xmin, ymin, xmax-xmin, ymax-ymin)
		self.YN = 100
		self.DF = 10.0
	

	def dataset(self, x, y):
		self.datasets.append( (x, y) )


	def _fom_y(self, ycand, x0, relbox):
		rlist = []
		xtra_var = self.h()**2 * ((1.0/self.YN)**2 + self.H**2)
		xbdr = self.h() * self.H
		for (x, y) in self.datasets :
			ovlap = Num.greater(x, x0+relbox.xmin()-xbdr) * Num.less(x, x0+relbox.xmax()+xbdr)
			avoid = Num.compress(ovlap, y)
			an = avoid.shape[0]
			if an > 1:
				asum = Num.sum(avoid, axis=0)
				assq = Num.sum((avoid-asum/an)**2, axis=0)
				assq += an * xtra_var
				# Avoid the data in the relevant x-range:
				rlist.append( (asum/an, assq/an, -self.DF) )
				# But be nearby:
				rlist.append( (asum/an, 100.0*assq/an, 0.1*self.DF) )
	
			rn = y.shape[0]
			if rn > 1:
				rsum = Num.sum(y, axis=0)
				rssq = Num.sum((y-rsum/rn)**2, axis=0)
				rssq += rn * xtra_var
				# Also be near the overall dataset
				rlist.append( (rsum/rn, 2*rssq/rn, 0.1*self.DF) )

		for a in self.avoidlist:
			veff = relbox.w()**2 + a.w()**2
			wt = q_gauss(x0+relbox.xc(), a.xc(), veff)
			rlist.append( (a.yc(), a.h()**2, -wt) )

		fom = Num.zeros(ycand.shape, Num.Float)
		yco = ycand + relbox.ymin()
		for (rbar, rvar, wt) in rlist:
			fom += wt*Gauss(yco, rbar, rvar+relbox.h()**2)
		return fom
	
	def find_y(self, x0, ttm):
		"""Figures out a good place to put a label.
		The label is at a specified tc, but can be at any vertical
		position.   This finds a good vertical position.
		Returns the bottom of the block of text.
		"""
		delta = self.h()/self.YN
		y_candidates = (Num.arrayrange(self.YN)-(0.5*self.YN))*delta + self.yc()
		fom = Num.zeros(y_candidates.shape, Num.Float)
		for lbox in ttm.lines:
			tmp = self._fom_y(y_candidates, x0, lbox)
			Num.add(fom, tmp, fom)
		return y_candidates[Num.argmax(fom)]


	def textplace(self, x0, text):
		tt = text_template(text, self.H*self.h(), self.W*self.w())
		yc = self.find_y( x0, tt )
		for (l, bx) in zip(tt.txt, tt.lines):
			bxs = bx.shift(x0, yc)
			self.avoidlist.append(bxs)
			yield (bxs.xmin(), bxs.ymin(), l)
	

	def draw_hor_line(self, xc, yc, w):
		EPS = 0.005
		self.avoidlist.append(boxc(xc, yc, w, EPS*self.h()))

