#!/usr/bin/python

"""This program reads a FIAT format data file
and displays some of the information.
You can select some of the lines with the
-select flag, and the display the selected lines
in several different ways.

Flags:
	- -select expr	Where expr is a python expression
		that returns True or False.   All the normal
		builtins are available.   The data in the
		line is presented as a set of local variables,
		so that if the value in the column labelled
		"filename" is "f005.wav", then you could test
		for 'filename=="f005.wav"'.   Note that everything
		is a string, so you may need to convert to int
		or float before some tests: 'int(nspeakers)<5'.
	- -showav	Displays the entire line in a=v; format.
	- -showfiat	Displays the resulting file in FIAT format,
		preserving the header information.
	- -show format
		This displays the file as a
		text file, using evaluating format (which is a
		snippet of python code that should return a string):
		-show "'%s # %s'%(fname,loudness)"
		will display the fname and loudness columns of the
		selected lines, separated by a hash mark.
	- -rav	Reads the input file in a=v; format rather than fiat.

	- -senv  Exec some python code to set a global variable
		that is visible in the -select expression.
		(e.g. "x=3").
	- -penv  Exec some python code to set a global variable
		that is visible in the -show expression.
		(e.g. "x=3").
	- -strap exception value
"""

from gmisclib import die
from gmisclib import fiatio
from gmisclib import avio
from gmisclib import g2_select
from gmisclib import gpk_writer

SHOWAV = 1
SHOWFIAT = 2


def process(f, read_fcn, o, select):
	if f == '-':
		fd = sys.stdin
	else:
		fd = open(f, 'r')

	h1, d1 = read_fcn(fd)
	o.headers(h1)

	ne1 = 0
	ne2 = 0
	npr = 0
	for (i, t) in enumerate(d1):
		try:
			ok = select.eval(t)
		except NameError, x:
			if ne1 == 0:
				die.warn('NameError in selector: %s on item %d: %s' % (str(x), i+1, avio.concoct(t)))
			ne1 += 1
			ok = False
		if not ok:
			continue

		try:
			o.datum(t)
			npr += 1
		except NameError, x:
			if ne2 == 0:
				die.warn('NameError in show: %s on item %d: %s' % (str(x), i+1, avio.concoct(t)))
			ne2 += 1
	if ne1==len(d1):
		die.warn('NameError in select on each of the %d data.' % len(d1))
	if ne2>0 and npr == 0:
		die.warn('NameError in show on each of the %d prints.' % ne2)


def fiat_read(fn):
	h, d, c = fiatio.read(fn)
	return (h, d)


def avio_read(fn):
	d, c = avio.read(fn)
	return ({}, d)


def _find_lod(lod, attribute, value):
	"""Look through a list of dictionaries, as one might get from fiatio.read
	or avio.read, and pick out the dictionary that contains a specified
	attribute=value pair.
	"""
	for d in lod:
		try:
			if d[attribute] == value:
				return d
		except KeyError:
			pass
	return None


class writer(gpk_writer.writer):
	def comment(self, comment):
		"""Add a comment to the data file."""
		pass

	def header(self, k, v):
		pass
	
	def __init__(self, fd, s):
		gpk_writer.writer.__init__(self, fd)
		self.s = g2_select.selector_c(s)


	def datum(self, data_item):
		self.fd.write(str(self.s.eval(data_item)) + '\n')

	def globals(self, code):
		self.s.globals(code)


if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	select = g2_select.selector_c('True')
	select.g['fiatio'] = fiatio
	select.g['avio'] = avio
	select.g['find'] = _find_lod
	o = avio.writer(sys.stdout)
	read_fcn = fiat_read
	deferred_penv = []
	n_senv = 1
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-select':
			select.set_code(arglist.pop(0))
		elif arg == '-senv':
			tmp = arglist.pop(0)
			try:
				select.globals(tmp)
			except:
				die.warn('Exception while executing -senv flag number %d: "%s"' %
						(n_senv, g2_select._compact(tmp)))
				raise
			n_senv += 1
		elif arg == '-strap':
			select.set_trap(eval(arglist[0], select.g), eval(arglist[1], select.g))
			arglist = arglist[2:]
		elif arg == '-penv':
			deferred_penv.append( arglist.pop(0) )
		elif arg == '-show':
			o = writer(sys.stdout, arglist.pop(0))
		elif arg == '-showav':
			o = avio.writer(sys.stdout)
		elif arg == '-showfiat':
			o = fiatio.writer(sys.stdout)
		elif arg == '-rav':
			read_fcn = avio_read
		elif arg == '-rfiat':
			read_fcn = fiatio_read
		else:
			die.die('Bad arg: %s' % arg)
	if isinstance(o, writer):
		n_penv = 1
		for tmp in deferred_penv:
			try:
				o.globals( tmp )
			except:
				die.warn('Exception while executing -penv flag number %d: "%s"' %
						(n_penv, g2_select._compact(tmp)))
				raise
			n_penv += 1
	elif deferred_penv:
		die.die("Flag -penv only makes sense with -show flag")

	if len(arglist) < 1:
		print __doc__
		die.die('Not enough arguments')

	for f in arglist:
		process(f, read_fcn, o, select)

