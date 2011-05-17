from urllib2 import urlopen, Request
import simplejson
import logging

def get(url, api_key=None):
    "Only goo.gl are supported now"

    api_url = 'https://www.googleapis.com/urlshortener/v1/url'
    if api_key:
        api_url += '?key=%s' % api_key
    post = simplejson.dumps({'longUrl': url})
    headers = {'Content-Type': 'application/json'}
    resp = urlopen(Request(api_url, post, headers)).read()
    return simplejson.loads(resp)['id']
