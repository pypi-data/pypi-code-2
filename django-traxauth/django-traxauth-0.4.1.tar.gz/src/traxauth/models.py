# -*- coding: utf-8 -*-
#
#  This file is part of django-traxauth.
#
#  django-traxauth adds support for profile management to Django powered projects.
#
#  Copyright (c) 2010 George Notaras <gnot@g-loaded.eu>
#
#  Sponsored by:
#    - http://www.g-loaded.eu/
#    - http://www.codetrax.org/
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-traxauth
#
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-traxauth
#
#  This project has derived from the old self contained and mod-python
#  based traxauth project, which is copyright (c) 2007 George Notaras.
#    - http://www.codetrax.org/projects/traxauth/wiki
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
from django.utils.translation import ugettext_lazy as _

from traxauth import settings



class UserProfile(models.Model):
    """Defines a profile for users.
    
    Technical Doccumentation
    
    For this to actually be a profile:

     - Set a user field like the one below:
     
        user = models.ForeignKey('auth.User', unique=True)

     - Set the following in the settings.py

        AUTH_PROFILE_MODULE = 'traxauth.UserProfile"
    
    Retrieve the user's profile by:
    
        user.get_profile()
    
    Important Notice
    
    Since the UserProfile model implements some extra methods for users, it is
    required that a user profile is created for every Django user. This is
    taken care of by the post_save signal below.
    
    """
#    GENDER_CHOICES = (
#        ('M', _('Male')),
#        ('F', _('Female')),
#    )
#    
#    gender = models.PositiveSmallIntegerField(verbose_name=_('gender'), choices=GENDER_CHOICES, blank=True, null=True)

    # This is the only required field for profiles to work
    user = models.ForeignKey('auth.User', unique=True, editable=False, related_name='%(class)s_user')
    
    birth_date = models.DateField(verbose_name=_('birth date'), blank=True, null=True)
    birth_date_public = models.BooleanField(verbose_name=_('birthdate public'), default=False, help_text=_("""Mark your birthdate as being publicly viewable."""))

    location = models.CharField(verbose_name=_('location'), max_length=200, null=True, blank=True, help_text=_("""Enter your location. Prefered format: 'City, State, Country'."""))
    about = models.TextField(verbose_name=_('about'), max_length=1000, blank=True, help_text=_("""Enter a short description of yourself."""))
    website = models.URLField(verbose_name=_('website'), verify_exists=False, null=True, blank=True, help_text=_("""Enter the URL to your website."""))
    
    is_public = models.BooleanField(verbose_name=_('public'), default=True, db_index=True, help_text=_("""Mark your profile as being public (checked) or private (unchecked)."""))
    
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __unicode__(self):
        return 'profile of %s' % self.user

    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), {'username': self.user.username})

