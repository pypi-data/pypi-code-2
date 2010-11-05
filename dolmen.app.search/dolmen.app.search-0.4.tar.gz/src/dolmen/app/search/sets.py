# -*- coding: utf-8 -*-

from zope.security.management import checkPermission


class PermissionAwareResultSet:
    """Lazily accessed set of objects.
    """
    def __init__(self, uids, uidutil, permission):
        self.uids = uids
        self.uidutil = uidutil
        self.perm = permission

    def __len__(self):
        return len(self.uids)

    def __iter__(self):
        for uid in self.uids:
            obj = self.uidutil.getObject(uid)
            if self.perm is None or checkPermission(self.perm, obj):
                yield obj
