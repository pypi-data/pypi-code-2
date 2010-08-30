# -*- coding: utf-8 -*-
from lxml import etree
from StringIO import StringIO
from httplib2 import Http

class html2data(object):
    def load(self, url=None, html=None, config={}):
        if url:
            rest = Http()
            header, html = rest.request(url)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        returnObj = {}
        mapping = config.get('map')
        for key, xpath in mapping:
            xpath_elements = tree.xpath(xpath)
            if(len(xpath_elements)>1):
                returnObj[key] = []
                for el in xpath_elements:
                    returnObj[key].append(el.strip())
            else:
                returnObj[key] = xpath_elements[0].strip()
        return returnObj