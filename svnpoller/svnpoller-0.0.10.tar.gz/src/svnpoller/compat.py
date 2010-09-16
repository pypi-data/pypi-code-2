# -*- coding: utf-8 -*-

__all__ = ['xml2elem', 'strptime']

##############################
# xml2elem implementations

import sys
from xml.dom.minidom import parseString

class minidom_xml2elem(object):
    def __init__(self, root):
        if isinstance(root, basestring):
            self.root = parseString(root).childNodes[0]
        else:
            self.root = root

    def find(self, tag):
        return minidom_xml2elem(self.root.getElementsByTagName(tag)[0])

    def __iter__(self):
        for node in self.root.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                yield minidom_xml2elem(node)

    @property
    def attrib(self):
        return dict(self.root.attributes.items())

    @property
    def text(self):
        return self.root.childNodes[0].nodeValue

try:
    # import lxml if exist
    from lxml.etree import XML as xml2elem
except:
    if sys.version_info < (2,5):
        xml2elem = minidom_xml2elem
    else:
        from xml.etree.ElementTree import fromstring as xml2elem


##############################
# strptime implementations

import sys, time
from datetime import datetime

# Python2.4 have no `strptime` method at datetime class
if sys.version_info < (2,5):
    strptime = lambda t,f: datetime(*(time.strptime(t, f)[0:6]))
else:
    strptime = datetime.strptime


