# -*- coding: utf-8 -*-

#działający key i secret zarejestrowanej przeze mnie aplikacji, można testować

CONSUMER_KEY = '9IIoLsjrHKW9cAIePhvw'
CONSUMER_SECRET = 'YMk75YklVYnwAYDllJP2WM2H8ktZFBUN2fumv5K6'

from oauth import oauth
from blipapi import BlipApi

consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)

# poniższą wartość można skopiować z wyniku działania skryptu token_req.py

access_token = oauth.OAuthToken.from_string("oauth_token_secret=.....................&oauth_token=................")

api = BlipApi(oauth_token = access_token, oauth_consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET))

print api.dashboard_read(limit=1)
print
print api.dirmsg_create(u'dirmsg test', 'mrk')
