# -*- coding: utf-8 -*-
CONSUMER_KEY = '9IIoLsjrHKW9cAIePhvw'
CONSUMER_SECRET = 'YMk75YklVYnwAYDllJP2WM2H8ktZFBUN2fumv5K6'

request_token_url = 'http://blip.pl/oauth/request_token'
access_token_url = 'http://blip.pl/oauth/access_token'
authorize_url = 'http://blip.pl/oauth/authorize'

from oauth import oauth
import urllib2

opener = urllib2.build_opener()
consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
signature = oauth.OAuthSignatureMethod_HMAC_SHA1()
oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url=request_token_url)
oauth_request.sign_request(signature, consumer, None)

req = urllib2.Request(oauth_request.to_url())
data = opener.open(req)
resp = data.read()
print resp
token = oauth.OAuthToken.from_string(resp)
print 'request token:', token

oauth_request = oauth.OAuthRequest.from_token_and_callback(token = token, http_url = authorize_url)
print "\nOdwiedź ten url i zaakceptuj dostęp do konta:\n%s\n"%oauth_request.to_url()

print "podaj wartosc parametru oauth_verifier z url'a zwrotnego"
verifier = raw_input()
oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, verifier=verifier, http_url = access_token_url)
oauth_request.sign_request(signature, consumer, token)
req = urllib2.Request(oauth_request.to_url())
data = opener.open(req)
access_token = oauth.OAuthToken.from_string(data.read())

print "access token:\n",access_token
