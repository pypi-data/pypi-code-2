##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.i18nmessageid
import zope.configuration.fields

_ = zope.i18nmessageid.MessageFactory('p01')


def isFile(path):
    return os.path.isfile(path)


def isDirectory(path):
    return os.path.isdir(path)


class ITMPStorage(zope.interface.Interface):
    """Temporary file storage."""

    path = zope.configuration.fields.Path(
        title=_(u'File system directory path for temporary storage files'),
        description=_(u'File system directory path for temporary storage files'),
        required=True,
        constraint=isDirectory,
        max_length=256)

    def generateNewTMPFilePath():
        """Generate a new unique unused tmp file path."""

    def getTMPFile():
        """Returns a TMPFile

        The file get observed by a transaction manager and will get removed
        at the end of our transaction if the file didn't get moved to a storage.
        """


class ITMPFile(zope.interface.Interface):
    """Temporary file with tmp file path.

    Other objects can consume the file with a zero-copy operation or
    they can read the file input.

    Such temp file can be moved with a zero-copy operation to another location
    e.g. a file system storage. You can also read a TMPFile like any other file
    and store this data in a ZODB file.

    If a file with the tmpPath exist at the end of the transaction, the
    transaction will remove the file. Which means the file didn't get moved
    (FSFile) or the data get consumed with a file read operation. (ZODB file)
    """

    tmpPath = zope.configuration.fields.Path(
        title=_(u'Temporary file system file path'),
        description=_(u'Temporary file system file path'),
        required=True,
        constraint=isFile,
        max_length=256)

    size = zope.schema.Int(
        title=_(u'Size'),
        description=_(u'Size'),
        default=0,
        readonly=True)

    closed = zope.schema.Bool(
        title=_(u'Closed'),
        description=_(u'Closed'),
        default=True,
        readonly=True)

    ctime = zope.schema.Float(
        title=_(u'Creation Time'),
        description=_(u'Creation Time'),
        readonly=True)

    atime = zope.schema.Float(
        title=_(u'Access Time'),
        description=_(u'Access Time'),
        readonly=True)

    def __nonzero__():
        """support for bool()"""

    def __len__():
        """returns the size of the file"""

    # delegated file operations
    def read(size=-1):
        """see file.read"""

    def close():
        """see file.close"""

    def seek(offset, whence=0):
        """see file.seek"""

    def tell():
        """see file.tell"""

    def fileno():
        """see file.fileno"""

    def __iter__():
        """see file.__iter__"""

    def write(s):
        """see file.write"""

    def writelines(lines):
        """see file.writelines"""

    def release():
        """Remove the file system file if the file with the tmpPath exist."""
