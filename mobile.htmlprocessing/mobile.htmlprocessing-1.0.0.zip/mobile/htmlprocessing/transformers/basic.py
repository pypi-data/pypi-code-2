"""
    HTML cleaning basic facilities.

    See also http://codespeak.net/svn/lxml/trunk/src/lxml/html/clean.py

"""

__license__ = "GPL 2"
__copyright__ = "2009-2011 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>"
__author_url__ = "http://webandmobile.mfabrik.com"
__docformat__ = "epytext"

import re
import copy

import logging

logger = logging.getLogger("mobile.htmlprocessing")

try:
    import lxml

    from lxml.html import defs
    from lxml.html import fromstring, tostring, XHTML_NAMESPACE
    from lxml.html import _nons, _transform_result
    
    from lxml.etree import ParserError 
    
    from lxml.html.clean import Cleaner
    
    LXML = True

except ImportError, e:
    #raise RuntimeError("Please install lxml: http://pypi.python.org/pypi/lxml/")
    logger.exception(e)
    logger.error("Could not import lxml - probably not installed or too old version")
    
    LXML = False
    

if LXML:

    class BasicCleaner(Cleaner):
        """ Clean incoming HTML to be valid XHTML mobile profile without any nastiness """
    
        def __init__(self, trusted=False):
            """ Initialize HTML cleaner.
            
            Set whether we want to filter out nasty tags also.
             
            @param trusted: True if HTML is from trusted source 
            """
            self.trusted = trusted
            
        def add_alt_tags(self, el):
            """ Alt tags are needed for every image.
    
            If not ALT tag is present, put in an empty string.
            """
            if not "alt" in el.attrib:
                el.attrib["alt"] = ""
    
        def process_img(self, doc, el):
            self.add_alt_tags(el)
    
        def process_imgs(self, doc):
            for el in doc.iter('img'):
                self.process_img(doc, el)
    
        def clean_mobile(self, doc):
            """ Run XHTML-MP specific cleaners for the document.
            """
            self.process_imgs(doc)
    
        def process(self, html):
            """ Run XHTML mobile profile cleaner for HTML code.
    
            @param html: HTML as a strinrg or lxml Document
            @return: XHTML, utf-8 encoded string
            """
            
            # Check whether we got ready parse-tree or string input
            result_type = type(html)
    
            
            if isinstance(html, basestring):
                try:
                    doc = fromstring(html)
                except ParserError:
                    # Can't handle malformed doc, empty doc, etc.
                    return html
            else:
                doc = copy.deepcopy(html)
    
            # Run XHTML MP specific cleaning
            self.clean_mobile(doc)
    
            # Run normal cleaning
            if not self.trusted:
                self(doc)
    
            return tostring(doc, method="xml", encoding='UTF-8')

else:
    # No LXML
    class BasicCleaner(object):
        def __init__(self, trusted=False):
            pass
        
        def process(self, html):
            raise NotImplementedError("lxml support needed")

cleaner = BasicCleaner()

fix_html = cleaner.process
