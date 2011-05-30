#!/usr/bin/env python

"""Python interface to the Discogs music information database."""

import urllib, urllib2, gzip, cStringIO
import xml.etree.ElementTree as ET
from argparse import ArgumentParser

DISCOGS_API_KEY = 'f1e79f104f'
MULTI_DELIMITER = ' / '

def urlopen_gzip(url): #{{{1
    req = urllib2.Request(url)
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
    return urllib2.urlopen(req)

def get_arguments(): #{{{1
    args = ArgumentParser()
    args.add_argument('-v', '--verbose', action='store_true', default=False, help='be verbose')
    args.add_argument('-r', '--release', help='set release')
    args.add_argument('-q', '--query', help='display a specific attribute')
    return args.parse_args()

def main(): #{{{1
    args = get_arguments()
    d = Discogs(DISCOGS_API_KEY)
    if args.release:
        release = d.release(args.release)
        if args.query:
            query = getattr(release, args.query)
            if type(query) in (tuple, list):
                print MULTI_DELIMITER.join(query)
            else:
                print query

#}}}1

class Discogs(object): #{{{1

    def __init__(self, api_key):
        self.api_key = api_key
        self.url_base = 'http://www.discogs.com'

    def url(self, operation, operand):
        return '%s/%s/%s?%s' % (
                self.url_base,
                operation,
                urllib.quote_plus(str(operand)),
                urllib.urlencode({'api_key': self.api_key, 'f': 'xml',})
                )

    def root(self, name, value):
        url = self.url(name, value)
        print url
        return ET.parse(urlopen_gzip(url)).getroot().find(name)

    def artist(self, artist):
        return Artist(self.root('artist', artist))

    def release(self, release):
        return Release(self.root('release', release))



class DiscogsXML(object): #{{{1

    def __init__(self, root):
        self.root = root
        self.load()

    def load(self):
        pass



class Artist(DiscogsXML): #{{{1

    def load(self):
        self.name = self.root.find('name').text
        self.releases = {}
        for element in self.root.findall('releases/release'):
            if element.get('type') != 'Main': continue
            self.releases[int(element.get('id'))] = element.find('title').text



class Image(DiscogsXML): #{{{1

    def load(self):
        self.height = int(self.root.get('height'))
        self.width = int(self.root.get('width'))
        self.type = self.root.get('type')
        self.url = self.root.get('uri')
        self.url_small = self.root.get('uri150')



class Release(DiscogsXML): #{{{1

    def load(self):
        self.id = int(self.root.get('id'))
        self.genres = []
        self.genres.extend(e.text for e in self.root.findall('genres/genre'))
        self.genres.extend(e.text for e in self.root.findall('styles/style'))
        self.images = [Image(e) for e in self.root.findall('images/image')]

#}}}1

if __name__ == '__main__': main()
