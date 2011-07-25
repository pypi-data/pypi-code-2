#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from unittest import TestLoader
import os

import psycopg2
from van.pg import DatabaseManager
import testresources
import testtools

from pgbouncer.fixture import PGBouncerFixture

# A 'just-works' workaround for Ubuntu not exposing initdb to the main PATH.
os.environ['PATH'] = os.environ['PATH'] + ':/usr/lib/postgresql/8.4/bin'

def test_suite():
    result = testresources.OptimisingTestSuite()
    result.addTest(TestLoader().loadTestsFromName(__name__))
    return result


class ResourcedTestCase(testtools.TestCase, testresources.ResourcedTestCase):
    """Mix together testtools and testresources."""


def setup_user(db):
    conn = psycopg2.connect(host=db.host, database=db.database)
    conn.cursor().execute('CREATE USER user1')
    conn.commit()
    conn.close()


class TestFixture(ResourcedTestCase):

    resources = [('db', DatabaseManager(initialize_sql=setup_user))]

    def test_dynamic_port_allocation(self):
        bouncer = PGBouncerFixture()
        db = self.db
        bouncer.databases[db.database] = 'host=%s' % (db.host,)
        bouncer.users['user1'] = ''
        with bouncer:
            conn = psycopg2.connect(host=bouncer.host, port=bouncer.port,
                user='user1', database=db.database)
            conn.close()

    def test_stop_start_facility(self):
        # Once setup the fixture can be stopped, and started again, retaining
        # its configuration. [Note that dynamically allocated ports could
        # potentially be used by a different process, so this isn't perfect,
        # but its pretty reliable as a test helper, and manual port allocation
        # outside the dynamic range should be fine.
        bouncer = PGBouncerFixture()
        db = self.db
        bouncer.databases[db.database] = 'host=%s' % (db.host,)
        bouncer.users['user1'] = ''
        def check_connect():
            conn = psycopg2.connect(host=bouncer.host, port=bouncer.port,
                user='user1', database=db.database)
            conn.close()
        with bouncer:
            current_port = bouncer.port
            bouncer.stop()
            self.assertRaises(psycopg2.OperationalError, check_connect)
            bouncer.start()
            check_connect()
