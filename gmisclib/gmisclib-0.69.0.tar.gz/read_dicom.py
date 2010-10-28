#!/usr/bin/env python

import g_exec
import re
import Num


def _rm_bkt(s):
	s = s.strip()
	if s.startswith('[') and s.endswith(']'):
		return s[1:-1]
	return s

def _sq(s):
	return ''.join( [ q.capitalize() for q in s.split() ] )
	

def read_header(f):
	pass1 = re.compile(r'[(]([0-9a-fA-F]+),([0-9a-fA-F]+)[)]\s+[A-Z]+.[0-9].\s+([a-zA-Z0-9_]+):\s*(.*)\s*[(]\s*[0-9]+ bytes\s*[)]$')
	pass2gel = re.compile(r'([a-zA-Z0-9_]+)\s+[(][0-9]+[)]:\s*([x0-9a-fA-F]+)')
	pass2e = re.compile(r'(.*)\s*:\s*(.*)')
	gnpat = re.compile(r'(.*)\s+-\s+Group\s+([x0-9a-fA-F]+)')
	defer = {}
	gnames = {}
	caught = set()
	ipass = 0
	lip = 0
	p2g = None
	p2e = None
	gname = None
	for s in g_exec.getiter_raw('medcon', ['medcon', '-f', f]):
		s = s.rstrip()

		# print '#', s
		if s.startswith('Pass #1: through DICOM reader'):
			ipass = 1
			continue
		elif s.startswith('Pass #2: through Acr/Nema reader'):
			ipass = 2
			continue
		elif gnpat.match(s):
			m = gnpat.match(s)
			gname = m.group(1)
			gnames[ int(m.group(2),16) ] = gname
			continue

		if ipass == 1:
			m = pass1.match(s)
			if not m:
				continue
			k1, k2, k, v = m.groups()
			if k != 'Unknown':
				caught.add( (int(k1,16), int(k2,16)) )
				yield (k, _rm_bkt(v))
			else:
				defer[ (int(k1,16),int(k2,16)) ] = _rm_bkt(v)
		elif ipass == 2:
			if s.startswith('----'):
				continue
			m = pass2gel.match(s)
			if m:
				if m.group(1) == 'Group':
					p2g = m.group(2)
				elif m.group(1) == 'Element':
					p2e = m.group(2)
				lip += 1
				continue
			m = pass2e.match(s)
			if not m:
				continue
			if p2g is None or p2e is None:
				continue
			k1 = int(p2g, 16)
			k2 = int(p2e, 16)
			if (k1, k2) in caught:
				continue
			k, v = m.groups()
			if v.strip() == '<not printed>':
				continue
			if k.strip() == 'Unknown Element':
				continue
			if (k1,k2) in defer:
				del defer[ (k1,k2) ]
			caught.add( (k1, k2) )
			p2g = None
			p2e = None
			yield (_sq(gname) + '.' + _sq(k), v)
	for ((k1,k2),v) in defer.items():
		if k1 in gnames:
			yield ('%s.%#x' % (_sq(gnames[k1]),k2), v)
		else:
			yield ('CODE%#x.%#x' % (k1,k2), v)


class img_with_mx(object):
	"""This is a way of reading in a 2-D image when you don't
	know the final size.   It keeps a larger image around
	and keeps track of the area that has been set.
	"""

	def __init__(self, i, j):
		"""Create an image that contains pixel (i,j)."""
		assert i>=0 and j>=0
		self.img = Num.zeros((2*i+1,2*j+1), Num.Float)
		self.mi = i
		self.mj = j

	def resize(self, inxt, jnxt):
		tmp = Num.zeros((inxt,jnxt), Num.Float)
		tmp[:self.mi+1, :self.mj+1] = self.img[:self.mi+1, :self.mj+1]
		self.img = tmp

	def set(self, i, j, val):
		"""Set a pixel, expanding the allocated space as needed."""
		assert i>=0 and j>=0

		try:
			self.img[i,j] = val
		except IndexError:
			if i >= self.img.shape[0]:
				inxt = 2*i+2
			else:
				inxt = max(i, self.mi) + 1
	
			if j >= self.img.shape[1]:
				jnxt = 2*j+2
			else:
				jnxt = max(j, self.mj) + 1
			self.img.resize(inxt, jnxt)
			self.img[i,j] = val

		if i > self.mi:
			self.mi = i
		if j > self.mj:
			self.mj = j

	def get(self):
		"""Get the image, trimming it to show
		the area that has been set.
		"""
		return self.img[self.mi:0:-1, :self.mj]


def _set(imgs, iimg, i, j, val):
	assert i>=0 and j>=0
	try:
		img = imgs[iimg]
	except KeyError:
		img = img_with_mx(i, j)
		imgs[iimg] = img
	img.set(i, j, val)


def read_body(f):
	pix = re.compile('\s*P[(]\s*([0-9]+),\s*([0-9]+)\s*[)]')
	imgs = {}
	for s in g_exec.getiter_raw('medcon', ['medcon', '-pa', '-f', f]):
		if not s.startswith('#'):
			# print 'Not hash', s
			continue
		a = s.split(':')
		if len(a) != 8:
			# print 'Not 8:', s
			continue
		assert a[0] == '#' and a[2]=='S' and a[4]=='I'
		m = pix.match(a[6])
		assert m
		i = int(m.group(1)) - 1
		j = int(m.group(2)) - 1
		iimg = int(a[1]) - 1
		sl = float(a[3])
		intercept = float(a[5])
		val = sl*float(a[7]) + intercept
		_set(imgs, iimg, j, i, val)
	o = []
	imgl = imgs.items()
	imgl.sort()
	for (j,img) in imgl:
		o.append(img.get())
	return o


def read_imgs(f):
	import gpkimgclass
	h = dict(read_header(f))
	b = read_body(f)
	return [gpkimgclass.gpk_img(h.copy(), bi) for bi in b]

if __name__ == '__main__':
	import sys
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass
	arglist = sys.argv[1:]
	if arglist[0] == '-o':
		arglist.pop(0)
		o = arglist.pop(0)
		tmp = read_imgs(arglist[0])
		assert len(tmp) == 1
		tmp[0].write(o)
	else:
		for (k,v) in read_header(arglist[0]):
			print '%s = %s' % (k, v)
