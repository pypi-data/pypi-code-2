# -*- coding: utf-8 -*-
#
#  This file is part of django-primary-filters.
#
#  django-primary-filters provides some extra filters that are often needed by Django projects.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-primary-filters
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-primary-filters
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

import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_spaces_between_tags

from primary_filters import utils


register = template.Library()



@register.filter
@stringfilter
def meshterms(value):
    """Replaces commas with semicolon.
    
    Useful for converting a comma-delimited list of keywords to terms for
    the Dublin Core dc.subject element.
    
    """
    return utils.meshterms(value)


@register.filter
@stringfilter
def dash2space(value):
    """Converts dashes to spaces."""
    return utils.dash2space(value)

    
@register.filter
@stringfilter
def space2dash(value):
    """Converts spaces to dashes."""
    return utils.space2dash(value)


@register.filter
@stringfilter
def strfdt(value, arg):
    """Example Filter
    
    Use with:
    
        {% load primary_filters %}
        ...
        {{ entry.date_published|strfdt:"%A, %d %B" }}
        ...
        
    """
    return utils.strfdt(value, arg)



@register.filter
@stringfilter
def nofollowlinks(value):
    """Adds the nofollow attribute to hyperlinks
    
    Use with:
    
        {% load primary_filters %}
        ...
        {{ comment.comment|nofollowlinks }}
        ...
        
    """
    return utils.nofollowlinks(value)



@register.filter
def sanitize(value, allowed_tags):
    """Strips all HTML tags except those in the 'allowed_tags' list.
    
    Argument should be in form 'tag2:attr1:attr2 tag2:attr1 tag3', where tags
    are allowed HTML tags, and attrs are the allowed attributes for that tag.
    
    Requires: BeautifulSoup
    
    Taken from:
    
        http://www.djangosnippets.org/snippets/1655/
    
    Also see:
    
        http://www.djangosnippets.org/snippets/205/#c2355
    
    """
    return utils.sanitize(value, allowed_tags)



n1 = re.compile(r'>([\s]*)([^<\s]*)')   # strip whitespace between tag and text
n2 = re.compile(r'([^<\s]*)([\s]*)<')   # strip whitespace between text and tag
n3 = re.compile(r'> ([^<]+) </')        # Capture the closest tag pair and strip the whitespace around the text that might have been added by n1 & n2
n4 = re.compile(r'\s+')                 # strip consecutive whitespace characters
@register.filter
@stringfilter
def spaceless_deep(value):
    out = n1.sub(r'> \2', value)
    out = n2.sub(r'\1 <', out)
    out = n3.sub(r'>\1</', out)
    out = n4.sub(r' ', out)
    out = strip_spaces_between_tags(out)
    return out




#
# Template Tags
#

def do_spacelessdeep(parser, token):
    nodelist = parser.parse(('endspacelessdeep',))
    parser.delete_first_token()
    return SpacelessDeepNode(nodelist)

class SpacelessDeepNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        output = self.nodelist.render(context)
        return spaceless_deep(output)

register.tag('spacelessdeep', do_spacelessdeep)

