# LinkExchange.Django - Django integration with LinkExchange library
# Copyright (C) 2011 Konstantin Korikov
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

import unittest

from linkexchange.tests import MultiHashDriverTestMixin

from linkexchange_django.models import DBHash
from linkexchange_django.db_drivers import DjangoMultiHashDriver

class DBHashTest(unittest.TestCase):
    def setUp(self):
        self.hash = DBHash.objects.create(dbname='testdb', key='testkey')
        self.hash.save()

    def tearDown(self):
        self.hash.items.all().delete()
        self.hash.delete()

    def test_clear_items(self):
        self.hash.set_items([('k1', 'v1'), ('k2', 'v2')])
        self.hash.save()
        self.assertEqual(len(self.hash), 2)
        self.hash.clear_items()
        self.hash.save()
        self.assertEqual(len(self.hash), 0)

    def test_update_items(self):
        self.hash.set_items([('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')])
        self.hash.save()
        self.assertEqual(len(self.hash), 3)

        self.hash.update_items([('k3', 'v3x'), ('k4', 'v4')])
        self.hash.save()
        self.assertEqual(len(self.hash), 4)
        self.assertEqual(self.hash['k1'], 'v1')
        self.assertEqual(self.hash['k2'], 'v2')
        self.assertEqual(self.hash['k3'], 'v3x')
        self.assertEqual(self.hash['k4'], 'v4')

    def test_set_items(self):
        self.hash.set_items([('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')])
        self.hash.save()
        self.assertEqual(len(self.hash), 3)
        self.assertEqual(self.hash['k1'], 'v1')
        self.assertEqual(self.hash['k2'], 'v2')
        self.assertEqual(self.hash['k3'], 'v3')

        self.hash.set_items([('k1', 'v1'), ('k3', 'v3x'), ('k4', 'v4')])
        self.hash.save()
        self.assertEqual(len(self.hash), 3)
        self.assertEqual(self.hash['k1'], 'v1')
        self.assertEqual(self.hash['k3'], 'v3x')
        self.assertEqual(self.hash['k4'], 'v4')

    def test_delete_items(self):
        self.hash.set_items([('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')])
        self.hash.save()
        self.assertEqual(len(self.hash), 3)
        self.hash.delete_items(['k2', 'k3'])
        self.assertEqual(len(self.hash), 1)

class DjangoMultiHashDriverTest(MultiHashDriverTestMixin,
        unittest.TestCase):

    with_blocking = False

    def setUp(self):
        self.db = DjangoMultiHashDriver('testdb')

    def tearDown(self):
        for h in DBHash.objects.filter(dbname=self.db.dbname):
            h.items.all().delete()
            h.delete()
        del self.db
