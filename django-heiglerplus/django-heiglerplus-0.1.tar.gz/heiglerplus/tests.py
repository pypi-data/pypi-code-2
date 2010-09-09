#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse


class AdminTestCase(TestCase):
    
    def _check_view(self, instance, viewcode, **kwargs):
        meta = instance._meta
        url = reverse('admin:%s_%s_%s' %(meta.app_label, meta.module_name, viewcode), **kwargs)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)

    def assertValidAdmin(self, instance):
        self._check_view(instance, 'add')
        self._check_view(instance, 'change', args=[instance.pk])
        self._check_view(instance, 'changelist')
        self._check_view(instance, 'delete', args=[instance.pk])