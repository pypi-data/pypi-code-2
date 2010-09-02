# -*- coding: utf-8 -*-
from lxml import etree
from StringIO import StringIO
from httplib2 import Http

class html2data(object):
    def load(self, url=None, html=None, config={}):
        returnObj, html = self.loadAndGetContent(url, html, config)
        return returnObj
    
    def loadAndGetContent(self, url=None, html=None, config={}):
        if url:
            rest = Http()
            header, html = rest.request(url)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        returnObj = {}
        mapping = config.get('map')
        for mapping_args in mapping:
            key = mapping_args[0]
            xpath = mapping_args[1]
            func = lambda x: x
            if len(mapping_args) == 3:
                func = mapping_args[2]
            xpath_elements = tree.xpath(xpath)
            returnObj[key] = func(xpath_elements)
        return (returnObj, html)