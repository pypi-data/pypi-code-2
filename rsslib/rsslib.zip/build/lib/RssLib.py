#!/usr/bin/python
# -*- coding: utf-8 -*-


##################################################
#       BitLyClient Library
#-------------------------------------------------
#   Copyright:    (c) 2010 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     krstevsky[at]gmail[dot]com
##################################################




"""
RssLib Python Library
This module will help you to read the RSS feeds from some of your favourite websites!

This module is based on GNU General Public License (GPL)!
http://www.gnu.org/licenses/gpl.html

Also this module has been created according to the standards of the RSS 2.0!
http://cyber.law.harvard.edu/rss/rss.html

This module is freeware, you can use, copy, edit, redistribute...
You can send FeedBack, comment, suggestion or etc on krstevsky[at]gmail[dot]com


Class variables:
    url        = String, Feed URL

Class methods:
    strip_tags( data )
    - Returns string, stripped HTML tags from data

    read( boolean strip = False )
    - Return dict
        * title = The RSS titles
        * link = The RSS links
        * description = The RSS descriptions
        * author = The RSS authors
        * category = The RSS categories
        * guid = The RSS guids
        * pubDate = The RSS pubDates
        * source = The RSS sources

    - strip = True
        * The HTML tags from the descriptions will be stripped
        

Exception:
    RssLibException as ex:
        print ex
        # This function will returns the exception
            

Usage:
    try:
        import rsslib
        url = '' # Feed URL
        rss = rsslib.RssLib(url).read()
        for title in rss['title']:
            print title
    except RssLibException as ex:
        print ex
"""




# public symbols
__all__ 		= ["url", "strip_tsgs", "read"]
__version__             = "1.0.0"




try:
    import sys, re
    from xml.dom.minidom import parseString, Element
    if sys.version[0] == '2':
        import urllib2 as urllib
    else:
        import urllib.request as urllib
except:
    raise ImportError("Some module(s) can not be imported!")




# Class RssLibException (Exception Message)
class RssLibException(Exception):
    ''' Class RssLibException (Exception Message) '''
    pass



# Class RssLib
class RssLib(object):
    ''' Class RssLib '''

    # Class Constructor
    def __init__(self, url = None):
        ''' Class Constructor '''
        self.url = url



    # Class Destructor
    def __del__(self):
        ''' Class Destructor '''
        self.url = None



    # Set the error message (Exception)
    def __set_error(self, error):
        ''' Set the error message (Exception) '''
        raise RssLibException(error)



    # Get the opener
    def __get_opener( self, ua = 'RssLib - Python' ):
        ''' Get the opener '''
        try:
            opener = None
            opener = urllib.build_opener()
            opener.addheaders = [('User-agent', ua)]
            return opener
        except Exception as ex:
            self.__set_error( str(ex) )
            

    
    # Appending node into list
    def __append_node( self, elem = None, tag = None ):
        ''' Appending node into list '''
        if not elem and not tag:
            self.__set_error("The params must have a value!")

        try:
            node = elem.getElementsByTagName(tag)
            if len(node) != 1:
                return ""
            else:
                if len(node[0].childNodes) != 1:
                    return ""
                else:
                    return node[0].firstChild.data
        except Exception as ex:
            self.__set_error( str(ex) )



    # Read the XML document
    def __read(self, url = None):
        ''' Read the XML document '''
        if not url:
            self.__set_error("URL must have a value!")

        try:
            req = self.__get_opener()
            return req.open(url).read()
        except Exception as ex:
            self.__set_error( str(ex) )



    # Strip the HTML tags
    def strip_tags(self, data = None):
        ''' Strip the HTML tags '''
        if not data:
            self.__set_error("Data must have a value!")

        p = re.compile(r'<.*?>')
        data = p.sub('', data)

        p = re.compile(r'\s+')
        return p.sub(' ', data)


    
    # Reading RSS Feed from URL
    def read(self, strip = False):
        ''' Reading RSS Feed from URL '''
        if not self.url:
            self.__set_error("Resource must have a value!")

        try:
            doc = parseString( self.__read(self.url) )
            items = doc.getElementsByTagName('item')
            rss = dict( {'title' : [], 'link' : [], 'description' : [], 'author' : [],
                         'category' : [], 'guid' : [], 'pubDate' : [], 'source' : [] } )

            for i in items:
                rss['title'].append( self.__append_node(i, 'title') )
                rss['link'].append( self.__append_node(i, 'link') )
                
                if strip == True:
                    rss['description'].append( self.strip_tags( self.__append_node(i, 'description') ) )
                else:
                    rss['description'].append( self.__append_node(i, 'description') )
                    
                rss['author'].append( self.__append_node(i, 'author') )
                rss['category'].append( self.__append_node(i, 'category') )
                rss['guid'].append( self.__append_node(i, 'guid') )
                rss['pubDate'].append( self.__append_node(i, 'pubDate') )
                rss['source'].append( self.__append_node(i, 'source') )
                
            return rss
        except Exception as ex:
            self.__set_error( str(ex) )
