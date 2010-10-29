# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
Retrievers for file like fields
$Id: retrievers.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from Products.CMFCore.utils import getToolByName

from interfaces import IFieldRetriever
from registry import GlobalRegistry

##
# FileField handling
##

class FileFieldRetriever:
    # Assume FileField and AttachmentField have the same API for what we need.
    # See "interfaces.py"

    __implements__ = IFieldRetriever

    field_type = 'file'

    def __init__(self, field, content):
        self.field = field
        self.content = content
        return

    def fileName(self):
        return self.field.getFilename(self.content)

    def relativePathFrom(self, base_content, portal_url=None):
        if portal_url is None:
            portal_url = getToolByName(base_content, 'portal_url')
        base_path = portal_url.getRelativeContentURL(base_content)
        content_path = portal_url.getRelativeContentURL(self.content)
        content_path = content_path[len(base_path):] + '/' + self.field.getName()
        return content_path

    def mimeType(self):
        return self.field.getContentType(self.content)

    def fileBody(self):
        try:
            # Append arg (full=True) to make sure we have the entire file
            bu = self.field.getBaseUnit(self.content, full=True)
        except:
            # old api of AT
            bu = self.field.getBaseUnit(self.content,)

        return bu.getRaw()

GlobalRegistry.register(FileFieldRetriever)

##
# ImageField handling
##

class ImageFieldRetriever(FileFieldRetriever):
    # ImageField and FileField have the same API for what we need

    field_type = 'image'


GlobalRegistry.register(ImageFieldRetriever)
