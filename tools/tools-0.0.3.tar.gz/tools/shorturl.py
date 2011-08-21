from urllib2 import urlopen, Request
import urllib
import simplejson
import logging

def get(url, service='bit.ly', login=None, api_key=None):
    "Only goo.gl are supported now"

    if service == 'goo.gl':
        api_url = 'https://www.googleapis.com/urlshortener/v1/url'
        if api_key:
            api_url += '?key=%s' % api_key
        post = simplejson.dumps({'longUrl': url})
        headers = {'Content-Type': 'application/json'}
        resp = urlopen(Request(api_url, post, headers)).read()
        return simplejson.loads(resp)['id']
    elif service == 'bit.ly':
        api_url = 'http://api.bitly.com/v3/shorten?login=%s&apiKey=%s&longUrl=%s&format=json'
        url = api_url % (login, api_key, urllib.quote(url))
        response = urllib.urlopen(url).read()
        parsed = simplejson.loads(response)
        if parsed['status_code'] != 200:
            raise Exception('Short Url error: %s' % parsed['status_txt'])
        return parsed['data']['url']
