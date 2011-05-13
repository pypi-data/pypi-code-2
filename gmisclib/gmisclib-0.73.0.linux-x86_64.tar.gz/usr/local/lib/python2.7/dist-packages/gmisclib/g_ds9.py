#!/usr/bin/env python

"""Handles interactions with ds9 (U{http://hea-www.harvard.edu/RD/ds9/}).
Ds9 is an image display and analysis tool commonly used in astrophysics,
but it's good for any kind of greyscale image.

Note: there is an extra, special property Coordsys.   This is not fed to
ds9.  It is merely something that you can use to remember what coordinate
system the regions are in.
"""


import re
import threading
import os
import time
import copy as COPY
from gmisclib import die
from gmisclib import g_exec

COLORS = ('white', 'black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
PLOTSYMS = ('circle', 'diamond', 'plus', 'cross')

class UnknownProperty(KeyError):
	def __init__(self, *s):
		KeyError.__init__(self, *s)


class execwait(object):
	def __init__(self, s):
		self.t = threading.Thread(target=os.system, args=(s,),
						name='execwait: %s' % s
						)
		self.t.start()

	def wait(self):
		self.t.join()


class ds9_io(object):
	def __init__(self, ds9start=None, xpaname='ds9',
				xpaset=['xpaset', ],
				xpaset_p=['xpaset', '-p'],
				xpaget=['xpaget']
				):
		if ds9start is None:
			ds9start = 'ds9'
		self.setap = tuple(xpaset_p) + (xpaname,)
		self.seta = tuple(xpaset) + (xpaname,)
		self.geta = tuple(xpaget) + (xpaname,)
		self.ds9ew = None
		self.debug = 0

		try:
			tmp = self.getall('about')
			if tmp:
				self.closed = False
				return
		except g_exec.ExecError:
			pass

		self.ds9ew = execwait(ds9start)
		sleep = 0.10
		time.sleep(2*sleep)
		while True:
			try:
				tmp = self.getall('about')
				if tmp:
					self.closed = False
					return
			except g_exec.ExecError:
				sleep += 0.1
				time.sleep(sleep)
				


	def set(self, *args):
		tmp = self.setap + tuple(args)
		g_exec.getall(tmp[0], tmp)


	def set_with_input(self, input, *args):
		"""Run the X{xpaset} command and feed it data on its standard input.
		Each element in the input list becomes one line of data
		to C{xpaset}.
		@param input:
		@type input: L{list} or iterator
		@param args: The command line used to execute C{xpaset}.
		@type args: C{[ "xpaset", ...]}
		"""
		tmp = self.seta + tuple(args)
		g_exec.getall(tmp[0], tmp,
				input=[q+'\n' for q in input],
				debug=self.debug)


	def getlast(self, *args):
		return self.getall(*args)[-1]


	def getall(self, *args):
		return list(self.getiter(*args))


	def getiter(self, *args):
		tmp = self.geta + tuple(args)
		for q in g_exec.getiter_raw(tmp[0], tmp):
			yield q.rstrip()


	def close(self):
		if self.ds9ew and not self.closed:
			self.set('quit')
			self.ds9ew.wait()
			self.ds9ew = None
			self.closed = True


	def __del__(self):
		try:
			self.close()
		except g_exec.ExecError:
			# Too late to report an error now.
			# If it doesn't shut down, that's just too bad.
			pass


class BadTagError(ValueError):
	def __init__(self, *args):
		ValueError.__init__(self, *args)


class Region(object):
	def __init__(self, kwargs, coordsys):
		self._props = kwargs
		self._pshared = True
		self.Coordsys = coordsys

	def __str__(self):
		raise RuntimeError, 'Virtual function'
	
	def addprop(self, k, v):
		if self._pshared:
			self._props = self._props.copy()
			self._pshared = False
		self._props[k] = v

	def has_prop(self, k):
		return self._props.has_key(k)

	def getprop(self, *args):
		return self._props.get(*args)


	def props(self):
		o = [ '#' ]
		for (k, v) in self._props.items():
			try:
				pof = PROPout[k]
			except KeyError, x:
				raise UnknownProperty( *(x.args) )
			o.extend( pof(k, v) )
		if len(o) > 1:
			return ' '.join(o)
		return ''


	def chgprops(self, **kwargs):
		if self._pshared:
			self._props = self._props.copy()
			self._pshared = False
		self._props.update(kwargs)
		return self

	def compatible_coord(self, coordsys):
		return (self.Coordsys is None or coordsys is None
			or self.Coordsys == coordsys)



def copy(r, **kwargs):
	"""Copy a region and update some of the keyword
	arguments (e.g. color).   The original object is unchanged,
	and you can copy any subclass of Region.
	"""
	assert isinstance(r, Region)
	tmp = COPY.copy(r)	# Deepcopy?
	tmp.chgprops(**kwargs)
	return tmp


class line(Region):
	def __init__(self, x0, y0, x1, y1, Coordsys=None, **kwargs):
		Region.__init__(self, kwargs, Coordsys)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1

	def __str__(self):
		return 'line %10g %10g %10g %10g %s' % ( self.x0+1, self.y0+1,
						self.x1+1, self.y1+1, self.props() )

	def end(self, whichend):
		if whichend == 0:
			return point(self.x0, self.y0, **self._props)
		elif whichend == 1:
			return point(self.x1, self.y1, **self._props)
		else:
			raise ValueError, "Whichend == 0 or 1"

	def center(self):
		return point(0.5*(self.x0+self.x1), 0.5*(self.y0+self.y1), Coordsys=self.Coordsys)


class circle(Region):
	def __init__(self, x, y, r, Coordsys=None, **kwargs):
		Region.__init__(self, kwargs, Coordsys)
		self.x = x
		self.y = y
		self.r = r

	def __str__(self):
		return 'circle %10g %10g %10g %s' % ( self.x+1, self.y+1, self.r, self.props() )

	def center(self):
		return point(self.x, self.y, Coordsys=self.Coordsys)


class point(Region):
	def __init__(self, x, y, Coordsys=None, **kwargs):
		Region.__init__(self, kwargs, Coordsys)
		self.x = x
		self.y = y

	def __str__(self):
		return 'point %10g %10g %s' % ( self.x+1, self.y+1, self.props() )




class text(Region):
	def __init__(self, x, y, text, Coordsys=None, **kwargs):
		Region.__init__(self, kwargs, Coordsys)
		self.addprop('text', text)
		self.x = x
		self.y =  y
		self.text = text

	def __str__(self):
		return 'text %10g %10g %s' % ( self.x+1, self.y+1, self.props() )


def dequote(s):
	if s.startswith('{') and s.endswith('}'):
		return s[1:-1]
	elif len(s)>1 and s.startswith('"') and s.endswith('"'):
		return s[1:-1]
	elif len(s)>1 and s.startswith("'") and s.endswith("'"):
		return s[1:-1]
	return s



PROPin = {'color': str, 'text': dequote, 'font': dequote,
	'select': int, 'edit': int, 'move': int, 'rotate': int,
	'delete': int, 'fixed': int,
	'line': None, 'tag': None,
	'ruler': int, 'width': int,
	'point': str, 'highlite': int, 'include': int
	}


def _kvquote(k, v):
	return [ '%s={%s}' % (k, v) ]


def _kvint(k, v):
	return [ '%s=%d' % (k, v) ]

def _kvstr(k, v):
	return [ '%s=%s' % (k, v) ]

def _kvnull(k, v):
	return []

def _kvline(k, v):
	return [ '%s = %d %d' % (k, v[0], v[1]) ]

_oktag = re.compile("^[a-zA-Z][a-zA-Z0-9]*$")
def _kvtags(k, v):
	for tmp in v:
		if not _oktag.match(tmp):
			raise BadTagError, 'tags can contain only alphanumerics: "%s"' % tmp
	return [ 'tag={%s}' % tmp for tmp in v ]

def _kverr(k, v):
	raise RuntimeError, "'tags', not 'tag'."

PROPout = {'color': _kvstr, 'text': _kvquote, 'font': _kvquote,
	'select': _kvint, 'edit': _kvint, 'move': _kvint, 'rotate': _kvint,
	'delete': _kvint, 'fixed': _kvint,
	'line': _kvline, 'tags': _kvtags, 'tag': _kverr,
	'ruler': _kvint, 'width': _kvint,
	'point': _kvstr, 'highlite': _kvint, 'include': _kvint
	}



_rparse = re.compile(r"""{[^}]*}|"[^"]*"|'[^']'|[^\s,()=#]+|[#]|=""")

def make_chunks(s):
	return _rparse.findall(s)



def property_parser(ap):
	kwargs = {}
	i = 0
	while i+2 < len(ap):
		arg = ap[i]
		if arg in PROPin and ap[i+1] == '=':
			if arg == 'line' and i+3 < len(ap):
				kwargs[arg] = ( int(ap[i+2]), int(ap[i+3]) )
				i += 4
			elif arg == 'tag': 
				if 'tags' not in kwargs:
					# This is just setting up a list to extend if we
					# have more than one occurrence of 'tags'.
					kwargs['tags'] = [ dequote(ap[i+2]) ]
				else:
					kwargs['tags'].append( dequote(ap[i+2]) )
				i += 3
			else:
				kwargs[arg] = PROPin[arg]( ap[i+2] )
				i += 3
		else:
			die.info('ap=%s' % str(ap))
			die.die('Unexpected word in property: %s' % arg)
	# print 'PP:', kwargs
	return kwargs


def test_property_parser():
	print "TPP"
	pp = property_parser
	assert pp(['select', '=', '1']) == {'select': 1}
	assert pp(['text', '=', '1']) == {'text': '1'}
	assert pp(['text', '=', '{foo}']) == {'text': 'foo'}
	assert pp(['text', '=', '"foo"']) == {'text': 'foo'}
	assert pp(['line', '=', '1', '1']) == {'line': (1,1)}
	assert pp(['select', '=', '1', 'fixed', '=', '0']) == {'select': 1, 'fixed': 0}


def region_parser(s, defprop):
	s = s.strip()
	kwargs = defprop.copy()
	if s.startswith('-'):
		kwargs['include'] = 0
		s = s[1:]
	elif s.startswith('+'):
		kwargs['include'] = 1
		s = s[1:]

	# print 's=', s
	aa = make_chunks(s)
	x = aa[0]
	# print 'aa=', aa
	if '#' in aa:
		hi = aa.index('#')
		# print 'hi=', hi
		ap = aa[hi+1:]
		aa = aa[1:hi]
	else:
		aa = aa[1:]
		ap = []
	# print 'region_parser:', aa, '###', ap

	args = [ float(q) for q in aa ]
	kwargs.update( property_parser(ap) )
	return (x, args, kwargs)


def test_region_parser():
	print "TRP"
	x, args, kwargs = region_parser('line(0,0,1,2)', {})
	assert x == 'line'
	assert args == [0, 0, 1, 2]
	assert kwargs == {}

	x, args, kwargs = region_parser('+point(-1,2)', {})
	assert x == 'point'
	assert args == [-1, 2]
	assert kwargs == {'include': 1}

	x, args, kwargs = region_parser('-point(-1,2) # color=red', {})
	assert x == 'point'
	assert args == [-1, 2]
	assert kwargs == {'include': 0, 'color': 'red'}

	x, args, kwargs = region_parser('circle(0,2,3) # text={foo}', {})
	assert x == 'circle'
	assert args == [0,2,3]
	assert kwargs == {'text': 'foo'}

	x, args, kwargs = region_parser('circle(0,2,3) # text="foo" rotate =1', {})
	assert x == 'circle'
	assert args == [0,2,3]
	assert kwargs == {'text': 'foo', 'rotate': 1}

	x, args, kwargs = region_parser('circle(0,2,3) # text="foo bar" rotate = 0 fixed= 1', {})
	assert x == 'circle'
	assert args == [0,2,3]
	assert kwargs == {'text': 'foo bar', 'rotate': 0, 'fixed': 1}

	x, args, kwargs = region_parser('circle(0,2,3) # text={foo bar} line=1 1 fixed=0', {})
	assert x == 'circle'
	assert args == [0,2,3]
	assert kwargs == {'text': 'foo bar', 'line': (1,1), 'fixed': 0}



_text_region = re.compile(r'\s*#\s*text[( \t]([0-9eE.+-]+)[, \t]+([0-9eE.+-]+)[) \t]\s*(.*)$')

def text_kluge(s):
	m = _text_region.match(s)
	assert m
	kwargs = property_parser(make_chunks(m.group(3)))
	# print '#kwargs=', kwargs
	txt = kwargs.pop('text')
	return text(float(m.group(1)), float(m.group(2)), txt, **kwargs)

def test_text_kluge():
	print "TTK"
	tmp = text_kluge('# text(2,1) text={fred} color=red tag={RefImgF}')
	assert tmp.getprop('color') == 'red'
	assert tmp.getprop('text') == 'fred'
	assert tmp.getprop('tags') == ['RefImgF',]
	assert abs(tmp.x-2.0)<0.0001 and abs(tmp.y-1.0)<0.00001


def r_list_factory(slist, Coordsys):
	gp = {'include': 1, 'text': '', 'color': 'green',
		'font': 'helvetica 10 normal', 'edit': 1,
		'move': 1, 'delete': 1, 'fixed': 0
		}
	for s in slist:
		s = s.strip()
		# print 's=', s
		if _text_region.match(s):
			yield text_kluge(s)
			continue
		elif s.startswith('#'):
			# print 'Comment', s
			continue
		if s.startswith('global'):
			gp = property_parser(make_chunks(s[len('global'):]))
			continue
		x, args, kwargs = region_parser(s, gp)
		if x is None:
			pass
		elif x == 'physical':
			pass
		elif x == 'image':
			pass
		elif x == 'circle':
			assert len(args) == 3
			yield circle(args[0]-1, args[1]-1, args[2], Coordsys=Coordsys, **kwargs)
		elif x == 'line':
			assert len(args) == 4
			yield line(args[0]-1, args[1]-1,
					args[2]-1, args[3]-1, Coordsys=Coordsys, **kwargs)
		elif x == 'point':
			assert len(args) == 2
			yield point(args[0]-1, args[1]-1, Coordsys=Coordsys, **kwargs)
		elif x == 'text':
			if len(args) == 2:
				# We happen to know that one of the kwargs
				# is text, which will provide the third
				# argument to the text() constructor.
				yield text(args[0]-1, args[1]-1, Coordsys=Coordsys, **kwargs)
			elif len(args) == 3:
				yield text(args[0]-1, args[1]-1, args[2], Coordsys=Coordsys, **kwargs)
		else:
			die.die('Unsupported region: %s in <%s>' % (x, s))


def read_regions_iter(fd, Coordsys=None):
	"""Read regions from a file.   This is an iterator.
	Fd is a file descriptor.
	"""
	return r_list_factory(fd, Coordsys)


def read_regions(fd, Coordsys=None):
	"""Read regions from a file.
	Fd is a file descriptor.
	"""
	return list(r_list_factory(fd, Coordsys))


PLOTSTYLES = ('discrete', 'line', 'step', 'quadratic', 'errorbar')


def _format_plot(xylist, format):
	if format == '(x,y)':
		ds9fmt = 'xy'
		o = [ '%10g %10g' % xy for xy in xylist ]
	elif format == '(x,y,ex)':
		ds9fmt = 'xyex'
		o = [ '%10g %10g %6g' % xye for xye in xylist ]
	elif format == '(x,y,ey)':
		ds9fmt = 'xyey'
		o = [ '%10g %10g %6g' % xye for xye in xylist ]
	elif format == '(x,y,ex,ey)':
		ds9fmt = 'xyexey'
		o = [ '%10g %10g %6g %6g' % xyexey for xyexey in xylist ]
	elif format == 'array(:,xy)':
		ds9fmt = 'xy'
		o = [ '%10g %10g' % (xylist[i,0], xylist[i,1]) for i in range(xylist.shape[0]) ]
	elif format == 'array(:,xyey)':
		ds9fmt = 'xyey'
		o = [ '%10g %10g %6g' % (xylist[i,0], xylist[i,1], xylist[i,2])
				for i in range(xylist.shape[0])
				]
	elif format == 'array(xy,:)':
		ds9fmt = 'xy'
		o = [ '%10g %10g' % (xylist[0,i], xylist[1,i]) for i in range(xylist.shape[1]) ]
	elif format == 'array(xyey,:)':
		ds9fmt = 'xyey'
		o = [ '%10g %10g %6g' % (xylist[0,i], xylist[1,i], xylist[2,i])
				for i in range(xylist.shape[1])
				]
		
	else:
		raise ValueError, 'Unknown plot data format: %s' % format
	return (ds9fmt, o)




class ds9(ds9_io):
	def __init__(self, ds9start=None):
		ds9_io.__init__(self, ds9start=ds9start)
		self.set('mode', 'pointer')
		self.frame = -1

	def load(self, fn):
		self.set('regions', 'delete', 'all')
		self.set('file', fn)

	def get_current_fname(self):
		return self.getlast( 'iis', 'filename' )

	def get_frames(self):
		tmp = self.getlast( 'frame', 'all' ).split()
		if 'XPA$END' in tmp:
			# This works around a bug in ds9:
			# if it has no data frames, it'll tell you
			# about the buttons and other stuff.
			return []
		return tmp

	def frame_cmd(self, *cmds):
		"""A catch-all command for anything that's not otherwise implemented."""
		self.set('frame', *cmds)
	

	def del_frames(self, framelist):
		"""Note: deleting all the frames crashes ds9.
		"""
		for i in framelist:
			self.select_frame(i)
			self.frame_cmd('delete')


	def select_frame(self, i):
		"""Select a frame on the attached ds9 image display.
		The frame will be created if it didn't already exist.
		@param i: Which frame?   Apparently, any integer is OK,
			even negative.
		@type i: L{int}
		"""
		si = str(int(i))
		if si != self.frame:
			self.set('frame', 'frameno', si)
			self.frame = si


	def get_regions_iter(self):
		return r_list_factory(self.getiter('regions', '-format', 'ds9',
							'-delim', 'nl' ),
					None
					)

	def get_regions(self):
		return list(self.get_regions_iter())

	def delete_all_regions(self):
		self.set('regions', 'delete', 'all')

	def delete_region_group(self, *group):
		for g in group:
			self.set('regions', 'group', g, 'delete')

	def add_region(self, *region):
		"""Add a list of regions to the current frame.
		@param region: one or more regions.
		@type region: C{[ region ]}, where C{region} is normally 
			an instance of L{Region}, but can be anything that
			produces a string suitable for X{ds9}.
			See C{http://hea-www.harvard.edu/RD/ds9/ref/xpa.html#regions}.
		"""
		# print 'region=', str(region)
		self.set_with_input([ str(r) for r in region ], 'regions')


	def region_cmd(self, *cmds):
		"""A catch-all command for anything that's not otherwise implemented.
		This does C{xpaset -p}, so you cannot use it for region definitions
		that need multi-line input via L{set_with_input}.
		"""
		self.set('regions', *cmds)

	def zoom(self, z):
		self.set('zoom', 'to', str(z))

	def scale_cmd(self, *cmds):
		"""A catch-all command for anything that's not otherwise implemented."""
		self.set('scale', *cmds)

	def cmap_cmd(self, *cmds):
		"""A catch-all command for anything that's not otherwise implemented."""
		self.set('cmap', *cmds)
	
	def set_mode(self, m):
		assert m in ['tile', 'blink', 'single']
		if m == 'tile':
			self.set('tile', 'yes')
		else:
			self.set('tile', 'no')
		if m == 'single':
			self.set('single')
		if m == 'blink':
			self.set('blink')

	def pan_to(self, x, y, coordsys):
		self.set('pan', 'to', str(x), str(y), coordsys)

	plotname_ok = re.compile('[a-z][a-zA-Z_]*')

	def plot(self, name, xylist, title='', xlabel='', ylabel='',
			format='(x,y)', line='solid',
			color='black', symbol=None):
		assert name != 'new'
		assert self.plotname_ok.match(name), "Bad plot name: %s" % name
		ds9fmt, formatted = _format_plot(xylist, format)
		if name in self.list_plots():
			assert title==''
			assert xlabel==''
			assert ylabel==''
			self.set_with_input( formatted, 'plot %s data %s' % (name, ds9fmt))
		else:
			self.set_with_input( formatted,
					'plot new name %s {%s} {%s} {%s} %s'
						% (name, title, xlabel, ylabel, ds9fmt)
						)
		assert color in COLORS
		self.set('plot', 'view', 'discrete', ['yes', 'no'][symbol is None])
		self.set('plot', 'view', 'line', ['yes', 'no'][line is None])
		if symbol is not None:
			assert symbol in PLOTSYMS
			self.set('plot', 'color', 'discrete', color)
			self.set('plot', 'line', 'discrete', symbol)
		if line is not None:
			self.set('plot', 'color', 'line', color)
			self.set('plot', 'line', 'dash', ['no', 'yes'][line=='solid'])

	def close_plot(self, name):
		self.set('plot', 'close', '{%s}' % name)

	def list_plots(self):
		return self.getlast('plot').split()

	def comment(self, s):
		pass

	def flush(self):
		pass


class ds9_file(object):
	"""This is just a convenient way to write regions to a file,
	instead of writing them to a ds9 session.   Note that plots
	and other interactive things are simply no-ops.
	"""

	def __init__(self, fd):
		self.fd = fd
		self.frame = -1
		self.fd.writelines('# Region file format: DS9 version 4.0\n')

	def select_frame(self, i):
		si = str(i)
		if si != self.frame:
			self.fd.writelines('# frame %s\n' % i)
			self.frame = si


	def add_region(self, region):
		self.fd.writelines( [ str(region), '\n'] )


	def comment(self, s):
		self.fd.writelines( ['# ', s, '\n'] )

	def flush(self):
		return self.fd.flush()

	def plot(self, name, *args, **kwargs):
		self.comment('plot %s' % name)


	def list_plots(self):
		return []

def test_io():
	print "TIO"
	ds9_io()


def test_tags():
	print "TT"
	tmp = ds9()
	tmp.add_region(line(1,1,50,50, tags=('aa', 't2', 'xyz'), text='foo bar') )
	for r in tmp.get_regions():
		if r.getprop('text', '') == 'foo bar':
			assert r.x0 == 1 and r.y0==1 and r.x1==50 and r.y1==50
			assert 'aa' in r.getprop('tags')
			assert 't2' in r.getprop('tags')
			assert 'xyz' in r.getprop('tags')


def test_plot():
	print "TPL"
	import math
	xylist1 = [ (x, math.cos(x*0.3)) for x in range(100) ]
	xylist2 = [ (x, math.sin(x*0.33)) for x in range(100) ]
	tmp = ds9()
	tmp.plot('some_data', xylist1, 'Some Data', 'x-axis', 'y-axis')
	tmp.plot('some_data', xylist2, color='red')
	time.sleep(6)



if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2:
		for r in read_regions_iter(open(sys.argv[1], 'r')):
			print r
		sys.exit(0)
	test_property_parser()
	test_text_kluge()
	test_region_parser()
	test_io()
	test_tags()
	test_plot()

