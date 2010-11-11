from __future__ import with_statement
from datetime import timedelta
from demo import settings
from demo.models import SessionDatabase
from demo.shared import THREAD_LOCALS
from django.core.management import call_command
from django.test.client import Client
from django.test.testcases import TestCase
from exampleapp.models import Item
import time

class Database(object):
    """
    Helper context manager to access a client's database.
    """
    def __init__(self, client):
        self.client = client
        
    def __enter__(self):
        THREAD_LOCALS.database = SessionDatabase.objects.get_db_name(self.client)
        
    def __exit__(self, type, value, traceback):
        THREAD_LOCALS.database = None


class SettingsOverride(object):
    def __init__(self, **overrides):
        self.overrides = overrides
        
    def __enter__(self):
        self.old = {}
        for key, value in self.overrides.items():
            self.old[key] = getattr(settings, key)
            setattr(settings, key, value)
        
    def __exit__(self, type, value, traceback):
        for key, value in self.old.items():
            setattr(settings, key, value)


def get_share_link(client, path='/'):
    return '%s?%s=%s' % (path, settings.SHARE_PARAMETER, client.session.session_key)


class DemoTestCase(TestCase):
    def tearDown(self):
        for obj in SessionDatabase.objects.all():
            obj.kill(True)
            
    def assert200(self, response):
        self.assertEqual(response.status_code, 200)

    def test_01_single(self):
        """
        Basic testing with one client
        """
        c1 = Client()
        # assure the database is empty at the moment
        self.assertEqual(0, SessionDatabase.objects.count())
        self.assert200(c1.get('/'))
        # first request should have created an entry in SessionDatabase
        self.assertEqual(1, SessionDatabase.objects.count())
        # assure that there's no item yet
        self.assertEqual(0, Item.objects.count())
        with Database(c1):
            # and that there's no item in that client's database
            self.assertEqual(0, Item.objects.count())
        # post an item
        self.assert200(c1.post('/', {'name': 'Test'}))
        # check that it was not written into the global database
        self.assertEqual(0, Item.objects.count())
        with Database(c1):
            # however check that it is in the client's database
            self.assertEqual(1, Item.objects.count())
        
    def test_02_double(self):
        """
        Testing with two clients.
        """
        c1 = Client()
        c2 = Client()
        # check that we have no database yet
        self.assertEqual(0, SessionDatabase.objects.count())
        self.assert200(c1.get('/'))
        # first client should have created a database
        self.assertEqual(1, SessionDatabase.objects.count())
        # second client should have created a database
        self.assert200(c2.get('/'))
        self.assertEqual(2, SessionDatabase.objects.count())
        # check databases are isolated per cleint
        C1_NAME = 'CLIENT-ONE-TEST'
        C2_NAME = 'CLIENT-TWO-TEST'
        self.assert200(c1.post('/', {'name': C1_NAME}))
        self.assert200(c2.post('/', {'name': C2_NAME}))
        r1 = c1.get('/')
        self.assertContains(r1, C1_NAME)
        self.assertNotContains(r1, C2_NAME)
        r2 = c2.get('/')
        self.assertContains(r2, C2_NAME)
        self.assertNotContains(r2, C1_NAME)
        with Database(c1):
            self.assertEqual(1, Item.objects.count())
            i1 = Item.objects.all()[0]
        with Database(c2):
            i2 = Item.objects.all()[0]
            self.assertEqual(1, Item.objects.count())
        self.assertEqual(0, Item.objects.count())
        self.assertNotEqual(i1.name, i2.name)
        
    def test_03_share(self):
        """
        Tests that sharing of a database works correctly
        """
        c1 = Client()
        # no assertions here because it's tested in test_01_single
        c1.get('/')
        c1.post('/', {'name': 'Test'})
        c2 = Client()
        # check we have one database
        self.assertEqual(1, SessionDatabase.objects.count())
        c2.get(get_share_link(c1))
        # check we still have only one database because it got shared
        self.assertEqual(1, SessionDatabase.objects.count())
        with SettingsOverride(ALLOW_SHARE=False):
            c3 = Client()
            c3.get(get_share_link(c1))
            # since sharing is disabled, client 3 should get a new database
            self.assertEqual(2, SessionDatabase.objects.count())
        
    def test_04_max_database(self):
        """
        Tests that the DEMO_MAX_DATABASES setting works
        """
        c1 = Client()
        c2 = Client()
        c3 = Client()
        self.assertEqual(0, SessionDatabase.objects.count())
        c1.get('/')
        self.assertEqual(1, SessionDatabase.objects.count())
        c2.get('/')
        self.assertEqual(2, SessionDatabase.objects.count())
        # Client 3 should not get a new database!
        response = c3.get('/')
        self.assert200(response)
        self.assertEqual(2, SessionDatabase.objects.count())
        self.assertTemplateUsed(response, 'demo/database_limit.html')
        
    def test_05_expires(self):
        with SettingsOverride(DATABASE_LIVETIME=timedelta(seconds=2)):
            c1 = Client()
            self.assertEqual(0, SessionDatabase.objects.count())
            c1.get('/')
            self.assertEqual(1, SessionDatabase.objects.count())
            share_link = get_share_link(c1)
            time.sleep(2)
            # cleanup
            call_command('cleandemos')
            # The database should be gone by now
            self.assertEqual(0, SessionDatabase.objects.count())
            # Client 2 should not be able to access the database via share link
            c2 = Client()
            response = c2.get(share_link)
            self.assert200(response)
            self.assertEqual(0, SessionDatabase.objects.count())
            self.assertTemplateUsed(response, 'demo/database_expired.html')