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
$Id: macro.py 108174 2010-01-16 09:12:27Z jukart $
"""
__docformat__ = "reStructuredText"

from StringIO import StringIO

from zope.tal.talinterpreter import TALInterpreter

class Macro(object):
    """Provides a single macro from a template for rendering."""

    def __init__(self, template, macroName, view, request, contentType):
        self.template = template
        self.macroName = macroName
        self.view = view
        self.request = request
        self.contentType = contentType

    def __call__(self, *args, **kwargs):
        try:
            program = self.template.macros[self.macroName]
        except KeyError:
            raise KeyError('Macro "%s" not found in file "%s"'% (
                self.macroName, self.template.filename))
        output = StringIO(u'')
        namespace = self.template.pt_getContext(self.view,
                                                self.request,
                                                options=kwargs)
        context = self.template.pt_getEngineContext(namespace)
        debug_flags = self.request.debug
        TALInterpreter(
                program,
                None,
                context,
                output,
                tal=True,
                showtal=getattr(debug_flags, 'showTAL', 0),
                strictinsert=0,
                sourceAnnotations=getattr(debug_flags, 'sourceAnnotations', 0),
                )()
        if not self.request.response.getHeader("Content-Type"):
            self.request.response.setHeader("Content-Type",
                                            self.contentType)
        return output.getvalue()

