import datetime
import random

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core import mail

from crm import models as crm
from timepiece.tests import TimepieceDataTestCase

from minibooks.ledger import models as ledger
from minibooks.ledger.test import TestCase as BaseTestCase


class LedgerDataTestCase(TimepieceDataTestCase):
    def create_account(self, data={}):
        defaults = {
            'name': self.random_string(20, extra_chars=' '),
            'number': random.randint(1000, 9999),
        }
        defaults.update(data)
        return ledger.Account.objects.create(**defaults)
    
    def create_exchange_type(self, data={}):
        label = self.random_string(20, extra_chars=' ')
        defaults = {
            'label': label,
            'slug': slugify(label),
        }
        defaults.update(data)
        return ledger.ExchangeType.objects.create(**defaults)
    
    def create_exchange(self, data={}):
        defaults = {
            'business': self.create_business(),
            'type': self.create_exchange_type(),
            'date': datetime.datetime.now(),
        }
        defaults.update(data)
        return ledger.Exchange.objects.create(**defaults)

    def create_transaction(self, data={}):
        defaults = {
            'memo': self.random_string(100, extra_chars=' '),
            'amount': '%d.%02d' % (random.randint(1,100000), random.random()),
            'quantity': random.randint(1,10000),
            'date': datetime.datetime.now(),
        }
        if 'debit' not in data:
            data['debit'] = self.create_account()
        if 'credit' not in data:
            data['credit'] = self.create_account()
        defaults.update(data)
        return ledger.Transaction.objects.create(**defaults)


class ExchangeEmails(LedgerDataTestCase):
    def setUp(self):
        self.superuser = User.objects.create_user('superuser', 
                                                  'test@example.com', 'test')
        self.superuser.is_superuser = True
        self.superuser.save()
        
    def test_business_exchange_email(self):
        """
        Tests sending an exchange to a business with no project.
        """
        self.client.login(username='superuser', password='test')
        exchange = self.create_exchange()
        person = self.create_person()
        self.create_relationship(data={
            'from_contact': exchange.business, 
            'to_contact': person
        })
        email_exchange_url = reverse('email_exchange', args=(exchange.pk,))
        response = self.client.get(email_exchange_url)
        self.assertEqual(response.status_code, 200)
        data = {
            'to': person.pk,
            'memo': self.random_string(500),
        }
        response = self.client.post(email_exchange_url, data)
        self.assertNoFormErrors(response)
        view_business_url = reverse('view_business', 
                                    args=(exchange.business.pk,))
        self.assertRedirects(response, view_business_url)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(
            message.subject, 
            ' '.join([
                exchange.business.name, 
                exchange.type.label,
                datetime.datetime.today().strftime('%Y-%m-%d'),
            ]),
        )
        self.assertEqual(message.body.strip(), data['memo'])
        self.assertTrue(person.email in message.to)
        
    def test_project_exchange_email(self):
        """
        Tests sending an exchange to a business with no project.
        """
        self.client.login(username='superuser', password='test')
        exchange = self.create_exchange()
        person = self.create_person()
        self.create_relationship(data={
            'from_contact': exchange.business, 
            'to_contact': person
        })
        project = self.create_project(data={'business': exchange.business})
        self.create_project_relationship(data={
            'project': project,
            'contact': person,
        })
        transaction = self.create_transaction(data={'exchange': exchange,
                                                    'project': project,})
        email_exchange_url = reverse('email_exchange', args=(exchange.pk,))
        response = self.client.get(email_exchange_url)
        self.assertEqual(response.status_code, 200)
        data = {
            'to': person.pk,
            'memo': self.random_string(500),
        }
        response = self.client.post(email_exchange_url, data)
        self.assertNoFormErrors(response)
        view_business_url = reverse('view_business', 
                                    args=(exchange.business.pk,))
        self.assertRedirects(response, view_business_url)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(
            message.subject, 
            ' '.join([
                project.name, 
                exchange.type.label,
                datetime.datetime.today().strftime('%Y-%m-%d'),
            ]),
        )
        self.assertEqual(message.body.strip(), data['memo'])
        self.assertTrue(person.email in message.to)
