# encoding: utf-8
"""
This module defines a single template tag that will return a context object for
your Last.fm widget. It contains a title for the widget and a ``<div>``
container. This container includes the AJAX code that retrieves the data from
the ``lastfm`` view and generates an image for each item.

.. sourcecode:: html+django

    {% load lastfm_widget %}

    {% get_lastfm_widget as lastfm_widget %}
    <h2>{{ lastfm_widget.title }}</h2>
    {{ lastfm_widget.content }}

The generated code will roughly look like this:

.. sourcecode:: html

    <div class="lastfm">
        <div><a><img /></a></div>
        <div><a><img /></a></div>
        <!-- ... -->
    </div>

The surrounding ``<div>`` has the CSS class *lastfm*. You can use this to
customize the style of the widget. This how it could look like:

.. sourcecode:: css

    #sidebar > #lastfm {
        min-height: 225px; /* required due to "float: left" in the next sec. */
    }

    #sidebar #lastfm div {
        width: 54px;
        height: 39px;
        overflow: hidden;
        float: left;
        border: 1px solid white;
        -moz-border-radius: 2px;
        -khtml-border-radius: 2px;
        border-radius: 2px;
        margin: 0px 2px 4px 2px;
    }

    #sidebar #lastfm div:active, #sidebar #lastfm div:hover {
        border-color: #9FC765;
    }

    #sidebar #lastfm img {
        width: 54px;
        min-height: 39px;
    }

"""
from django import template
from django.conf import settings


register = template.Library()


class LastfmWidgetNode(template.Node):
    """
    This class will create a context object named ``var_name``. It will contain
    the ``title`` and the ``content`` of the widget.

    """
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        """Load the template and render it into a context variable."""
        t = template.loader.get_template('lastfm_widget/_widget.html')
        lastfm_widget = {
            'title': settings.LASTFM_WIDGET_TITLE,
            'content': t.render(template.Context({},
                    autoescape=context.autoescape)),
        }

        context[self.var_name] = lastfm_widget
        return ''


@register.tag
def get_lastfm_widget(parser, token):
    """Get the variable name for the widget from the template tag."""
    try:
        tagname, _as, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires two arguments.' %
                token.contents.split()[0])
    return LastfmWidgetNode(var_name)
