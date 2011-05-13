#!/usr/bin/env python

"""This program takes files named *.q in the current directory, and converts them to HTML.
To do that, it looks for a python script called 'headfoot.py' or '../headfoot.py' or ... .
This script needs to define one variable ( server ) and two functions (header and footer).

The .q files have the following format::

	TITLE title string
	OTHER_HEADER_KEYWORD header info
	
	P
		Text is 3>5 ?
		A ref="foo.html" No!
			More text inside the link.
		IMG ref="foo.gif"
		UL
			LI List item
			LI Another List item


The header info is separated from the body with a blank line.
HTML tags are always the first thing on a line.
Line continuations and enclosures are indicated with indentation.
Tags automatically close when the indentation gets smaller.

The PRE tag is the only exception.
You have to close it with a line beginning '/PRE'.
No indenting is needed inside a PRE /PRE pair.

The user needs to define one thing:
the address of the web server.
This address is prepended to
all hyperlinks and image references that aren't absolute.

All the header information gets put into a dictionary, and is
passed into the header() and footer() functions.
That dictionary has 'filename' and '_server_root' entries added.

The user can also define three things:

DEFAULT_HEADER, a dictionary passed to the header() and footer functions().
Useful things to put in DEFAULT_HEADER are:
	- 'lang': 'en'	# appears in the <html lang="en"> tag
	- 'stylesheet': url becomes a link to a stylesheet: <link rel="stylesheet" type="text/css" href="url">
	- Anything in the form M.x:y becomes a <meta name="x" content="y">
	- M.description and M.keywords are useful.
	- Anything in the form HTTP.x:y becomes a <meta http-equiv="x" content="y">

Header(thd, hinfo) takes two arguments, a file descriptor
to which it should write the HTML, and a dictionary of header
information.

Footer(thd, hinfo) takes the same arguments.

See _header() and _footer() below, for examples.
"""

import os
import re
import time
import urlparse
from gmisclib import die
from gmisclib import g_pipe

XML = 0

POINTTAG = 1
_anytag = {'P':0, 'STYLE': 0,
		'UL':0, 'OL':0, 'DL':0,
		'LI':0, 'DT': 0, 'DD': 0,
		'PRE':'SPECIAL',
		'TABLE':0, 'TR':0, 'TD':0,
		'CAPTION':0,
		'TBODY':0, 'THEAD':0, 'TFOOT':0,
		'FORM':0, 'INPUT':1, 'SELECT':0, 'OPTION':0, 'TEXTAREA':0,
		'A':0, 'NOP': 0,
		'H1':0, 'H2':0, 'H3':0, 'H4':0,
		'EM':0, 'STRONG':0, 'CITE':0, 'DFN':0,
		'CODE':0, 'SAMP':0, 'KBD':0, 'VAR':0, 'ABBR':0, 'ACRONYM':0,
		'OBJECT': 0, 'DIV': 0, 'SPAN': 0,
		'FONT': 0,
		'IMG': POINTTAG, 'BR': POINTTAG, 'HR': POINTTAG
		}

_ck = re.compile(r'\b(H1|PRE|P|TITLE|IMG)\b', re.IGNORECASE)

def _checkfile(f):
	"""Look at the beginning of a file to see if is plausibly input for this program."""
	fd = open(f, "r")
	for l in fd.readlines()[:10]:
		if _ck.match(l):
			return 1
	return 0



def qfiles(dir):
	o = []
	minname = re.compile('^.*[.]q$')
	l = os.listdir(dir)
	for t in l:
		ts = t.strip()
		x = minname.match(ts)
		if not x:
			continue
		if not _checkfile(ts):
			continue
		o.append(ts)
	return o




def av(k, v):
	if not v.startswith('"') or not v.endswith('"'):
		v = '"%s"' % v
	return "%s=%s" % (k, v)


LL = 60
TABW = 8

DEFAULT_TAG = 'P'
DEFAULT_INDENT = -1

def measure_indent(s):
	indent = 0
	i = 0
	if s.isspace():
		return (None, '')

	while i<len(s) and s[i].isspace():
		if s[i] == ' ':
			indent += 1
		elif s[i] == '\t':
			indent = TABW*((indent+TABW)/TABW)
		elif s[i] == '\r' or s[i] == '\n':
			return (None, '')
		else:
			raise ValueError, "Unrecognized whitespace: %d" % ord(s[i])
		i += 1
	return indent


def prepare_text(l):
	l = l.strip()
	if l.startswith('%'):
		l = l[1:].lstrip()
	return l


def starts_with_a_tag(l):
	a = l.split(None, 1)
	if len(a) == 0:
		return False
	elif len(a) == 1:
		return _anytag.has_key(a[0])
	else:
		return _anytag.has_key(a[0]) and '=' in a[1]


_eqtoken = re.compile("""\s*([a-zA-Z0-9_:]+)\s*=\s*(("[^"]*")|(\S+))\s*""")
def tokenize(l):
	# print "TOKENIZE:", l.strip()
	a = l.split(None, 1)
	tag = a[0]
	args = {}
	if len(a) > 1:
		s = a[1]
		while True:
			m = _eqtoken.match(s)
			if not m:
				break
			args[m.group(1)] = m.group(2)
			s = s[m.end():]
		txt = s
	else:
		txt = ''
	die.info("TOKENIZED:%s %s %s" % (tag, args, txt))
	return (tag, args, txt)


class lineC:
	def __init__(self, l):
		self.indent = measure_indent(l)
		l = l.strip()
		if starts_with_a_tag(l):
			self.tag, self.args, self.txt = tokenize(l)
		else:
			self.tag = None
			self.args = None
			self.txt = prepare_text(l)

	def getarg(self, k, defv):
		return self.args.get(k, defv)




def format_dict(d, drop=None):
	o = []
	if drop is None:
		for (k, v) in d.items():
			o.append(av(k, v))
	else:
		for (k, v) in d.items():
			if not k.startswith(drop):
				o.append(av(k, v))
	return o


def dequote(a):
	if len(a) > 1 and a[0]=='"' and a[-1]=='"':
		return a[1:-1]
	return a

def urlq(s):
	return s


def prepend(a, b):
	"""Process a URL.  Pathnames are prepended with the server root.
	Complete URLs are untouched."""

	# print 'JOIN', a['_abs_root'] + '/' + a['_cwd'] + '/', b
	return '"%s"' % urlparse.urljoin(urlq(a['_abs_root'] + '/' + a['_cwd'] + '/'),
					urlq(dequote(b)))



def process_tag(d, od, hinfo, eol):
	references = []

	# print "Tag=", d.tag
	if d.tag == 'IMG':
		d.args['src'] = prepend(hinfo, d.args['ref'])
		references = [ d.args['src'] ]
		del d.args['ref']
	elif d.tag == 'OBJECT':
		d.args['data'] = prepend(hinfo, d.args['ref'])
		references = [ d.args['data'] ]
		del d.args['ref']
	elif d.tag == 'A' and 'ref' in d.args:
		d.args['href'] = prepend(hinfo,  d.args['ref'])
		references = [ d.args['href'] ]
		del d.args['ref']

	args = format_dict(d.args, '_')

	if XML:
		pointclose = ([], ['/'])[ _anytag[d.tag]==POINTTAG ]
	else:
		pointclose = []

	od.write('<%s>%s%s' % (' '.join([d.tag] + args + pointclose), d.txt, eol))

	if not _anytag[d.tag] == POINTTAG:
		return (references, d.tag)
	return (references, None)


_escape = {'~': '&nbsp;', '>':'&gt;', '<':'&lt;', '&':'&amp;',
		'"': '&quot;'
		}
_epat = '&[0-9a-zA-Z]{,5};|' + ( '|'.join(_escape.keys()) )
# print "EPAT=", _epat
_ere = re.compile(_epat)
def _esc1(x):
	"""Converts a character in a MatchObject to a &xx; (HTML) escape sequence"""
	mstring = x.group(0)
	if len(mstring)==1:
		return _escape[mstring]
	return mstring



def escape(s):
	return _ere.sub(_esc1, s)


def get_logical_line(lines):
	while 1:
		if len(lines) == 0:
			break
		o = lines.pop(0)
		if not o.startswith('#'):
			return o
	return None



def process(lines, od, hinfo):
	stack = [('BODY', -1000)]	# [ (tag, indent), ... ]

	references = []
	eol = '\n'
	n = 0
	while 1:
		n += 1
		l = get_logical_line(lines)
		if l is None:
			break
		if l.lower().startswith('pre'):
			od.write('<pre>' + l[len('pre'):])
			while len(lines) > 0:
				l = lines.pop(0).rstrip()
				if l.lower().startswith('/pre'):
					break
				od.write(l + '\n')
			od.write("</pre>\n")
			if len(lines) == 0:
				break
			l = get_logical_line(lines)

		# print "#", l
		try:
			d = lineC(l)
		except ValueError, x:
			raise ValueError, "Bad Parse, line %d: %s" % (n, x)

		if d is None:
			# print "EMPTY"
			continue

		while d.indent <= stack[-1][1]:
			cltag, oindent = stack.pop(-1)
			od.write("</%s>%s" % (cltag, eol))

		if d.tag is not None:
			# print "args=", d.args
			some_refs, cltag = process_tag(d, od, hinfo, eol)
			if cltag is not None:
				stack.append((cltag, d.indent))
			references.extend( some_refs )

		elif d.txt is not None:
			od.write('%s%s' % (escape(d.txt), eol))

	while len(stack) > 0:
		od.write('</%s>%s' % (stack.pop(-1)[0], eol))

	return references


def swapend(a, e):
	t = a.rindex('.')
	return a[:t] + e


def aget(dic, alist):
	o = []
	for a in alist:
		for ac in [a, a.lower(), a.upper()]:
			if dic.has_key(ac):
				o.append('%s="%s"' % (ac, dic[ac]))
				break
	if len(o) == 0:
		return ''
	return " " + ' '.join(o)


def sw(s, prefix):
	return s.startswith(prefix) or s.startswith(prefix.lower()) or s.startswith(prefix.upper())

def dpre(s, prefix):
	return s[len(prefix):]

def agp(dic, prefix):
	lp = len(prefix)
	o = []
	for (k, v) in dic.items():
		if len(k) <= lp:
			continue
		if sw(k, prefix):
			o.append('%s="%s"' % (k[lp:], v))
	if len(o) == 0:
		return ''
	return " " + ' '.join(o)


def get(dic, key, dfl):
	for k in [key, key.lower(), key.upper()]:
		if dic.has_key(k):
			return dic[k]
	return dfl


def _header(thd, hinfo):
	thd.write( get(hinfo, 'DOCTYPE',
			'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
			) + '\n'
		)
	thd.write('<html%s>\n' % aget(hinfo, ['lang']))
	thd.write("<head>\n")
	sty = get(hinfo, 'stylesheet', '')
	if sty != '':
		thd.write('<link rel="stylesheet" type="text/css" href="%s">' % sty)
	if hinfo.has_key('_mod_time'):
		thd.write('<meta http-equiv="Last-Modified" content="%s">\n'
				% time.asctime(time.gmtime(hinfo['_mod_time'])))
	for (k, v) in hinfo.items():
		if sw(k, 'M.'):
			thd.write('<meta name="%s" content="%s">\n' % (dpre(k, 'M.'), v))
		if sw(k, 'HTTP.'):
			thd.write('<meta http-equiv="%s" content="%s">\n' % (dpre(k, 'HTTP:'), v))
	thd.write("<title>%s</title>\n" % get(hinfo, 'TITLE', hinfo['filename']))
	thd.write("</head>\n")
	thd.write("<body%s>\n" % agp(hinfo, 'B.'))


def _common(lines, hinfo):
	return lines


def _footer(thd, hinfo):
	thd.write("</html>\n")


def readheader(fd, t):
	h = {'filename': t}
	while 1:
		l = fd.readline()
		if l is None:
			break
		l = l.rstrip()
		if l == '':
			break
		if l[0] == '#':
			continue
		a = l.split(None, 1)
		assert len(a) == 2
		h[a[0].strip()] = a[1].strip()
	return h


MTIME = 8

def needcopy(a, b, force=None):
	"""Do we need to reconstruct file b from
	file a?   Also reconstruct b if it is older
	than the date in force.
	"""
	assert os.access(a, os.F_OK + os.R_OK)
	ossa = os.stat(a)
	if not os.access(b, os.F_OK):
		return 1
	ossb = os.stat(b)
	if force is not None and ossb[MTIME] < force:
		return 1
	if ossb[MTIME] < ossa[MTIME]:
		return 1
	return 0


def file_only(url):
	"""Given a URL, just return the file part,
	not the target specifier inside the file."""

	a = url.split('#')
	if len(a) > 2:
		die.warn("URL has more than one '#': can't split into file and target.")
		return url
	return a[0]


def del_fin_sl(s):
	if s.endswith('/'):
		return s[:-1]
	return s


def go(env, force=None):
	htmlheader = env.get('header', _header)
	htmlfooter = env.get('footer', _footer)
	htmlcommon = env.get('common', _common)
	default_header = env.get('DEFAULT_HEADER', {})
	all = set()
	q = qfiles('.')
	for t in q:
		th = swapend(t, '.html')
		if not needcopy(t, th, force):
			print "# No need to process", t
			continue
		die.info("# processing:%s -> %s\n" % (t, th))
		fd = open(t, "r")
		# thd = open(th, "w")
		thd, thdo = g_pipe.popen2("/usr/bin/tidy", ['tidy', '-asxhtml', '-c', '-i', '-q', '-o', th])
		hinfo = default_header.copy()
		hinfo.update(readheader(fd, t))
		hinfo['_mod_time'] = os.fstat(fd.fileno()).st_mtime
		hinfo['_server_root'] = del_fin_sl(env.get('server', '.'))
		hinfo['_abs_root'] = del_fin_sl(env.get('server', '.'))
		hinfo['_rel_root'] = del_fin_sl(env.get('rel_root', '.'))
		if env.has_key('cwd'):
			hinfo['_cwd'] = env['cwd']
			hinfo['_local_root'] = env['cwd']
		htmlheader(thd, hinfo)
		lines = htmlcommon([x.rstrip() for x in fd.readlines()], hinfo)
		for reference in process(lines, thd, hinfo):
			all.add(reference)
		fd.close()
		htmlfooter(thd, hinfo)
		thd.close()

	return all



DEFF = 'headfoot.py'


def easygo():
	force = None
	env = {}
	cwd = os.getcwd().split('/') + ['.']
	for i in range(10):
		chkd = './' + ( '../' * i )
		chk = chkd + DEFF
		print "checking", chk
		if os.access(chk, os.R_OK):
			env['rel_root'] = chkd[:-1]
			env['cwd'] = '/'.join(cwd[-i-1:])
			execfile(chk, env)
			assert env.has_key('server')
			force = os.stat(chk)[MTIME]
			break
	return go(env, force)
	





if __name__ == '__main__':
	o = easygo()
	print "# Files to upload:"
	for t in o:
		print t
