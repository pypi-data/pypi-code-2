#!/usr/bin/python
#  -*- coding=utf-8 -*-
"""
This file is part of Pynav.

Pynav is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pynav is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Pynav. If not, see <http://www.gnu.org/licenses/lgpl.html>.

Copyright 2009-2011 Sloft http://bitbucket.org/sloft/pynav
"""

import re
from formdumper import FormDumper
from datetime import datetime
from urlparse import urlparse

class Response(object):
    """Contains HTTP headers infos and response data"""
    
    def __init__(self, browser, read=True):
        self.browser = browser
        self.handle = browser.handle
        self.headers = self.handle.headers
        self.max_page_size = browser.max_page_size
        self.values = self.post = self.handle.values
        self.real_url = self.handle.geturl()
        self.relative_url = self.real_url.replace(self.real_url.split('/')[-1], '')
        up = urlparse(self.real_url)
        self.root_url = "{scheme}://{netloc}/".format(scheme=up.scheme, netloc=up.netloc)
        self.status_code = self.handle.getcode()
        self.status_message = self.handle.msg
        self.content_type = None
        if 'Content-Type' in self.headers:
            self.content_type = self.headers['Content-Type']
        self.content_length = None
        if 'Content-Length' in self.headers:
            self.content_length = self.headers['Content-Length']
        date = self.headers.getdate('Date')
        self.date = None
        if(isinstance(date, tuple)):
            self.date = datetime(*date[:7])
        date = self.headers.getdate('Last-Modified')
        self.last_modified = None
        if(isinstance(date, tuple)):
            self.last_modified = datetime(*date[:7])
        self.fd = None
        self.data = ''
        self.read(read)
    
    def read(self, read=True):
        """Read the handle if not already done"""
        if read and self.data is '':
            if self.content_type_allowed():
                self.data = self.handle.read(self.max_page_size)
                return True
            else:
                print "Content-Type {content_type} is not allowed !".format(content_type=self.content_type)
        return False
        
    def search(self, reg):
        """Search a regex in the page, return a boolean"""
        return re.search(reg, self.data)
    
    def find(self, reg):
        """Return the result found by the regex"""
        res = re.findall(reg, self.data, re.S)
        if len(res)==1:
            return res[0]
        else:
            return res
    
    def find_all(self, reg):
        """Return all results found by the regex"""
        return re.findall(reg, self.data, re.S)
    
    @property
    def links(self):
        return self.get_links()

    def get_links(self, reg = None):
        """Return a list of all get_links found, a regex can be used"""
        links = re.findall('href="(.*?)"', self.data)
        if reg:
            def match(link): return len(re.findall(reg, link)) > 0
            return [self._add_path(link) for link in links if match(self._add_path(link))]
        else:
            return [self._add_path(link) for link in links]
    
    @property
    def images(self):
        return self.get_images()
    
    def get_images(self, reg = None):
        """Return a list of all images found, a regex can be used"""
        images = re.findall('img.*?src="(.*?)"', self.data)
        if reg:
            def match(image): return len(re.findall(reg, image)) > 0
            return [self._add_path(image) for image in images if match(self._add_path(image))]
        else:
            return [self._add_path(image) for image in images]
    
    def strip_tags(self, html=None):
        """Strip all tags of an HTML string and return only texts"""
        if html is None:
            html = self.data
        intag = [False]
        def chk(c):
            if intag[0]:
                intag[0] = (c != '>')
                return False
            elif c == '<':
                intag[0] = True
                return False
            return True
        return ''.join(c for c in html if chk(c))
    
    def save(self, destination):
        """Save the page to a file"""
        f = open(destination, 'w')
        try:
            f.write(self.data)
        finally:
            f.close()

    def dump_form(self, form_number=None):
        """Dump a form with FormDumper
           Becareful: FormDumper need to reloaded the page with the same GET/POST values"""
        handle = self.browser.open(self.real_url, self.values)
        if self.fd is None:
            self.fd = FormDumper(handle=handle)
        if form_number is not None:
            self.fd.dump(form_number)
    
    def dump_forms(self):
        """Dump all forms with FormDumper
           Becareful: FormDumper need to reloaded the page with the same GET/POST values"""
        handle = self.browser.open(self.real_url, self.values)
        if self.fd is None:
            self.fd = FormDumper(handle=handle)
        self.fd.dump_all()

    def formDumper(self, verbose_level=1):
        """Return a FormDumper object"""
        handle = self.browser.open(self.real_url, self.values)
        self.fd = FormDumper(handle=handle, verbose_level=verbose_level)
        return self.fd
    
    def _add_path(self, url):
        """Correct an url depending on the link, internal use"""
        if re.search('://', url):
            return url
        else:
            if re.search('mailto:', url):
                return url
            if url == '':
                return self.root_url
            if url[0] == '/':
                return self.root_url[:-1]+url
            else:
                return self.relative_url+url
    
    def content_type_allowed(self):
        """Return True if the current Content-Type is allowed by the Browser isntance""" 
        if len(self.browser.allowed_content_types) == 0:
            return True
        elif len(self.browser.allowed_content_types) > 0:
            found = [c for c in self.browser.allowed_content_types if self.content_type.startswith(c)]
            return len(found)>0
        else:
            return False
    
    def __str__(self):
            return self.data

