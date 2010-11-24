import unittest

from django.db import transaction
from django.test.client import Client

from minibooks.ledger.management import clean_minibooks_db


class TestCase(unittest.TestCase):
    def setUp(self):
        self.c = Client()
        clean_minibooks_db()
    
    def tearDown(self):
        self.assertUserLogout()
        self.c = None
        transaction.rollback()
    
    def assertUserLogout(self):
        # log out only if logged in
        if self.c.cookies:
            self.c.logout()
        self.user = None
    
    def assertUserLogin(self, username, password):
        login_successful = self.c.login(username=username, password=password)
        self.assertEqual(login_successful, True)
        try:
            self.user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                self.user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
    
    def assertRedirects(
        self,
        response,
        expected_path,
        status_code=302,
        target_status_code=200,
      ):
        self.assertEqual(response.status_code, status_code)
        expected_url = "http://testserver%s" % expected_path
        actual_url = response['Location'][0:len(expected_url)]
        self.assertEqual(actual_url, expected_url, str(response))

        if target_status_code:
            response = self.c.get(expected_path)
            self.assertEqual(
                response.status_code,
                target_status_code,
                response,
            )
