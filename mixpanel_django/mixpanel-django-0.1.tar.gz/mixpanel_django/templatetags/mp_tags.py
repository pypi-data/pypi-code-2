#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.template.loader import render_to_string
#from django.template import Node

register = template.Library()

MP_API_TOKEN = getattr(settings, 'MP_API_TOKEN', None)
if not MP_API_TOKEN:
    raise ValueError, 'Mixpanel API token not defined'
MP_EVENT_COMMON_JS_URL = getattr(settings, 'MP_EVENT_COMMON_JS_URL', '/media/scripts/mp_common_events.js')

@register.tag(name="mp_init")
def do_mp_init(parser, token):
    try:
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    if format_string not in ['standard', 'async', 'fbml']:
        raise template.TemplateSyntaxError, '%r tags argument should be one of "standard" or "async"' % tag_name
    return MPInitNode(format_string)

class MPInitNode(template.Node):
    def __init__(self, load_type):
        self.load_type = load_type
        self.context = {'mp_token':MP_API_TOKEN, 'mp_common_events_js':MP_EVENT_COMMON_JS_URL}
    def render(self, context):
        if self.load_type == 'standard':
            res = render_to_string('mp_init_standard.html', self.context)
        elif self.load_type == 'async':
            res = render_to_string('mp_init_async.html', self.context)
        elif self.load_type == 'fbml':
            res = render_to_string('mp_init_fbml.html', self.context)
        return res

