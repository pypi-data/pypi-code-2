#!/usr/bin/env python

import sys
import cssutils
from BeautifulSoup import BeautifulSoup

class Premailer(object):
    """ http://github.com/ralphbean/python-premailer """

    def __init__(self, html=''):
        self.html = html
        self.soup = BeautifulSoup(self.html)

    def getStyleMap(self):
        """ Create a dictionary of lists mapping selectors to styles."""
        styleblocks = [b.contents[0] for b in self.soup.findAll('style')]
        parser = cssutils.CSSParser()
        selectors = []
        sMap = {}
        for block in styleblocks:
            sheet = parser.parseString(block)
            for rule in sheet.cssRules:
                if not isinstance(rule, cssutils.css.CSSStyleRule):
                    #type(rule) != cssutils.css.CSSStyleRule:
                    continue
                for selector in rule.selectorList:
                    # TODO stripping off the '.' that precedes styles?
                    sel = selector.selectorText[1:]
                    sMap[sel] = sMap.get(sel, []) + [rule.style.cssText]
        return sMap

    def destroyStyle(self):
        """ Destroy style header information in the soup."""
        for block in self.soup.findAll('style'):
            block.extract()

    def applyStyleMap(self, sMap={}):
        """ Apply styles to the <body>."""
        comp = lambda ele : not ( ele is None or selector not in ele )

        # Actually apply them.
        for selector, styles in sMap.iteritems():
            for element in self.soup.findAll(attrs={"class" : comp}):
                try:
                    styles.append(element.__getitem__('style'))
                except:
                    pass
                element.__setitem__('style', ';'.join(styles))

        # Remove the old class tags to prove we were here.
        for selector, styles in sMap.iteritems():
            for element in self.soup.findAll(attrs={"class" : comp}):
                element.__delitem__('class')
    
    def premail(self):
        """ Does all the work.  Returns premailed html. """
        self.applyStyleMap(self.getStyleMap())
        self.destroyStyle()
        return str(self.soup.html)
        
