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

"""
In order to use these template tags you need to use the following in your templates

{% load content_licenses_tags %}

"""

from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


register = template.Library()



class SetLicenseLinkNode(template.Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        LICENSE_LINK_TEMPLATE = "content_licenses/creative-commons-license-hyperlink.html"
        t = template.loader.get_template(LICENSE_LINK_TEMPLATE)
        context[self.context_var] = t.render(template.Context(context))
        return ''

def do_set_license_link(parser, token):
    """
    Stores the license link to a context variable.
    
    Usage::

        {% license_link as [varname] %}
    
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError('%s tag requires two arguments' % bits[0])
    if bits[1] != 'as':
        raise template.TemplateSyntaxError("first argument to %s tag must be 'as'" % bits[0])
    return SetLicenseLinkNode(bits[2])

register.tag('set_license_link', do_set_license_link)


