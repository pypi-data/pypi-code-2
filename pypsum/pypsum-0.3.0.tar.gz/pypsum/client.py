from urllib import unwrap
from urlparse import urlparse
from cgi import parse_header
import requests
from . import settings
try:
    import json
except ImportError:
    import simplejson as json
try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                import cElementTree as etree
            except ImportError:
                import elementtree.ElementTree as etree

class Response(object):
    def __init__(self, response):
        self._next = None
        link, params = parse_header(response.headers.get('link', ''))
        if params.get('rel','').strip('"\'') == 'next':
            self._next = unwrap(link)

    @property
    def next(self):
        return self._next

    @property
    def content(self):
        return self._loremipsum

class JsonResponse(Response):
    def __init__(self, response):
        Response.__init__(self, response)
        self._loremipsum = json.loads(response.content)['loremipsum']

    @property
    def generation_time(self):
        return float(self._loremipsum['header']['generation_time'])

    @property
    def words(self):
        return int(self._loremipsum['header']['words'])

    @property
    def sentences(self):
        return int(self._loremipsum['header']['sentences'])

    @property
    def paragraphs(self):
        return int(self._loremipsum['header']['paragraphs'])

    @property
    def text(self):
        return [b.values()[0] for b in self._loremipsum['body']]

class XMLResponse(Response):
    def __init__(self, response):
        Response.__init__(self, response)
        self._loremipsum = etree.ElementTree(etree.fromstring(response.content))

    @property
    def generation_time(self):
        return float(self._loremipsum.find('header/generation_time').text)

    @property
    def words(self):
        return int(self._loremipsum.find('header/words').text)

    @property
    def sentences(self):
        return int(self._loremipsum.find('header/sentences').text)

    @property
    def paragraphs(self):
        return int(self._loremipsum.find('header/paragraphs').text)

    @property
    def text(self):
        return [b.text for b in self._loremipsum.find('body').iter()]

class Client(object):
    def __init__(self, url, accepts='application/json'):
        self.url = url
        self.accepts = accepts

    def get(self, **params):
        result = {
            'generation_time': 0,
            'words': 0,
            'sentences': 0,
            'paragraphs': 0,
            'text': []}
        headers = {'Accept': self.accepts, 'User-Agent': 'pypsum-client'}
        build = {
            'application/json': JsonResponse,
            'application/xml': XMLResponse}.get(self.accepts)
        scheme, netloc = urlparse(self.url)[:2]
        more = self.url
        query = params
        while more:
            response = requests.get(more, params=query, headers=headers)
            response.raise_for_status()
            loremipsum = build(response)
            for key in result:
                result[key] += getattr(loremipsum, key)
            try:
                path, query = loremipsum.next.split('?')
            except ValueError:
                path, query = loremipsum.next, {}
            more = '%s://%s%s' % (scheme, netloc, path) if path else ''
        return result

    def __call__(self, **params):
        return self.get(**params)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self[name]

    def __getitem__(self, name):
        return Client('%s/%s' % (self.url, name), self.accepts)

# from pypsum import client
#
# pypsum = client.pypsum()
# pypsum.generate[15].lipsum.sentences()
# pypsum.generator.get(amount=15, text_start='lipsum', text_type='sentences')
#
def pypsum(url=None, accepts=None):
    url = url or 'http://' + settings.application_location
    accepts = accepts or settings.client_accepts
    return Client(url, accepts)
