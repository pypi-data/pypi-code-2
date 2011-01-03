##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import zope.component
import ZODB.interfaces

mb_b = 1048576

def cacheMonitor(connection, database=None, size=''):
    msg = ''
    if database is None:
       for nm, db in zope.component.getUtilitiesFor(ZODB.interfaces.IDatabase):
           msg += 'DB cache sizes for %s\n' % (nm or 'main')
           msg += 'Max objects: %s\n' % db._cache_size
           msg += 'Max object size bytes: %sMB\n' % (db._cache_size_bytes/mb_b)
    else:
        if database == '-':
            database = ''
        db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)
        if not size:
            msg += 'DB cache sizes for %s\n' % (database or 'main')
            msg += 'Max objects: %s\n' % db._cache_size
            msg += 'Max object size bytes: %sMB\n' % (
                db._cache_size_bytes/mb_b)
        elif size.endswith('MB'):
            num = int(size[:-2])
            num *= mb_b
            db.setCacheSizeBytes(num)
            msg += 'Set max object size bytes to %s\n' % size
        else:
            db.setCacheSize(int(size))
            msg += 'Set max objects to %s\n' % size
    connection.write(str(msg))
