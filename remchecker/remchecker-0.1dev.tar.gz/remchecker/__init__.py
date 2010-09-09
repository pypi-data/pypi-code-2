#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import sys

import yaml
import tweepy


CONSUMER_KEY = 'NMaOvEn0u8QSwhxiGGY0rg'
CONSUMER_SECRET = 'FtY5BbJkaotQQDjUCEutCBk8fL8E8dH67fhKh07dkQ'
CONFIG = os.path.expanduser('~/.remchecker.yml')
MESSAGE = u'%s にリムーブされました'


def init(filename):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    print 'Please authorize us: %s' % auth.get_authorization_url()
    verifier = raw_input('PIN: ').strip()
    access_token = auth.get_access_token(verifier)
    api = tweepy.API(auth)
    data = dict(
        key = access_token.key,
        secret = access_token.secret,
        followers = list(str(user.screen_name) for user in tweepy.Cursor(api.followers).items())
    )

    with open(filename, 'w') as f:
        yaml.dump(data, f, encoding='utf8')


def update(filename):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    data = {}
    prev = set()
    with open(filename) as f:
        data = yaml.load(f.read().decode('utf8'))
        auth.set_access_token(data['key'], data['secret'])
        prev = set(data['followers'])
    api = tweepy.API(auth)
    current = set(str(user.screen_name) for user in tweepy.Cursor(api.followers).items())
    users = []
    diff = prev - current
    for s in diff:
        if users and len(users[-1])+len(s)+2+len(MESSAGE) < 140:
            users[-1] += ' @'+s
        else:
            users.append('@'+s)

    if diff:
        sys.stderr.write("removed by "+', '.join('@'+u for u in diff)+'\n')

    myname = api.me().screen_name
    for s in users:
        api.send_direct_message(screen_name=myname, text=MESSAGE.encode('utf8') % s)

    data['followers'] = list(current)
    with open(filename, 'w') as f:
        yaml.dump(data, f, encoding='utf8')


def main():
    if not os.path.exists(CONFIG):
        init(CONFIG)
    else:
        update(CONFIG)
