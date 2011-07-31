#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       items.py
#       
#       Copyright 2011 Bidossessi Sodonon <bidossessi.sodonon@yahoo.fr>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       
from gi.repository import GObject
from functions  import make_time, make_uuid, make_path

class Category:
    def __init__(self, **kw):
        self.name    = kw.get('name')
        self.id      = make_uuid(kw.get('name'))
        self.feeds = []

class Feed:
    
    bozo_invalid = ['urlopen', 'Document is empty']

    def __init__(self, **kw):
        self.id          = make_uuid(kw.get('url'))
        self.url         = kw.get('url')
        self.name        = kw.get('name') or kw.get('url')
        self.category_id = kw.get('category') or 'uncategorized'
        self.timestamp   = kw.get('timestamp') or time.time()
        self.parse       = kw.get('parse') or True
        self.f           = None
        self.articles    = []

    def parse(self, interval):
        """Returns True if parsing was allowed and successfull."""
        now = time.time()
        elapsed = now - self.timestamp
        if elapsed < interval:
            return False
        try:
            self.f = feedparser.parse(self.url)
        except:
            return False
        if(hasattr(self.f.feed,'title')):
            self.name = self.f.feed.title.encode('utf-8')    
        if hasattr(self.f,'bozo_exception'): # Feed HAS a bozo exception...
            for item in bozo_invalid:
                if item in str(self.f.bozo_exception):
                    return False
        
class Article:
    def __init__(self, **kw):
        self.id          = make_uuid(kw.get('url'))
        self.title       = kw.get('title')
        self.url         = kw.get('url')
        self.content     = kw.get('content')
        self.date        = kw.get('date')
        self.read        = kw.get('read') or False
        self.starred     = kw.get('starred') or False
        self.feed_id     = kw.get('feed_id')
        self.images    = []

class Image:
    def __init__(self, **kw):
        self.id         = None
        self.local_path = None
        self.url        = kw.get('url')
        self.article_id = kw.get('article_id')
