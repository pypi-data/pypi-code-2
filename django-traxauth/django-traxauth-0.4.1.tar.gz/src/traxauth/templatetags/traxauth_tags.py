# -*- coding: utf-8 -*-
#
#  This file is part of django-vcs-manager.
#
#  django-vcs-manager is a version control system manager and gateway.
#
#  Copyright (c) 2010 George Notaras <gnot@g-loaded.eu>
#
#  Sponsored by:
#    - http://www.g-loaded.eu/
#    - http://www.codetrax.org/
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-vcs-manager
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-vcs-manager
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

"""
In order to use these template tags you need to use the following in your templates

{% load traxauth_tags %}

"""

try:
    import hashlib
    md5 = hashlib.md5
except ImportError:
    import md5
    md5 = md5.new

from django import template


register = template.Library()



@register.inclusion_tag('traxauth/gravatar.html')
def gravatar_for_email(email, size=32):
    url = "http://www.gravatar.com/avatar/%s?size=%d" % (md5(email).hexdigest(), size)
    return {
        'url': url,
        'size': size,
    }


@register.simple_tag
def object_as_p(object):
    p = []
    field_names = object._meta.get_all_field_names()
    for field_name in field_names:
        field_value = getattr(object, field_name)
        p.append('<p>%s: %s</p>' % (field_name, field_value))
    return '\n'.join(p)

