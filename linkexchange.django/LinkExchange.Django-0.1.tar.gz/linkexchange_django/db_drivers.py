# LinkExchange.Django - Django integration with LinkExchange library
# Copyright (C) 2009, 2011 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

from django.db import transaction

from linkexchange.db_drivers import BaseMultiHashDriver
from linkexchange_django.models import DBHash, DBHashItem

class DjangoMultiHashDriver(BaseMultiHashDriver):
    """
    Django ORM multihash driver.
    """
    def __init__(self, dbname):
        self.dbname = dbname

    def load(self, hashkey):
        try:
            return DBHash.objects.get(dbname=self.dbname, key=hashkey)
        except DBHash.DoesNotExist:
            raise KeyError(hashkey)

    def get_mtime(self, hashkey):
        try:
            return DBHash.objects.get(dbname=self.dbname, key=hashkey).mtime
        except DBHash.DoesNotExist:
            raise KeyError(hashkey)

    def _run_in_transaction(self, func, args=[], kwargs={}):
        ok = False
        sid = transaction.savepoint()
        try:
            result = func(*args, **kwargs)
            ok = True
        finally:
            if ok:
                transaction.savepoint_commit(sid)
            else:
                transaction.savepoint_rollback(sid)
        return result

    def _get_hash(self, hashkey):
        try:
            return DBHash.objects.get(dbname=self.dbname, key=hashkey)
        except DBHash.DoesNotExist:
            pass
        h = DBHash(dbname=self.dbname, key=hashkey)
        h.save()
        return h

    def save(self, hashkey, newhash, blocking=True):
        def _save():
            h = self._get_hash(hashkey)
            h.set_items(newhash)
            h.save()
            return True
        return self._run_in_transaction(_save)

    def modify(self, hashkey, otherhash, blocking=True):
        def _modify():
            h = self._get_hash(hashkey)
            h.update_items(otherhash)
            h.save()
            return True
        return self._run_in_transaction(_modify)

    def delete(self, hashkey, keys, blocking=True):
        def _delete():
            h = self._get_hash(hashkey)
            h.delete_items(keys)
            h.save()
            return True
        return self._run_in_transaction(_delete)
