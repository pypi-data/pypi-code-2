"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django import forms
from django.test import TestCase, Client
from django.contrib.auth.models import User
from chimpy.chimpy import ChimpyException
from django_mailchimp_forms.forms import chimpy_form_class_wrapper, ChimpyForm, chimpy_form_instance_wrapper
from django_mailchimp_forms.models import MailingList
from django_mailchimp_forms.utils import register_user, unregister_user, retry_unconfirmed_registrations

TEST_EMAIL = "test_email@email.com"

class ModelApiTest(TestCase):
    # fixtures contain one unregistered and one registered user
    fixtures = ['auth.user.json', 'mailing_list.json']

    def setUp(self):
        self.guest = User.objects.get(username="guest")
        self.guest2 = User.objects.get(username="guest2")

    def tearDown(self):
        self.guest = User.objects.get(username="guest")
        ml = MailingList.objects.get_or_create(user=self.guest)[0]
        ml.confirmed = True
        ml.save()
        try:
            unregister_user(self.guest)
        except ChimpyException, e:
            pass

        self.guest2 = User.objects.get(username="guest2")
        try:
            self.guest2.mailinglist.delete()
        except MailingList.DoesNotExist, e:
            pass
        try:
            register_user(self.guest2)
        except ChimpyException, e:
            pass

    def test_add_user_to_mailing_list(self):
        self.assertRaises(MailingList.DoesNotExist,
                          lambda: self.guest.mailinglist)
        register_user(self.guest)
        assert self.guest.mailinglist.id
        self.assertEqual(self.guest.mailinglist.confirmed, True)
    
    def test_remove_user_from_mailing_list(self):
        assert self.guest2.mailinglist.id
        unregister_user(self.guest2)
        self.guest2 = User.objects.get(username="guest2")
        self.assertRaises(MailingList.DoesNotExist,
                          lambda: self.guest2.mailinglist)

    def test_register_unconfirmed_users(self):
        MailingList(user=self.guest, confirmed=False).save()
        retry_unconfirmed_registrations()
        assert self.guest.mailinglist.id
        self.assertEqual(self.guest.mailinglist.confirmed, True)

    def test_default_form(self):
        form = ChimpyForm({'username': "guest3", 'password1': "guest3",
                           'password2': "guest3", 'email': TEST_EMAIL,
                           'newsletter': True})
        assert form.is_valid()
        guest3 = form.save()
        assert guest3.id
        self.assertEqual(guest3.username, "guest3")
        self.assertEqual(guest3.email, TEST_EMAIL)
        assert guest3.mailinglist.id
        self.assertEqual(guest3.mailinglist.confirmed, True)

    def test_class_wrapper(self):
        class test_form(forms.Form):
            username = forms.CharField(required=True)
            password = forms.CharField(required=True, widget=forms.PasswordInput)

            def save(self):
                username = self.cleaned_data['username']
                password = self.cleaned_data['password']
                return User.objects.create_user(username, '', password)
        form_class = chimpy_form_class_wrapper(test_form)
        form = form_class({
            'username': "guest3", 'password': "guest3",
            'email': TEST_EMAIL, 'newsletter': True
        })
        assert form.is_valid()
        guest3 = form.save()
        assert guest3.id
        self.assertEqual(guest3.username, "guest3")
        self.assertEqual(guest3.email, TEST_EMAIL)
        assert guest3.mailinglist.id
        self.assertEqual(guest3.mailinglist.confirmed, True)

    def test_instance_wrapper(self):
        class test_form(forms.Form):
            username = forms.CharField(required=True)
            password = forms.CharField(required=True, widget=forms.PasswordInput)

            def save(self):
                username = self.cleaned_data['username']
                password = self.cleaned_data['password']
                return User.objects.create_user(username, '', password)
        post_data = {'username': "guest3", 'password': "guest3",
                     'email': TEST_EMAIL, 'newsletter': True }
        form = test_form(post_data)
        form = chimpy_form_instance_wrapper(form, post_data)
        assert form.is_valid()
        guest3 = form.save()
        assert guest3.id
        self.assertEqual(guest3.username, "guest3")
        self.assertEqual(guest3.email, TEST_EMAIL)
        assert guest3.mailinglist.id
        self.assertEqual(guest3.mailinglist.confirmed, True)

    def test_default_form_raises_when_email_is_blank(self):
        form = ChimpyForm({'username': "guest3", 'password1': "guest3",
                           'password2': "guest3", 'email': '',
                           'newsletter': True})
        assert not form.is_valid()

class UserExperienceTest(TestCase):
    # fixtures contain one unregistered and one registered user
    fixtures = ['auth.user.json', 'mailing_list.json']
    # urls = 'django_mailchimp_forms.urls'

    def setUp(self):
        self.guest = User.objects.get(username="guest")
        self.guest_client = Client()
        self.guest_client.login(username="guest", password="guest")
        self.guest2 = User.objects.get(username="guest2")
        self.guest2_client = Client()
        self.guest2_client.login(username="guest2", password="guest2")

    def tearDown(self):
        self.guest = User.objects.get(username="guest")
        ml = MailingList.objects.get_or_create(user=self.guest)[0]
        ml.confirmed = True
        ml.save()
        try:
            unregister_user(self.guest)
        except ChimpyException, e:
            pass

        self.guest2 = User.objects.get(username="guest2")
        try:
            self.guest2.mailinglist.delete()
        except MailingList.DoesNotExist, e:
            pass
        try:
            register_user(self.guest2)
        except ChimpyException, e:
            pass

    def test_user_register(self):
        self.assertRaises(MailingList.DoesNotExist,
                          lambda: self.guest.mailinglist)
        self.guest_client.post("/mailing_list/register/?next=/", {})
        assert self.guest.mailinglist.id
        self.assertEqual(self.guest.mailinglist.confirmed, True)

    def test_user_unregister(self):
        assert self.guest2.mailinglist.id
        self.guest2_client.post("/mailing_list/unregister/?next=/", {})
        self.guest2 = User.objects.get(username="guest2")
        self.assertRaises(MailingList.DoesNotExist,
                          lambda: self.guest2.mailinglist)

    def test_user_sign_up_with_mailinglist(self):
        self.client.post('/accounts/register/', {
            'username': "guest3", 'password1': "guest3",
            'password2': "guest3", 'email': TEST_EMAIL,
            'mailing_list': True
        })
        guest3 = User.objects.get(username="guest3")
        assert guest3.mailinglist.id
        self.assertEqual(self.guest3.mailinglist.confirmed, True)

    def test_user_sign_up_without_mailinglist(self):
        self.client.post('/accounts/register/', {
            'username': "guest3", 'password1': "guest3",
            'password2': "guest3", 'email': TEST_EMAIL,
            'mailing_list': False
        })
        guest3 = User.objects.get(username="guest3")
        self.assertRaises(MailingList.DoesNotExist,
                          lambda: guest3.mailinglist)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

