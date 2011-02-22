#!/usr/bin/python
#  -*- coding=utf-8 -*-
'''
Created on 15 nov. 2009

@author: Sloft

Licence : GNU General Public License (GPL)

This file is kept for backward compatibility (Pynav-0.6 branch)
Pynav 0.6 is no longer maintained, you should use the new version (Pynav-0.7 branch)
'''

from __future__ import with_statement #for Python 2.5 compatibility
import os
import re
import time
import random
import socket
import urllib
import urllib2
import httplib
import urlparse
import cookielib
try:
    import cPickle as pickle
except ImportError:
    import pickle

class Pynav(object):
    """Programmatic web browser to fetch data and test web sites"""
    version = '0.6.5'
    verbose = False
    
    def __init__(self, timeout=None, proxy=None):
        """ Constructor, many attributes can be used """
        self.temps_min = 0
        self.temps_max = 0
        self.max_page_size = 500000
        self.max_history = 200
        self.verbose = False
        self._set_user_agents_list()
        # Add that as an __init__ argument and remove the 'user_agents_list'
        self.user_agent = self.user_agent_list['firefox']['windows']
        self._headers = {'User-Agent' : self.user_agent}
        self._auto_referer = False
        self._cookie_jar = cookielib.CookieJar()
        self.proxy = proxy
        self._url_opener = urllib2.build_opener(*self._get_handlers())
        self.history = []
        self.current_page = -1
        self.page_document_type = None
        self.page_info = None
        self.real_url = None
        self.relative_url = None
        self.base_url = None
        self.response = None
        # Pass that to the download function
        self.download_path = os.getcwd()
        if timeout:
            socket.setdefaulttimeout(timeout)
    
    def _get_handlers(self):
        """Private method to get all handlers needed"""
        handlers = []
        handlers.append(urllib2.HTTPCookieProcessor(self._cookie_jar))
        if self.proxy:
            handlers.append(urllib2.ProxyHandler({'http': self.proxy}))
        return handlers
       
    def _set_user_agents_list(self):
        """Private method to set the user agents list"""
        self.user_agent_list = {}
        self.user_agent_list['firefox'] = \
        {'windows' : 'Mozilla/5.0 (Windows; U; Windows NT 6; fr; rv:1.9.1.5) Gecko/Firefox/3.5.5'}
        self.user_agent_list['ie'] = {
            'windows' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Win64; x64; Trident/4.0)'}
    
    def set_http_auth(self, base_url, username, password):
        """Define parameters to set HTTP Basic Authentication"""
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, base_url, username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        self._url_opener.add_handler(handler)

    def _set_referer(self, referer):
        """Decorator to define a referer, the previous visited page"""
        self._headers['Referer'] = referer
    
    def _get_referer(self):
        """Decorator to get the referer, the previous visited page"""
        if self._headers.has_key('Referer'):
            return self._headers['Referer']
        else:
            return None
    
    referer = property(_get_referer, _set_referer)

    def _set_auto_referer(self, auto_referer):
        """Decorator to set the status of the auto_referer attribute"""
        self._auto_referer = auto_referer
        if not auto_referer:
            if self._headers.has_key('Referer'):
                self._headers.pop('Referer')
    
    def _get_auto_referer(self):
        """Decorator to get the status of the auto_referer attribute"""
        return self._auto_referer
    
    autoReferer = property(_get_auto_referer, _set_auto_referer)
    
    def save_history(self, file_name):
        """Save history in a file"""
        with open(file_name, 'w') as f:
            pickle.dump(self.history, f)
    
    def load_history(self, file_name):
        """Load history from a file"""
        try:
            with open(file_name, 'r') as f:
                self.history = pickle.load(f)
        except IOError:
            print "ERROR: file", file_name, "doesn't exist"
    
    def _init_go(self):
        """Private method to initialize some attributes"""
        sleep_time = random.randint(self.temps_min, self.temps_max)
        if self.verbose and sleep_time > 0:
            print 'waiting', sleep_time, 'secs'
        if sleep_time:
            time.sleep(sleep_time)
        if self._auto_referer:
            if len(self.history) > 0:
                self.referer = self.history[self.current_page]['url']
        
    def go(self, url, values = {}):
        """Visite a web page, post values can be used"""
        self._init_go()
        
        if not re.search('://', url):
            url = 'http://' + url
        
        if url.count('/') < 3:
            url = url + '/'
        
        data = urllib.urlencode(values)
        
        if values:
            req = urllib2.Request(url, data, self._headers)
        else:
            req = urllib2.Request(url, headers=self._headers)
        
        self.response = None
        
        handle = None
        try:
            handle = self._url_opener.open(req)
        except urllib2.HTTPError, exception:
            if exception.code == 404:
                print '(404) Page not found !'
            else:           
                print 'HTTP request failed with error %d (%s)' % (
                    exception.code, exception.msg)
        except urllib2.URLError, exception:
            print 'Opening URL failed because:', exception.reason
        except httplib.BadStatusLine, exception:
            print exception.line #print nothing...
            print "BadStatusLine Error! Httplib issue, can't get this page, sorry..."

        if handle:
            # Maybe pack these attributes into the response object?
            self.response = handle.read(self.max_page_size)
            self.handle = handle
            self.page_document_type = handle.info().getheader("Content-Type","")
            self.page_info = handle.info()
            self.real_url = handle.geturl()
            
            if len(self.history) > self.max_history - 1:
                del self.history[0]
            self.current_page = self.current_page + 1
            self.history.append({'url':url, 'post':values, 'response':self.response})
            
            if self.current_page > len(self.history) - 1:
                self.current_page = len(self.history) - 1
            
            self.relative_url = self.real_url.replace(self.real_url.split('/')[-1], '')
            self.base_url = 'http://'+self.real_url[7:].split('/')[0]+'/'
            return self.response
        else:
            # I think this can be removed and simply return None for each
            # except above
            return None #Exception ?
    
    def replay(self, begining=0, end=None, print_url=False, print_post=False, print_response=False):
        """Replay history, can be used after loading history from a file"""
        history, self.history = self.history, []
        if not end:
            end = len(history)
        for page in history[begining:end]:
            self.go(page['url'], page['post'])
            if print_url:
                print page['url']
            if print_post:
                print page['post']
            if print_response:
                print page['response']
    
    def search(self, reg):
        """Search a regex in the page, return a boolean"""
        return re.search(reg, self.response)
    
    # I think this doesn't need to be here, the user can handle that himself
    # by using the response
    def find(self, reg):
        """Return the result found by the regex"""
        res = re.findall(reg, self.response, re.S)
        if len(res)==1:
            return res[0]
        else:
            return res
    
    # I think this doesn't need to be here, the user can handle that himself
    # by using the response
    def find_all(self, reg):
        """Return all results found by the regex"""
        return re.findall(reg, self.response, re.S)
    
    def download(self, url, destination=None):
        """Download the file at a url to a file or destination"""
        if not destination:
            destination = self.download_path
        
        if os.path.isdir(destination):
            if destination[-1] in ('/', '\\'):
                destination = destination + url.split('/')[-1]
            else:
                destination = destination + '/' + url.split('/')[-1]
        else:
            destination = self.download_path + destination

        if self.verbose:
            print 'Downloading to:', destination
        return urllib.urlretrieve(url, destination)

    # I think this doesn't need to be here, the user can handle that himself
    # by using the response
    def save_response(self, destination):
        """Save the page to a file"""
        f = open(destination, 'w')
        try:
            f.write(self.response)
        finally:
            f.close()
    
    def get_cookies(self, web_page=None):
        """This always returns the cookies the current visited URL holds,
           if web_page is specified this will return the cookies this web_page has
           within our browser instance."""
        if not web_page:
            if not self.base_url:
                return None
            else:
                netloc = urlparse.urlparse(self.base_url).netloc
        else:
            netloc = urlparse.urlparse(web_page).netloc
        return self._cookie_jar._cookies[netloc]['/']

    def cookie_exists(self, name='PHPSESSID'):
        """Test if a cookie exists. Kept for Pynav 0.6 compatibility"""
        return name in [cookie.name for cookie in self._cookie_jar]
    
    def add_path(self, url):
        """Correct an url depending on the link, internal use"""
        if re.search('://', url):
            return url
        else:
            if url == '':
                return self.base_url
            if url[0] == '/':
                return self.base_url[:-1]+url
            else:
                return self.relative_url+url
    
    # I think this doesn't need to be here, the user can handle that himself
    # by using the response
    def get_all_links(self, reg = None):
        """Return a list of all links found, a regex can be used"""
        links = re.findall('href="(.*?)"', self.response)
        if reg:
            def match(link): return len(re.findall(reg, link)) > 0
            return [self.add_path(link) for link in links if match(link)]
        else:
            return [self.add_path(link) for link in links]
    
    # I think this doesn't need to be here, the user can handle that himself
    # by using the response
    def get_all_images(self, reg = None):
        """Return a list of all images found, a regex can be used"""
        images = re.findall('img.*?src="(.*?)"', self.response)
        if reg:
            def match(image): return len(re.findall(reg, image)) > 0
            return [self.add_path(image) for image in images if match(image)]
        else:
            return [self.add_path(image) for image in images]
    
    # I think this doesn't need to be here, the user can handle that himself
    def set_page_delay(self, temps_min=0, temps_max=0):
        """Define the time between pages, random seconds, min and max"""
        self.temps_min = temps_min
        if(temps_min > temps_max):
            self.temps_max = temps_min
        else:
            self.temps_max = temps_max
        if self.verbose:
            print 'temps_min:', self.temps_min, ', temps_max:', self.temps_max

    # I think this doesn't need to be here, the user can handle that himself
    # by using the response
    def strip_tags(self, html):
        """Strip all tags of an HTML string and return only texts"""
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

