# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from linkexchange.django import support

register = template.Library()

@stringfilter
def linkexchange_filter(value, request, autoescape = None):
    """
    Django template filter to support linkexchange content filtering.  The
    argument is request object, to access this object add
    'django.core.context_processors.request' to the TEMPLATE_CONTEXT_PROCESSORS
    in your settings.py.

    Usage example:

        {% load linkexchange_tags %}
        {{ page.html|safe|linkexchange_filter:request }}
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    value = esc(value)

    if support.platform is not None:
        value = support.platform.content_filter(
                support.convert_request(request), value)

    return mark_safe(value)

linkexchange_filter.needs_autoescape = True
register.filter('linkexchange_filter', linkexchange_filter)

class LinkExchangeFilterNode(template.Node):
    def __init__(self, request, nodelist):
        self.request = request
        self.nodelist = nodelist

    def render(self, context):
        request = self.request.resolve(context)
        content = self.nodelist.render(context)
        if support.platform is not None:
            content = support.platform.content_filter(
                    support.convert_request(request), content)
        return content

def linkexchange_filter_tag(parser, token):
    """
    Django template tag to support linkexchange content filtering.  The
    argument is request object, to access this object add
    'django.core.context_processors.request' to the TEMPLATE_CONTEXT_PROCESSORS
    in your settings.py.

    Usage example:

        {% load linkexchange_tags %}
        <html>
        <body>
            {% linkexchange_filter request %}
            Page content.
            {% endlinkexchange_filter %}
        </body>
        </html>
    """
    try:
        tag_name, request = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, (
                "%r tag requires a single argument" %
                token.contents.split()[0])
    request = parser.compile_filter(request)
    nodelist = parser.parse(('endlinkexchange_filter',))
    parser.delete_first_token()
    return LinkExchangeFilterNode(request, nodelist)

register.tag('linkexchange_filter', linkexchange_filter_tag)
