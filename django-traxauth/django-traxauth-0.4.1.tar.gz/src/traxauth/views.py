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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from profiles import views as profiles_views
from traxauth.forms import UserChangeForm, UserProfileForm


@login_required
def profile_redirect(request, *args, **kwargs):
    """ This view is displayed right after login.
    
    It does not do much, but redirect to the user's profile page
    
    """
    redirect_to = reverse('profiles_profile_detail', args=[request.user.username])
    return HttpResponseRedirect(redirect_to)


@login_required
def create_profile(request, *args, **kwargs):
    if request.method == 'POST':
        userform = UserChangeForm(data=request.POST, instance=request.user)
        if userform.is_valid():
            userform.save()
    else:
        userform = UserChangeForm(instance=request.user)
        kwargs['extra_context'] = {'userform': userform}
    return profiles_views.create_profile(request, *args, **kwargs)


@login_required
def edit_profile(request, *args, **kwargs):
    if request.method == 'POST':
        userform = UserChangeForm(data=request.POST, instance=request.user)
        if userform.is_valid():
            userform.save()
    else:
        userform = UserChangeForm(instance=request.user)
        kwargs['extra_context'] = {'userform': userform}
    kwargs['form_class'] = UserProfileForm
    return profiles_views.edit_profile(request, *args, **kwargs)


def profile_detail(request, *args, **kwargs):
    kwargs['public_profile_field'] = 'is_public'
    return profiles_views.profile_detail(request, *args, **kwargs)


def profile_list(request, *args, **kwargs):
    kwargs.update({
        'public_profile_field': 'is_public',
    })
    return profiles_views.profile_list(request, *args, **kwargs)

