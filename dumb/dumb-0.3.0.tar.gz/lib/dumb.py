#!/usr/bin/env python

""" 
pydumb

pydumb is a Python module to manage a dumb collection of bookmarks

"""

__author__ = 'Elena "of Valhalla" Grandi'
__version__ = '0.3.0'
__copyright__ = '2009-2011 Elena Grandi'
__license__ = 'LGPL'

import os,sys
import hashlib
import logging

try:
    import yaml
except ImportError, ex:
    sys.stderr.write("This program requires the yaml module from http://pyyaml.org/\n")
    raise

# This class is available in the logging module from version 2.7
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class Collection:
    """"""

    def __init__(self,directory):
        """"""
        self.directory = directory
        self.bookmarks = {}
        self.keywords = []
        self.logger = logging.getLogger('dumb.Collection')
        self.logger.addHandler(NullHandler())

    def __contains__(self,bm_id):
        """"""
        return bm_id in self.bookmarks

    def __getitem__(self,bm_id):
        """Returns the bookmark with the given id/hash"""
        return self.bookmarks[bm_id]

    def fuzzy_get(self,partial_id):
        bms = []
        for bm_id in self.bookmarks:
            if bm_id.startswith(partial_id):
                bms.append(self.bookmarks[bm_id])
        return bms

    def load(self):
        """Reads the bookmarks in the collection directory"""
        for bfile in os.listdir(self.directory):
            bm = None
            try:
                fp = open(self.directory+'/'+bfile)
                bm = Bookmark(stream=fp)
            except IOError:
                self.logger.info(bfile+" is not a readable file")
            except ValueError:
                self.logger.info(bfile+" is not a bookmark file")
            if bm != None:
                bm_id = hashlib.md5(bm['url']).hexdigest()
                self.bookmarks[bm_id] = bm
                if 'keywords' in bm:
                    for keyword in bm['keywords']:
                        if keyword not in self.keywords:
                            self.keywords.append(keyword)

    def save(self):
        """Saves the current bookmarks"""
        for bm_id in self.bookmarks:
            bm = self.bookmarks[bm_id]
            filename = os.path.join(self.directory,bm_id)
            try:
                fp = open(filename,'w')
            except IOError:
                self.logger.error("Could not open file "+filename+" for writing")
                raise
            try: 
                yaml.dump(bm.data,fp,default_flow_style=False)
            except IOError:
                self.logger.error("Could not write to "+filename)
                raise
            finally:
                fp.close()

    def add_bookmark(self,data):
        """Adds a new bookmark to the collection from a dict of data"""

        try:
            bm_id = hashlib.md5(data['url']).hexdigest()
            self.bookmarks[bm_id] = Bookmark(data=data)
        except KeyError:
            raise ValueError, "A bookmark must have an url"
        if 'keywords' in data:
            for keyword in data['keywords']:
                if keyword not in self.keywords:
                    self.keywords.append(keyword)


    def get_bookmarks(self,keywords=None):
        """Returns a list of the bookmarks with the given tags.
        If kkeywords == None, return every bookmark in the collection."""
        if keywords == None:
            return self.bookmarks.values()
        bms = []
        if type(keywords) == list:
            for bm in self.bookmarks:
                for keyword in keywords:
                    if 'keywords' in self.bookmarks[bm] and keyword in self.bookmarks[bm]['keywords']:
                        bms.append(self.bookmarks[bm])
                        break
        return bms

    def get_base_bookmarks(self,url):
        bms = []
        for bm in self.bookmarks:
            if self.bookmarks[bm]['url'] in url:
                bms.append(self.bookmarks[bm])
        return bms

    def get_keywords(self):
        """Returns the list of keywords in this collection"""
        return self.keywords


class Bookmark():
    """"""

    def __init__(self,data=None,stream=None):
        """Creates a new bookmark instance.
        """
        self.logger = logging.getLogger('dumb.Bookmark')
        self.logger.addHandler(NullHandler())
        self.data = {}
        if data != None:
            try:
                self.data['url']=data['url']
            except KeyError:
                raise ValueError, "Could not find an url in the given data"
            self.data=data
        elif stream != None:
            try:
                parsed_data = yaml.safe_load(stream)
            except yaml.YAMLError:
                raise ValueError, "Could not find sane yaml data in the given stream"
            if not 'url' in parsed_data:
                raise ValueError, "Could not find an url in the given data"
            self.load_data(parsed_data)
        else:
            raise ValueError, "a Bookmark must be initialized with either a data dict or a yaml stream"

    def __str__(self):
        """"""
        return yaml.dump(self.data,default_flow_style=False)

    def __repr__(self):
        """"""
        return repr(self.data)

    def __getitem__(self,key):
        """"""
        return self.data[key]

    def __setitem__(self,key,value):
        """"""
        self.data[key]=value

    def __contains__(self,key):
        """"""
        return self.data.has_key(key)

    #def get_parsed_value(self,key):
    #    """Returns the value of the given key with %(url)s explicited"""
    #    return self.data[key].replace("%(url)s",self.data['url'])

    def load_data(self,data):
        """Loads the bookmark informations from a dict"""
        # TODO: add a (pythonic) type check
        if data.has_key('url'):
            self.data['url'] = data['url']
        if data.has_key('title'):
            self.data['title'] = data['title']
        if data.has_key('comment'):
            self.data['comment'] = data['comment']
        if data.has_key('content-type'):
            self.data['content-type']=data['content-type']
        if data.has_key('added'):
            self.data['added'] = data['added']
        if data.has_key('last-seen'):
            self.data['last-seen'] = data['last-seen']
        if data.has_key('cline'):
            self.data['cline'] = data['cline']
        if data.has_key('keywords'):
            if not self.data.has_key('keywords'):
                self.data['keywords'] = []
            for keyword in data['keywords']:
                self.data['keywords'].append(keyword)
        if data.has_key('mirrors'):
            if not self.data.has_key('mirrors'):
                self.data['mirrors'] = []
            for mirror in data['mirrors']:
                self.data['mirrors'].append(mirror)
        if data.has_key('positions'):
            if not self.data.has_key('positions'):
                self.data['positions'] = []
            for pos in data['positions']:
                self.data['positions'].append(pos)
        if data.has_key('related'):
            if not self.data.has_key('related'):
                self.data['related'] = []
            for rel in data['related']:
                self.data['related'].append(rel)


def main():
    pass


if __name__ == '__main__': main()
