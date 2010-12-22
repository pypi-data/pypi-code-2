# -*- coding: utf-8 -*-

import re

from zope.app.component.hooks import getSite

from Products.Archetypes.interfaces import IBaseObject
from collective.pathtouid.interfaces import IUIDConverted

mstring_absolute = r'''\s(?:href|src)="(/.*?)"'''
mstring_relative = r'''\s(?:href|src)="(.*?)"'''

class UIDConverter(object):
    """Utility for managing and trasforming text with relative or absolute
    site path, to use resolveuid
    """

    def findAbsolutePath(self, text):
        """
        Conversion of absolute path inside HREF or SRC attributes.
        
        >>> converter = UIDConverter()
        >>> converter.findAbsolutePath('''abc href="/plone/aaa/bbb/ccc" def
        ... ghi src="/plone/ddd/eee" lmn''')
        ['/plone/aaa/bbb/ccc', '/plone/ddd/eee']
        """
        r = re.compile(mstring_absolute, re.IGNORECASE)
        return r.findall(text)

    def findRelativePath(self, text):
        """
        Conversion of relative path inside HREF or SRC attributes.
        
        >>> converter = UIDConverter()
        >>> converter.findRelativePath('''abc href="aaa/bbb/ccc" def
        ... ghi src="ddd/eee" lmn''')
        ['aaa/bbb/ccc', 'ddd/eee']
        """
        r = re.compile(mstring_relative, re.IGNORECASE)
        return r.findall(text)

    
    def absolutePathToUID(self, text):
        """
        Converts all absolute paths inside a text in the "resolveuid" form.
        """
        site = getSite()
        paths = self.findAbsolutePath(text)
        for path in paths:
            target = site.restrictedTraverse(path, default=None)
            if target and IBaseObject.providedBy(target):
                text = text.replace(path, 'resolveuid/%s' % target.UID())
        return text

    
    def relativePathToUID(self, text, context=None):
        """
        Converts all relative paths inside a text in the "resolveuid" form.
        """
        site = getSite()
        if not context:
            context = site
        paths = self.findRelativePath(text)
        for path in paths:
            target = context.restrictedTraverse(path, default=None)
            if target and IBaseObject.providedBy(target):
                text = text.replace(path, 'resolveuid/%s' % target.UID())
        return text

