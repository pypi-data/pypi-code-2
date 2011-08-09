##############################################################################
#
# Copyright (c) 2006-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.interface import Interface, Attribute
from zope.schema.interfaces import IField
from zope.schema import TextLine, Bytes

class IFile(IField):
    u"""File field."""

class IHurryFile(Interface):
    filename = TextLine(title=u'Filename of file')
    data = Bytes(title=u'Data in file')
    file = Attribute('File-like object with data')
    headers = Attribute('Headers associated with file')
    size = Attribute('The size of the file in bytes.')

class IFileRetrieval(Interface):
    def getFile(data):
        """Get a file object for file data.
        """

    def createFile(filename, f):
        """Given a file object, create a HurryFile with that data in it.
        """
