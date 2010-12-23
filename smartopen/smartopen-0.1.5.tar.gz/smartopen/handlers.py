import address
import string
import urllib
import urllib2

class Location(object):
    """
    generic class for locations
    """

    def __init__(self, baseurl=""):
        self.baseurl = baseurl

    def url(self, query):
        return self.baseurl + self.process(query)

    def process(self, query):
        return query

    def test(self, query):
        return True

    def exists(self, URL):
        """does a URL exist?"""
        try:
            urllib.urlopen(URL)
            return True
        except IOError:
            return False

class URL(Location):
    """a straight URL"""

    def process(self, query):
        if '://' in query:
            return query
        return 'http://' + query

    def test(self, query):
        """try to open the url"""
        if ' ' in query or '\n' in query:
            return False
        return self.exists(self.process(query))

class GoogleMaps(Location):
    """try to google-maps the address"""

    def __init__(self):
        gmapsurl='http://maps.google.com/maps?f=q&hl=en&q='
        Location.__init__(self, gmapsurl)

    def process(self, query):
        theaddress = address.normalizeaddress(query)
        if not theaddress:
            return theaddress
        return urllib.quote_plus(theaddress)

    def test(self, query):
        return bool(self.process(query))

class Trac(Location):
    def __init__(self, baseurl):
        baseurl = baseurl.strip('/') + '/'
        Location.__init__(self, baseurl)

    def process(self, query):
        if query[0] == 'r':
            if query[1:].isdigit():
                return 'changeset/' + str(query[1:])
        if query[0] == '#':
            if query[1:].isdigit():
                return 'ticket/' + str(query[1:])

    def test(self, query):
        return bool(self.process(query))
        

class Wikipedia(Location):
    """try to open the query in wikipedia"""
    def __init__(self):        
        wikiurl = 'http://en.wikipedia.org/wiki/'
        Location.__init__(self, wikiurl)

    def process(self, query):
        return urllib.quote_plus('_'.join(query.split()))
        
    def test(self, query):
        'test to see if the article exists'

        # need a phony user agent so wikipedia won't know we're a bot
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.0.4) Gecko/20060508 Firefox/1.5.0.4'

        request = urllib2.Request(self.url(query), None, headers)
        try:
            f = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            return False

        if 'Wikipedia does not have an article with this exact name' in f:
            return False
        return True

class Wiktionary(Location):
    def __init__(self):
        baseurl = 'http://en.wiktionary.org/wiki/'
        Location.__init__(self, baseurl)
    def test(self, query):
        for c in (' ', '\n', '/'):
            if c in query:
                return False
        if self.exists(self.url(query)):
            return True
        
class Bugzilla(Location):
    def __init__(self):
        baseurl = 'https://bugzilla.mozilla.org/show_bug.cgi?id='
        Location.__init__(self, baseurl)
    
    def test(self, query):
        try:
            int(query)
            return True
        except:
            return False

class Google(Location):
    def __init__(self):        
        googleurl = 'http://www.google.com/search?hl=en&q='
        Location.__init__(self, googleurl)
        
    def process(self, query):
        return urllib.quote_plus(query)

class FedEx(Location):
    def __init__(self):
        baseurl = 'http://www.fedex.com/Tracking?cntry_code=us&language=english&tracknumber_list='
        Location.__init__(self, baseurl)

    def process(self, query):
        if query.count(' ') == 2:
            query = ''.join(query.split(' '))        
        return query

    def test(self, query):
        query = self.process(query)
        if len(query) != 12:
            return False
        try:
            int(query)
        except ValueError:
            return False
        return True

class MercurialRevision(Location):
    def __init__(self):
        baseurl = 'http://hg.mozilla.org/mozilla-central/rev/'
        Location.__init__(self, baseurl)

    def test(self, query):
        query = set(query)
        if query.issubset(string.digits + 'abcdef'):
            return True
        return False
