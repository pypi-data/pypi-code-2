#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Argot markup language, a set of extensions on John Gruber's markdown."""

import re
import sys
import random

# simplejson could potentially be all over the place
try: import json as simplejson # python 2.6
except ImportError:
    try: import simplejson
    except ImportError:
        try: from django.utils import simplejson
        except: simplejson = None

# pygments syntax highlighter
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from markdown import markdown, inlinepatterns

# from argot
import utils
from uuid import uuid4

def uuid():
    """Return a uuid as a string."""
    return str(uuid4())

class ArgotBlock(object):
    def render(self):
        raise NotImplemented

class CodeBlock(ArgotBlock):
    """Implements a standard codeblock.  render() returns pygmentized text
    for the contents of the codeblock with `lang` highlighting."""
    def __init__(self, content, lang=None):
        self.content = content
        self.lang = lang

    def render(self):
        return utils.pygmentize(self.content, self.lang)

class BlockquoteBlock(ArgotBlock):
    """Implements a standard blockquote.  render() returns blockquoted text
    with optional citation."""
    def __init__(self, content, cite=None):
        self.content = content
        self.cite = cite

    def render(self):
        tag = '<blockquote>'
        if self.cite:
            # TODO: fix this html injection vector
            tag = '<blockquote cite="%s">' % (self.cite)
        return u''.join([tag, markdown(self.content), '</blockquote>'])

class ArgotString(unicode):
    """A unicode subclass that automatically removes codeblocks and can 'render'
    itself as an Argot string.  Use its string value at your own risk;  the
    value is immutable and making copies won't preserve its block map."""
    codeblock_re = re.compile(r'{{{\s*'
        '(?:#!(?P<decl>\w+))?'  # optional language declaration
        '(?P<content>.*?)'      # content
        '}}}', re.MULTILINE|re.DOTALL)

    blockquote_re = re.compile(r'\(\(\(\s*'
        '(?:["\'](?P<cite>.*?)["\'])?'  # optional citation url
        '(?P<content>.*?)'              # content
        '\)\)\)', re.MULTILINE|re.DOTALL)

    def __new__(cls, val):
        val, map = cls.block_replace(val)
        obj = unicode.__new__(cls, val)
        obj.map = map
        return obj

    @staticmethod
    def block_replace(s):
        """Return a string that has moin blocks replaced with UUIDs and a
        dictionary that is a map from UUID to the content that has been
        removed."""
        s, map = ArgotString.codeblock_replace(s)
        s, map = ArgotString.blockquote_replace(s, map)
        return s, map

    @staticmethod
    def codeblock_replace(s, map=None):
        """Replace all codeblocks with uuids.  Return the new string and a
        map of uuids -> ArgotBlock objects that render themselves."""
        map = {} if map is None else map
        match = ArgotString.codeblock_re.search(s)
        while match:
            lang, content = match.groups()
            id = uuid()
            s = replace_section(s, id, match.start(), match.end())
            map[id] = CodeBlock(content, lang)
            match = ArgotString.codeblock_re.search(s)
        return s, map

    @staticmethod
    def blockquote_replace(s, map=None):
        """Replace all blockquotes with uuids.  Return the new string and a
        map of uuids -> ArgotBlock objects that render themselves."""
        map = {} if map is None else map
        match = ArgotString.blockquote_re.search(s)
        while match:
            cite, content = match.groups()
            id = uuid()
            s = replace_section(s, id, match.start(), match.end())
            map[id] = BlockquoteBlock(content, cite)
            match = ArgotString.blockquote_re.search(s)
        return s, map

    def render(self):
        #s = utils.decode_html_entities(unicode(self))
        s = unicode(self)
        s = markdown(link_processor.render(s))
        for key,block in self.map.iteritems():
            s = s.replace(key, block.render())
        return s


def render(string, no_surrounding_tag=False, encoding='utf-8'):
    """Render the string using Argot."""
    if not isinstance(string, unicode):
        string = string.decode(encoding)
    astr = ArgotString(string)
    s = astr.render()
    return utils.strip_surrounding_tag(s) if no_surrounding_tag else s

def replace_section(string, replace, start, end):
    return string[:start] + replace + string[end:]

class LinkProcessor(object):
    """A link processor is a callable who has an attribute 'tag' or whose
    __name__ is in the format `tag`_processor.  The `tag` portion will
    then be used to find and execute the links."""
    markdown_link_re = re.compile(inlinepatterns.LINK_RE)
    link_processor_re = re.compile('(?P<name>[\w]+?):(?P<query>[^/]+)')
    tag = 'link_processor'

    def __init__(self, encoding='utf-8'):
        """The `encoding` argumentis now deprecated."""
        pass

    def render(self, ustring):
        """Render a string based on the enabled link processors."""
        string = unicode(ustring)
        # not all links will be processed links;  when we find one, we have
        # to swap it out, then start over again :(  this sucks, but I can't
        # figure out a better way to do it.
        end = False
        while not end:
            end = True
            for match in LinkProcessor.markdown_link_re.finditer(string):
                link_text = match.groups()[7]
                lmatch = LinkProcessor.link_processor_re.search(link_text)
                if lmatch:
                    name, query = map(unicode.strip, lmatch.groups())
                    url = self.run_link_processor(name, query)
                    new = '[%s](%s)' % (match.groups()[0], url)
                    string = replace_section(string, new, match.start(), match.end())
                    end = False
                    break
        return string

    def run_link_processor(self, name, query):
        for proc in enabled_link_processors:
            tag = LinkProcessor.get_tag(proc)
            if name == tag:
                return proc(query)
        return '%s' % (query)

    @staticmethod
    def get_tag(function):
        tag = getattr(function, 'tag', None)
        if tag is not None:
            return tag
        else:
            return function.__name__.lower().split('_')[0]

link_processor = LinkProcessor()

# example firefox headers to hide our traffic in the bright glare of the sun
firefox_headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.10) Gecko/2009042523 Firefox/3.0.10',
    'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
}

def google_processor(query):
    """Default google link processor.  Attempts to do a googleapi ajax
    search with the query and return the first result.  For this to succeed,
    you need to set the `google_referer` to your website referer, either
    at the module level of `argot.markup` or via `set_google_referer`.
    If it fails, it returns the url of an 'Feeling Lucky' search.

    google api:
        http://code.google.com/apis/ajaxsearch/documentation/
    """
    from urllib2 import Request, urlopen
    from urllib import urlencode
    q = urlencode({'q': query})
    fallback_url = 'http://www.google.com/search?%s&btnI' % q
    if simplejson is None:
        sys.stderr.write('simplejson is required for the google link processor.')
        return query
    if not google_referer:
        return fallback_url
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % q
    req = Request(url)
    req.add_header('Referer', google_referer)
    response = urlopen(req).read()
    j = simplejson.loads(response)
    results = j['responseData']['results']
    if not len(results):
        return fallback_url
    return results[0]['url']


# amazon's search results were too fickle to run a test suite on, If you
# want to include links to books or media, I suggest you just append 'amazon'
# to a google search of the amazon query.
def amazon_processor(query):
    """Default amazon link processor, finds links of type 'amazon' and does
    a query on Amazon to find the book link.  Slightly less nice than the
    google link processor, for now this scrapes amazon's site.  If it fails,
    it falls back on providing the url of the search."""
    from urllib2 import Request, urlopen
    from urllib import urlencode
    try: import lxml.html
    except:
        sys.stderr.write('lxml required for amazon link processor.')
        return query
    q = urlencode({'field-keywords': query})
    url = "http://www.amazon.com/s/ref=nb_ss_gw?url=search-alias%%3Daps&%s" % q
    req = Request(url, headers=firefox_headers)
    response = urlopen(req).read()
    html = lxml.html.fromstring(response)
    link = html.cssselect('div.productData div.productTitle a')
    if not len(link):
        return url
    return link[0].items()[0][1]

enabled_link_processors = set([google_processor])

google_referer = None
def set_google_referer(ref):
    """Set the referer for the google search API.  If the referer is set to
    False, the google link processor will return "I'm feeling lucky" pages."""
    global google_referer
    google_referer = ref

def enable_link_processor(func, tag=None):
    """Enable a function as a link processor.  If no tag is supplied, it is
    added without one, and the tag for that processor will be the part of its
    __name__ before the first underscore."""
    if tag: func.tag = tag
    enabled_link_processors.add(func)

def disable_link_processor(func):
    """Disable link processors.  If a function is passed, that function is
    removed from the set of enabled link processors.  If a string is passed,
    any processors whose name or tags start with that string are disabled."""
    if isinstance(func, basestring):
        rem = []
        for proc in enabled_link_processors:
            if proc.__name__.startswith(func):
                rem.append(proc)
            elif hasattr(proc, 'tag') and proc.tag.startswith(func):
                rem.append(proc)
        for r in rem:
            try: enabled_link_processors.remove(func)
            except KeyError: pass
    else:
        try: enabled_link_processors.remove(func)
        except KeyError: pass

