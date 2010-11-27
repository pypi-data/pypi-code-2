# -*- coding: utf-8 -*-
#
#  This file is part of django-content-licenses.
#
#  django-content-licenses is a Django app that adds support for adding licensing information to content.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-content-licenses
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-content-licenses
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from django.db import models


class License(models.Model):

    name = models.CharField(max_length=100, unique=True,
        help_text="""The full name of the license.""")
    slug = models.SlugField(max_length=100, unique=True,
        help_text="""This is used to determine the license's template name. For example, if the slug is 'my-license', then the template name is expected to be 'content_licenses/my-license.html'.""")
    abbreviation = models.CharField(max_length=50, blank=True, null=True,
        help_text="""The short name of the license.""")
    url = models.URLField(verify_exists=True, blank=True, null=True,
        help_text="""The URL to the legal text/online representation of the license.""")
    logo = models.URLField(verify_exists=True, blank=True, null=True,
        help_text=""""A logo/icon/badge that is clearly associated with the license.""")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True,
        help_text="""Disable, if license shouldn't be available to users any more.""")
    
    date_created = models.DateTimeField(verbose_name='created on', auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='last modified on', auto_now=True)
    #created_by = models.ForeignKey('auth.User', related_name='%(class)s_created_by')

    def __unicode__(self):
        return self.name

    def _template_name(self):
        return 'content_licenses/%s.html' % self.slug
    template_name = property(_template_name)
    
    class Meta:
        ordering = ('name', )
        verbose_name = 'license'
        verbose_name_plural = 'licenses'

