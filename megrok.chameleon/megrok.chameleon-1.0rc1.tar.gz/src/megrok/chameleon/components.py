##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
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
"""Chameleon page template components"""
import os
from grokcore.component import GlobalUtility, implements, name
from grokcore.view import interfaces
from grokcore.view.components import GrokTemplate
from z3c.pt.pagetemplate import ViewPageTemplate, ViewPageTemplateFile

#
# Chameleon Zope Page Templates...
#
class PageTemplate(ViewPageTemplate):
    """A `z3c.pt` page template suitable for use with views.

    This page template implementation is different from `z3c.pt`
    implementation in two respects:

    - It sets ``python`` as default mode (instead of ``path``)
    - It injects any views ``static`` variable in template namespace.
    """
    default_expression = 'python' # Use the chameleon default

    def _pt_get_context(self, view, request, kwargs):
        """Get context vars for a template.

        Inject ``static`` var in template namespace.
        """
        context = super(PageTemplate, self)._pt_get_context(
            view, request, kwargs)
        context.update(kwargs)
        return context

class PageTemplateFile(PageTemplate, ViewPageTemplateFile):
    """A `z3c.pt` page template file suitable for use with views.

    This implementation is different from `z3c.pt` implementation in
    two respects:

    - It sets ``python`` as default mode (instead of ``path``)
    - It injects any views ``static`` variable in template namespace.
    """
    default_expression = 'python'

class ChameleonPageTemplate(GrokTemplate):

    def setFromString(self, string):
        self._filename = None
        self._template = PageTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        self._filename = filename
        self._prefix = _prefix
        self._template = PageTemplateFile(os.path.join(_prefix, filename))
        return

    @property
    def macros(self):
        return self._template.macros

    def render(self, view):
        return self._template(**self.getNamespace(view))

class ChameleonPageTemplateFactory(GlobalUtility):
    implements(interfaces.ITemplateFileFactory)
    name('cpt')

    def __call__(self, filename, _prefix=None):
        return ChameleonPageTemplate(filename=filename, _prefix=_prefix)
