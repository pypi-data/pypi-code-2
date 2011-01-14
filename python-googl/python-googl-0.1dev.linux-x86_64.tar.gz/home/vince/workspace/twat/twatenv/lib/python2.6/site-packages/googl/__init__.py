import httplib2
import urllib

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("You need to have a json parser, easy_install simplejson")

class Googl:
    """Access Goo.gl url shorten"""

    def __init__(self, key=None, baseurl="https://www.googleapis.com/urlshortener/v1/url"):
        self.key = key
        self.conn = httplib2.Http()
        self.baseurl = baseurl

    def _request(self, url="", method="GET", body="", headers=None):
        """send request and parse the json returned"""
        if not url:
            url = self.baseurl
        elif not url.startswith("http"):
            url = "%s?%s" % (self.baseurl, url)
        if self.key is not None:
            url +=  "%s%s" % ( ("?" if "?" not in url else "&"), "key=%s" % self.key)

        return json.loads(self.conn.request(url, method, body=body, headers=headers or {})[1])

    def shorten(self, url):
        """shorten the url"""
        body =json.dumps(dict(longUrl=url))
        headers = {'content-type':'application/json'}
        return self._request(method="POST", body=body, headers=headers)

    def expand(self, url, analytics=False):
        """expand the url"""
        data = dict(shortUrl=url)
        if analytics:
            data['projection'] = 'FULL'
        url = urllib.urlencode(data)
        return self._request(url)

