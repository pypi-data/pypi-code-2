# -*- coding: utf-8 -*-
import unittest
import urllib

from django.contrib.admin.models import User
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import QueryDict
from django import forms


from quieter_formset.formset import BaseFormSet, BaseModelFormSet


class ArticleForm(forms.Form):
    title = forms.CharField()


class Management:
    def basic(self, **kw):
        for k, v in kw.items():
            kw['form-%s' % k] = v
        formset = self.formset(kw)
        assert not formset.is_valid()
        assert formset.non_form_errors()

    def test_almost_empty(self):
        self.basic(title=1)

    def test_mangled(self):
        self.basic(TOTAL_FORMS='asd')

    def test_mangled2(self):
        self.basic(INITIAL_FORMS='abc',
                   MAX_NUM_FORMS='abc')

    def test_mangled3(self):
        self.basic(TOTAL_FORMS='a',
                   INITIAL_FORMS=1,
                   MAX_NUM_FORMS=1)

    def test_mangled4(self):
        self.basic(TOTAL_FORMS=10)

    def test_mangled5(self):
        self.basic(TOTAL_FOOBAR='asd')

    def test_unicode_mangled(self):
        self.basic(TOTAL_FORMS=1,
                   INITIAL_FORMS='ĦĤϕ')


class TestManagement(unittest.TestCase, Management):
    def setUp(self):
        self.formset = formset_factory(ArticleForm, formset=BaseFormSet)


class TestModelManagement(unittest.TestCase, Management):
    def setUp(self):
        self.formset = modelformset_factory(User, formset=BaseModelFormSet)
        self.user = User.objects.create(username='andymckay')
        self.data = {'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 1,
                     'form-MAX_NUM_FORMS': 1}

    def tearDown(self):
        User.objects.all().delete()

    def test_mangled_id(self):
        data = self.data.copy()
        data.update({'form-0-id':'asdawd'})
        self.formset = modelformset_factory(User, formset=BaseModelFormSet)
        fs = self.formset(data, queryset=User.objects.all())
        assert len(fs.forms) == 1

    def test_one_bad_apple(self):
        data = self.data.copy()
        data.update({'form-0-id':'asdawd', 'form-1-id':self.user.pk,
                     'form-TOTAL_FORMS': 2})
        self.formset = modelformset_factory(User, formset=BaseModelFormSet)
        fs = self.formset(data, queryset=User.objects.all())
        assert len(fs.forms) == 2

    def test_one_non_existant_apple(self):
        # Test for https://bugzilla.mozilla.org/show_bug.cgi?id=614108
        # and https://bugzilla.mozilla.org/show_bug.cgi?id=625603
        data = self.data.copy()
        data.update({'form-0-id':self.user.pk,
                     'form-TOTAL_FORMS': 1})
        self.formset = modelformset_factory(User, formset=BaseModelFormSet)
        self.formset._queryset = User.objects.none()
        fs = self.formset(data)
        assert not fs.is_valid()

    def test_key(self):
        data = self.data.copy()
        data.update({'form-0-id':self.user.pk,
                     'form-TOTAL_FORMS': 2,
                     'form-INITIAL_FORMS': 2})
        self.formset = modelformset_factory(User, formset=BaseModelFormSet)
        fs = self.formset(data)
        assert not fs.is_valid()

    def test_multivaluedictkey(self):
        # https://bugzilla.mozilla.org/show_bug.cgi?id=653147
        data = self.data.copy()
        data.update({'form-0-id':[self.user.pk],
                     'form-TOTAL_FORMS': 2,
                     'form-INITIAL_FORMS': 2})
        data = QueryDict(urllib.urlencode(data))
        self.formset = modelformset_factory(User, formset=BaseModelFormSet)
        fs = self.formset(data)
        assert not fs.is_valid()
