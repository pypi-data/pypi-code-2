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
import pytz
import sys
import uuid

import zope.interface
from zope.schema.fieldproperty import FieldProperty
from zope.app.appsetup.product import getProductConfiguration

from p01.tmp import exceptions
from p01.tmp import interfaces
import p01.tmp.file

def getTMPStoragePath(confKey='storage', envKey='P01_TMP_STORAGE_PATH'):
    path = None
    config = getProductConfiguration('p01.tmp')
    if config is not None:
        path = config.get(confKey)
    else:
        path = os.environ.get(envKey)
    # tweak windows path
    if path is None:
        raise ValueError(
            "You must define p01.tmp 'storage' for run this server "
            "or remove the p01/tmp/default.zcml from your configuration.zcml. "
            "See p01/tmp/wsgi.py how you can define this env variable.")
    if sys.platform == 'win32':
        # fix buildout based path setup like we do in buildout.cfg
        # ${buildout:directory}/parts/tmp
        parts = path.split('/')
        path = os.path.join(*parts)
    if not os.path.exists(path):
        raise exceptions.MissingStoragePathError(
            "Given tmp storage path '%s' does not exist" % path)
    return unicode(path)


class TMPStorage(object):
    """Temporary file storage."""

    zope.interface.implements(interfaces.ITMPStorage)

    path = FieldProperty(interfaces.ITMPStorage['path'])

    def __init__(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = os.path.abspath(path)

    def generateNewTMPFilePath(self):
        """Generate a new unique unused tmp file path."""
        tz = pytz.UTC
        while True:
            #there might be a race condition around this
            #but doing this right needs quite a bit of infrastructure
            #(that also depends on the platform)
            #that would contain also some locking on the file system
            path = os.path.join(self.path, str(uuid.uuid1()))
            if not os.path.exists(path):
                break
        return path

    def getTMPFile(self):
        """Returns a TMPFile

        The file get observed by a transaction manager and will get removed
        at the end of our transaction if the file didn't get moved to a storage.
        """
        path = self.generateNewTMPFilePath()
        path = os.path.abspath(path)
        return p01.tmp.file.TMPFile(path)
