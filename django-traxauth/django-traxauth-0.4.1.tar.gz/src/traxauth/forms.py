# -*- coding: utf-8 -*-
#
#  This file is part of django-traxauth.
#
#  django-traxauth is a Django app that provides support for user account registration and profile management.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-traxauth
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-traxauth
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


from django import forms
from django.db.models.loading import cache
from django.forms import extras

from traxauth.utils import get_last_100_year_range


class UserChangeForm(forms.ModelForm):
    
    class Meta:
        model = cache.get_model('auth', 'User')
        fields = ('first_name', 'last_name')


class UserProfileForm(forms.ModelForm):
    
    birth_date = forms.DateField(
        required=False, widget=extras.SelectDateWidget(years=get_last_100_year_range()))

    class Meta:
        model = cache.get_model('traxauth', 'UserProfile')

