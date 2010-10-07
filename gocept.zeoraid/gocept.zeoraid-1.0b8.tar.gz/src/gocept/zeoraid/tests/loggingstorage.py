##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
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
"""LoggingStorage is a storage used for testing purposes that logs calls made
   to an arbitrary method (getSize()).
"""

import tempfile

import ZODB.config
import ZODB.FileStorage


class Opener(ZODB.config.BaseConfig):

    def open(self):
        name = self.config.name
        file_handle, file_name = tempfile.mkstemp()
        return LoggingStorage(name, file_name)


class LoggingStorage(ZODB.FileStorage.FileStorage):

    def __init__(self, name='', file_name=''):
        ZODB.FileStorage.FileStorage.__init__(self, file_name)
        self._name = name
        self._log = []

    def getSize(self):
        self._log.append("Storage '%s' called." % self._name)
        return ZODB.FileStorage.FileStorage.getSize(self)
