##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
""" Server Control View

$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.component
from ZODB.interfaces import IDatabase
from ZODB.FileStorage.FileStorage import FileStorageError
from zope.size import byteDisplay
from zope.app.applicationcontrol.i18n import ZopeMessageFactory as _

from z3c.pagelet import browser
from z3c.template.template import getPageTemplate


class ZODBControl(browser.BrowserPagelet):

    template = getPageTemplate()

    status  = None
    
    @property
    def databases(self):
        res = []
        for name, db in zope.component.getUtilitiesFor(
            IDatabase):
            d = dict(
                dbName = db.getName(),
                utilName = str(name),
                size = self._getSize(db),
                )
            res.append(d)
        return res
            
    def _getSize(self, db):
        """Get the database size in a human readable format."""
        size = db.getSize()        
        if not isinstance(size, (int, long, float)):
            return str(size)
        return byteDisplay(size)

    def update(self):
        if self.status is not None:
            return self.status
        status = []
        if 'PACK' in self.request.form:
            dbs = self.request.form.get('dbs', [])
            try:
                days = int(self.request.form.get('days','').strip() or 0)
            except ValueError:
                status.append(_('Error: Invalid Number'))
                self.status = status
                return self.status
            for dbName in dbs:
                db = zope.component.getUtility(IDatabase, name=dbName)
                try:
                    db.pack(days=days)
                    status.append(_('ZODB "${name}" successfully packed.',
                               mapping=dict(name=str(dbName))))
                except FileStorageError, err:
                    status.append(_('ERROR packing ZODB "${name}": ${err}',
                                    mapping=dict(name=str(dbName), err=err)))
        self.status = status
        return self.status
