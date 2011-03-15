#!/usr/bin/python
# -*- coding: utf-8 -*-



################################################
#   use0mk
#-----------------------------------------------
#   Copyright:  (c) 2011 by Damjan Krstevski.
#   License:    GNU General Public License (GPL)
#   Feedback:   krstevsky[at]gmail[dot]com
################################################



"""
Documentation about use0mk class:
    Class:          use0mk.py
    Version:        v1.0.0
    Author:         Damjan Krstevski - SkyDriver
    Author URL:     http://profiles.google.com/krstevsky
    Compatibility:  Cross-platform and supports all Python's versions
    Feedback:       krstevsky@gmail.com

    Description:
        0.mk - Shorten your links!
        0.mk URL:       http://0.mk
        0.mk API Doc:   http://0.mk/api
"""


__all__     = ["_opener", "shortenUrl", "previewUrl"]
__version__ = "1.0.0"


try:
    import sys, json
    if sys.version[0] == "2":
        from urllib2 import build_opener
    else:
        from urllib.request import build_opener
except:
    raise ImportError("Import can't find module or can't find name in module.")



class use0mkException(Exception):
    """Class use0mkException
    Handling use0mk exception(s)
    """
    pass



class use0mk(object):
    """Class use0mk
    Class based on 0.mk API Documentation (http://0.mk/api)"""
    
    def __init__(self, user = None, apikey = None):
        """Object constructor
        @param user (string) - The 0.mk username
        @param apikey (string) - The 0.mk user's apikey
        """
        self.user       = user
        self.apikey     = apikey
        self.apidomain  = "http://api.0.mk/v2/"


    def __del__(self):
        """Object destructor"""
        del self.user, self.apikey, self.apidomain


    def __error(self, msg):
        """Handling use0mk exception(s)
        @param msg (string) - The exception message
        """
        raise use0mkException(str(msg))

    
    def _opener(self):
        """Get the URL opener
        @return OpenerDirector instance
        """
        useragent = "Use0mk Bot - Python"
        opener = build_opener()
        opener.addheaders = [("User-agent", useragent)]
        return opener


    def shortenUrl(self, link):
        """Shortening a long link
        @param link (string) - The long URL for shortening
        @return dict filled with the results
        """ 
        tmp = "skrati?format=json"
        if not self.user and not self.apikey:
            api = self.apidomain + tmp + "&link=" + link
        else:
            params = tmp + "&korisnik=" + self.user + "&apikey=" + self.apikey + "&link=" + link
            api = self.apidomain + params
        opener = self._opener()
        return json.load(opener.open(api))


    def previewUrl(self, link):
        """Preview the shortened link
        @param link (string) - The short URL
        @return dict filled with the results
        """
        tmp = "/pregled?link="
        opener = self._opener()
        return json.load(opener.open( self.apidomain + tmp + link ))
