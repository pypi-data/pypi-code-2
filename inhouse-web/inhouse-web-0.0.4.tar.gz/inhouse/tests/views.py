# -*- coding: utf-8 -*-

"""Testcases for the models."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from inhouse.models import Account

class TestContextProcessors(TestCase):

    def setUp(self):
        self.client = Client()

    def test_library(self):
        user = User.objects.create_user('foo', 'test@example.com', 'bar')
        user.save()
        self.client.login(username='foo', password='bar')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)
        self.assert_(isinstance(response.context['account'], Account))
        account = response.context['account']
        self.assertEqual(response.context['counter'], 1)
