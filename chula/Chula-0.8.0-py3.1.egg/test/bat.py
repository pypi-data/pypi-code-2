"""Class for use with Basic Acceptance Testing"""

# Python imports
import unittest
import urllib.request, urllib.error, urllib.parse

# Chula imports
from chula import collection

#class RedirectHandler(urllib2.HTTPRedirectHandler):
#    def http_error_301(self, req, fp, code, msg, headers):
#        upstream = urllib2.HTTPRedirectHandler.http_error_301
#        result = upstream(self, req, fp, code, msg, headers)
#        result.code = code
#        return result
#
#    def http_error_302(self, req, fp, code, msg, headers):
#        upstream = urllib2.HTTPRedirectHandler.http_error_302  
#        result = upstream(self, req, fp, code, msg, headers)
#        result.code = code
#        return result

class Bat(unittest.TestCase):
    def request(self, url):
        if not url.startswith('http://'):
            url = 'http://localhost:8080' + url

        #opener = urllib2.build_opener(RedirectHandler())
        #response = opener.open(url)

        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as ex:
            response = ex
        except urllib.error.URLError as ex:
            response = ex

        retval = collection.Collection()
        retval.data = response.read().decode()
        retval.status = response.code
        retval.headers = response.headers

        return retval
