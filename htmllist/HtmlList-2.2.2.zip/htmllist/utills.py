# HtmlList - Finds repetitive format patterns in an HTML page.
# Copyright (C) 2010  Erez Bibi (erezbibi@users.sourceforge.net)
#
# This file is part of HtmlList.
#
# HtmlList is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HtmlList is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HtmlList.  If not, see <http://www.gnu.org/licenses/>.

"""
Utilities Module
"""

import re
import itertools
from htmlentitydefs import entitydefs
from string import maketrans

from urllib2 import urlopen, Request, HTTPError

################################################################################

def iter2tuple(func):
	""" Simple decorator to convert iterator to a tuple """
	def _iter2tuple (*args, **kw):
		return tuple(func(*args, **kw))
	return _iter2tuple


def not_empty_iter(func):
	""" Decorator over a function that returns an iterator. If the returned
	iterator is empty, it will return None. So the user can (must) check if the
	iterator is not None before using it.
	"""
	def _not_empty_iter(*args, **kw):
		itr = func(*args, **kw)
		try:
			first = itr.next()
		except StopIteration:
			return None
		else:
			return itertools.chain([first], itr)
	return _not_empty_iter

################################################################################
## Quote and Unquote HTML ##
_re_unquote = re.compile(r"&(#?)(.+?);")
entitydefs["nbsp"] = ' ' # Fix a weirdness of entitydefs

def unquote_html(string):
	""" Convert an HTML quoted string into normal string (ISO-8859-1).
	Works with &#XX; and with &nbsp; &gt; etc.
	From: http://groups.google.com/group/comp.lang.python/browse_thread/thread/7f96723282376f8c/
	"""
	def _convert_entity(m):
		if m.group(1)=='#':
			try:
				return chr(int(m.group(2)))
			except ValueError:
				return '&#%s;' % m.group(2)
		try:
			return entitydefs[m.group(2)]
		except KeyError:
			return '&%s;' % m.group(2)

	if not string: return string
	return _re_unquote.sub(_convert_entity, string)

_re_quote = re.compile(r'(["<>])|(&)[^\s;]*(;)?')
_convertion_table = {
	'"': "&quot;",
	'<': "&lt;",
	'>': "&gt;",
	'&': "&amp;",
}

def quote_html(string):
	""" Quote the <, >, " symbols and the & symbol if it is not part of &xxx; """
	def _convert_entity(m):
		if m.group(1):
			return _convertion_table[m.group(1)]
		elif m.group(2) and not m.group(3):
			return _convertion_table[m.group(2)]

	if not string: return string
	return _re_quote.sub(_convert_entity, string)

################################################################################
## Remove tags ##

_ptrn_script = """<script
	(
		# [^>]*/> | # Links that closes in the start tag (<script .... />)
		[^>]*> .*? </script> # Regular <script>...</script>
	)
"""
_re_script = re.compile(_ptrn_script, re.DOTALL | re.VERBOSE | re.IGNORECASE)

def strip_scripts(data):
	""" Removes <script> tags from a string """
	return _re_script.sub(' ', data)

_re_tags = re.compile(r"\s*(<.*?>\s*)+", re.DOTALL)

def strip_tags(data, replacement=' '):
	""" Removes any tag from a string """
	return _re_tags.sub(replacement, data)

################################################################################
## Open URL ##

def url_open(url, user_agent=None, err=None):
	""" Open a URL with an optional user agent.
	url can be a string or a Request instance

	If err is a list object, in case of URL-Error it will append to this list
	the error code, error message, and URL

	Return the pages text.
	"""
	text = ''
	try:
		if not isinstance(url, Request):
			req = Request(url)
		else: req = url
		if user_agent:
			req.add_header("user-agent", user_agent)
		page = urlopen(req)
		text = page.read()
		page.close()
	except HTTPError, e:
		if isinstance(err, list):
			err.append(e.code)
			err.append(e.msg)
			err.append(e.url)
		print "Cannot open:", e.url, e.msg, e.code
	except:
		print "Error opening:", url
	return text

if __name__ == '__main__':
	err_lst = []
	url_open("http://pyhtmllist.sourceforge.net/foo.bar", err = err_lst)
	assert err_lst

