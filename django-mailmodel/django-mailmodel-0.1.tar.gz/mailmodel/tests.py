#-*- coding: utf-8 -*-
from django.test import TestCase
from django.core import mail
from mailmodel.models import MailModel
from django.test.client import Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class MailModelTestCase(TestCase):
    
    def setUp(self):
        settings.MAILMODEL_CONFIG = {
                "INCLUDE_CAPTCHA" : False,
                "APPS": ['auth.User'],
                "PUBLIC_CAPTCHA_KEY": "6LeFxwgAAAAAAGsK3bu4Ks4RAh2hcxGatYKL9nQv",
                "PRIVATE_CAPTCHA_KEY": "6LeFxwgAAAAAAJk18_gJOJtX6Tr90i6kKH6O6WnY"
            }
        User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        
    def test_mailmodel_view(self):
        resp = self.client.post(reverse('mailmodel'), 
                                {'name': 'name_test', 'email': 'sender@gmail.com',
                                 'recipient_name': 'recipient_name_test','recipient_email': 'recipient@gmail.com',
                                 'body': ''' Message body ''', 'content_type': 'auth.User','object_pk': 1})
        
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(mail.outbox[0].to, ['recipient@gmail.com'])
        self.assertTrue(u'name_test' in mail.outbox[0].subject)
        self.assertEqual(MailModel.objects.count(), 1)
