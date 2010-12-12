##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: zcml.py 78325 2007-07-25 15:43:51Z fdrake $
"""
__docformat__ = "reStructuredText"

import os

from zope import interface
from zope import component
from zope import schema

from zope.component import zcml

from zope.configuration.exceptions import ConfigurationError
import zope.configuration.fields

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.pagetemplate.interfaces import IPageTemplate
from zope.configuration.fields import GlobalObject
from zope import schema

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.viewtemplate.macro import Macro

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope')


class ITemplateDirective(interface.Interface):
    """Parameters for the template directive."""

    template = zope.configuration.fields.Path(
            title=_("Content-generating template."),
            description=_("Refers to a file containing a page template (should "
                          "end in extension ``.pt`` or ``.html``)."),
            required=False,
            )

    macro = schema.TextLine(
            title = _(u'Macro'),
            description = _(u"""
                The macro to be used.
                This allows us to define different macros in on template.
                The template designer can now create macros for the whole site
                in a single page template, and ViewTemplate can then extract
                the macros for single viewlets or views.
                If no macro is given the whole template is used for rendering.
                """),
            required = False,
            default = u'',
            )

    for_ = GlobalObject(
            title = _(u'View'),
            description = _(u'The view for which the template should be used'),
            required = False,
            default=interface.Interface,
            )

    layer = GlobalObject(
            title = _(u'Layer'),
            description = _(u'The layer for which the template should be used'),
            required = False,
            default=IDefaultBrowserLayer,
            )

    contentType = schema.BytesLine(
        title = _(u'Content Type'),
        description=_(u'The content type identifies the type of data.'),
        default='text/html',
        required=False,
        )



class TemplateFactory(object):

    template = None

    def __init__(self, filename, macro, contentType):
        self.filename = filename
        self.macro = macro
        self.contentType = contentType

    def __call__(self, view, request):
        if self.template is None:
            self.template= ViewPageTemplateFile(self.filename,
                                                content_type=self.contentType)
        if self.macro is None:
            return self.template
        return Macro(self.template, self.macro, view,
                     request, self.contentType)


def templateDirective(_context,
                      template,
                      macro=None,
                      for_=interface.Interface,
                      layer=IDefaultBrowserLayer,
                      contentType='text/html',
                      ):
    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = TemplateFactory(template, macro, contentType)

    # register the template
    zcml.adapter(_context, (factory,), IPageTemplate, (for_, layer))

