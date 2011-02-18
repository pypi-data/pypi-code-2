# -*- coding: utf-8 -*-
#
#  This file is part of django-context-extras.
#
#  django-context-extras provides some extra context processors that are often needed by Django projects.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-context-extras
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-context-extras
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

from django.db.models.loading import cache
from django.conf import settings


def current_site(request):
    """A context processor to add the "site" object to the current Context.
    
    To add the 'current_site' context processor to your project, add the
    'context_extras.context_processors.current_site' module in the
    TEMPLATE_CONTEXT_PROCESSORS setting in your settings.py file
    
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'context_extras.context_processors.current_site',
        ...
    )
    
    """
    
    Site = cache.get_model('sites', 'Site')
    try:
        return {
            'site': Site.objects.get_current(),
        }
    except Site.DoesNotExist:
        return {
            'site': None,
        }


def project_settings(request):
    """A context processor to add the "settings" object to the current Context.
    
    To add the 'project_settings' context processor to your project, add the
    'context_extras.context_processors.project_settings' module in the
    TEMPLATE_CONTEXT_PROCESSORS setting in your settings.py file
    
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'context_extras.context_processors.project_settings',
        ...
    )
    
    """
    
    return {
        'settings': settings,
    }


def protocol_host(request):
    """A context processor to add a context variable containing the protocol
    and the host.
    
    To add the 'protocol_host' context processor to your project, add the
    'context_extras.context_processors.protocol_host' module in the
    TEMPLATE_CONTEXT_PROCESSORS setting in your settings.py file
    
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'context_extras.context_processors.protocol_host',
        ...
    )
    
    """
    proto = 'http'
    if request.is_secure():
        proto = 'https'
    return {
        'PROTOHOST': '%s://%s' % (proto, request.get_host()),
    }

