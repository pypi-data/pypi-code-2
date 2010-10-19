# -*- coding: utf-8 -*-
# feed2mb
# Copyright (C) 2009 EBC - Empresa Brasil de Comunicação
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tweepy
from tweepy.error import TweepError
import readrss
from shortener import services, ShortenerException
from httplib import BadStatusLine
from urllib2 import HTTPError, URLError
import simplejson
import time
import re
import logging
log = logging.getLogger(__name__)

class Microblog(object):
    def strip_tags(self,value):
        "Return the given HTML with all tags stripped."
        txt = re.sub(r'<[^>]*?>', '', value.replace('\t','').replace('\n','')) 
        return txt.replace('(Comments)','')

    def update(self):
        log.info ('searching new items to publish on ' + self.alias)
        lastread = self.rss.getlastRead()
        if not lastread:
            log.info ("There's no record of previous update on " + self.alias)
            log.info ('new items to update: ' + str(self.items))

            items = self.rss.feed['items'][:self.items]
            items.reverse()
            self.postIt(items)
        else:
            try:
                lista = [item for item in self.rss.feed['items'] if item['published_parsed'] > lastread]
            except:
                lista = [item for item in self.rss.feed['items'] if item['updated_parsed'] > lastread]
            lista.reverse()
            log.info ('items to update: ' + str(len(lista)))
            self.postIt(lista)

    def postIt(self, items):
        oldItems = pItems = 0
        for it in items:
            if self.mode == 'title':
                try:
                    short_address = self.shortener.short(it["link"])	   
                except (ShortenerException):
                    continue
		txt_size = 140 - (len(short_address)+1)
                txt = it["title"][0:txt_size] + " " + short_address
            elif self.mode == 'text':
                try:
                    txt = self.strip_tags(it.content[0].value)[0:140]
                except:
                    txt = self.strip_tags(it.summary)[0:140]
            else:
                txt = it['title'][0:144] + " " + tiny(it['link'])
            try:
                status = self.api.update_status(txt)
                self.rss.updateLastRead(it)
                log.info(status.text + " posted on " + self.alias)
                time.sleep(5)

            except (TweepError), e:
                log.debug(e.reason)
                try:
                    if e.reason == 'Status is a duplicate.':
                        self.rss.updateLastRead(it)
                except:
                    pass
                #lets try in the next time
                continue

class WordpressAPI(object):
    def __init__(self,username = None, password = None, xmlrpc_url = None):
        import pyblog
        self.blog = pyblog.WordPress(xmlrpc_url, username, password)

    def PostUpdate(self,post):
        self.blog.new_post(post)
        status = type('',(),{})() 
        status.text = post['title']
        return status


class IdenticaAPI(object):

    _API_REALM = 'Identi.ca API'

    def PostUpdate(self, text):
        from twitter import Status
        from twitter import TwitterError
        '''Post a twitter status message from the authenticated user.
        
        The twitter.Api instance must be authenticated.

        Args:
        text: The message text to be posted.  Must be less than 140 characters.

        Returns:
        A twitter.Status instance representing the message posted
        '''
        if not self._username:
            raise TwitterError("The twitter.Api instance must be authenticated.")
        if len(text) > 140:
            raise TwitterError("Text must be less than or equal to 140 characters.")
        url = 'https://identi.ca/api/statuses/update.json'
        data = {'status': text}
        json = self._FetchUrl(url, post_data=data)
        data = simplejson.loads(json)
        return Status.NewFromJsonDict(data)

    def _GetOpener(self, url, username=None, password=None):
        import urlparse, urllib2
        if username and password:
            self._AddAuthorizationHeader(username, password)
            handler = self._urllib.HTTPBasicAuthHandler()
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
            handler.add_password(IdenticaAPI._API_REALM, netloc, username, password)
            opener = self._urllib.build_opener(handler)#,urllib2.HTTPHandler(debuglevel=1))
        else:
            opener = self._urllib.build_opener()
            opener.addheaders = self._request_headers.items()
        return opener


class Twitter(Microblog):
    def __init__(self, url='',service='',section='', interval='',mode='title', items = 5, shortener='tinyurl',oauth_secret='',oauth_token='',consumer_secret='',consumer_key='',pidfile=''):
        self.mode = mode
        self.alias = section
        self.url = url
        self.items = items
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(oauth_token, oauth_secret)
        self.api = tweepy.API(auth)
        self.rss = readrss.parse(url,self.__class__.__name__.lower(), self.alias)
        self.shortener = services[shortener]()

class Identica(Microblog):
    def __init__(self,  alias, url, username, passwd, mode='title', items = 5, shortener='tinyurl'):
	self.alias = alias
        self.mode = mode
        self.url = url
        self.items = items
        self.username = username
        self.passwd = passwd
        self.api = IdenticaAPI(username=self.username, password=self.passwd)
        self.rss = readrss.parse(url,self.__class__.__name__.lower(), self.alias)
        self.shortener = services[shortener]()

class Wordpress(Microblog):
    def __init__(self,  alias, url, username, passwd, mode='title', items = 5, shortener='tinyurl', xmlrpc_url=None):
	self.alias = alias
        self.mode = mode
        self.url = url
        self.items = items
        self.username = username
        self.passwd = passwd
        self.api = WordpressAPI(username=self.username, password=self.passwd, xmlrpc_url= xmlrpc_url)
        self.rss = readrss.parse(url,self.__class__.__name__.lower(), self.alias)
        self.shortener = services[shortener]()

    def postIt(self, items):
        oldItems = pItems=0
        for it in list(items):
            post={}
            post['title'] = it['title']
            try:
                post['description'] = it.content[0].value
            except:
                post['description'] = it.summary
            post['description'] += '<p><a href="' + it['links'][-1]['href'] + '">Original</a></p>'
            try:
                status = self.api.PostUpdate(post)
                self.rss.updateLastRead(it)
                log.info(status.text + " posted on " + self.alias)
                time.sleep(5)

            except (BadStatusLine, HTTPError):
                #lets try in the next time
                return

class service(object):
    def __init__(self,**kwargs):
        if kwargs['service'] == 'twitter':
            self.micro = Twitter(**kwargs)
        elif kwargs['service'] == 'identica':
            self.micro = Identica(kwargs['section'], kwargs['url'],kwargs['username'],kwargs['password'],kwargs['mode'],kwargs['items'],kwargs['shortener'])
        elif kwargs['service'] == 'wordpress':
            self.micro = Wordpress(kwargs['section'], kwargs['url'],kwargs['username'],kwargs['password'],kwargs['mode'],kwargs['items'],kwargs['shortener'], kwargs['xmlrpc_url'])

    def get(self):
        return self.micro
