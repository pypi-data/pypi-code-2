#!/usr/bin/env python
from xml.dom.minidom import parse
from xml.parsers.xmlproc import xmldtd
from xml.parsers.xmlproc import xmlproc
from xml.parsers.xmlproc import xmlval
from urlparse import urljoin
from urllib import urlopen, urlencode
from mx.DateTime.ISO import ParseDateTimeUTC as parseutc
from datetime import datetime
import os

#TODO DTD caching of well known dtd's should occur in xmlproc, so hardcoding
#     isn't needed.
SITEMAP_URL = 'http://www.cwi.nl/sitemap.xml'
DTD = os.path.join(os.path.dirname(__file__), 'dtd', 'xhtml1-strict.dtd')


def parsedatetime(s):
    return datetime.fromtimestamp(parseutc(s))


def loc(url):
    'Get the loc string from an url-node.'
    locs = url.getElementsByTagName('loc')
    if len(locs) > 1:
        raise Exception('More than 1 loc in url %s' % url.nodeValue)
    if len(locs) < 1:
        raise Exception('No loc in url %s' % url.nodeValue)
    for node in locs[0].childNodes:
        if node.nodeType == node.TEXT_NODE:
            return node.nodeValue


def lastmod(url):
    'Get the datetime the url was modified or None.'
    lastmod = url.getElementsByTagName('lastmod')
    if len(lastmod) > 1:
        raise Exception('More than 1 lastmod in url %s' % url.nodeValue)
    if len(lastmod) < 1:
        return None
    for node in lastmod[0].childNodes:
        if node.nodeType == node.TEXT_NODE:
            return parsedatetime(node.nodeValue)


def get_urls_from_sitemap(file, baseurl='', since=None):
    rv = []
    if type(file) in (str, unicode):
        baseurl = file
        file = urlopen(file)
    doc = parse(file)
    for url in doc.getElementsByTagName('url'):
        if since == None:
            rv.append(urljoin(baseurl, loc(url)))
        else:
            lm = lastmod(url)
            if not lm or lm > since:
                rv.append(urljoin(baseurl, loc(url)))
    return rv


class ValidationError(Exception):
    def __repr__(self):
        return '%s @ Line %s, Column %s: %s' % (self.args[0],\
             self.args[2][0], self.args[2][1], self.args[1])


class ErrorHandler(xmlval.ErrorHandler):
    def location(self):
        return self.get_locator().get_line(), self.get_locator().get_column()

    def warning(self, msg):
        raise ValidationError('Warning', msg, self.location())

    def error(self, msg):
        raise ValidationError('Error', msg, self.location())

    def fatal(self, msg):
        raise ValidationError('Fatal', msg, self.location())


def validate(file):
    """Validate the xml in file.

    The file argument can be a url.
    """
    if type(file) in (str, unicode):
        file = urlopen(file)
    # parser = xmlval.XMLValidator() # this will hit w3.org for the DTD

    # FIXME this hardwires to xhtml1-stict
    dtd = xmldtd.load_dtd(DTD)
    parser = xmlproc.XMLProcessor()
    parser.set_application(xmlval.ValidatingApp(dtd, parser))
    parser.dtd = dtd
    parser.ent = dtd

    parser.set_error_handler(ErrorHandler(parser))
    parser.read_from(file)


def w3c_url(url):
    'Get the W3C markup validator URL that checks url.'
    rv = 'http://validator.w3.org/check?'
    rv += urlencode({'verbose': 1, 'uri': url})
    return rv


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Crawl a sitemap.xml and validate the documents")
    parser.add_argument('SITEMAP_URL')
    args = parser.parse_args()
    errors = []
    for url in get_urls_from_sitemap(args.SITEMAP_URL):
        import re
        if re.match(r'http://www.cwi.nl/people/\d+.*', url):
            continue
        try:
            validate(url)
        except ValidationError, e:
            errors.append((url, e))
            print w3c_url(url)

if __name__ == '__main__':
    main()
