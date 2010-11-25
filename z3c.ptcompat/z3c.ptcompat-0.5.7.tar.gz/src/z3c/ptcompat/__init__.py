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
$Id: __init__.py 81270 2007-10-31 14:02:39Z jukart $
"""
__docformat__ = "reStructuredText"

from StringIO import StringIO
import config

if config.PREFER_Z3C_PT:
    from z3c.pt.pagetemplate import ViewPageTemplateFile
    from z3c.pt.pagetemplate import PageTemplateFile

    def bind_template(pt, view):
        return pt.bind(view)

    def bind_macro(template, view, request, macro):
        return template.bind(
            view, request=request, macro=macro)
    
else:
    from zope.tal.talinterpreter import TALInterpreter
    from zope.pagetemplate.pagetemplatefile import PageTemplateFile
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile    
    from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate as \
         bind_template

    def bind_macro(template, view, request, macro):
        program = template.macros[macro]

        def render(content_type=None, **kwargs):
            output = StringIO(u'')
            namespace = template.pt_getContext(
                view, request, options=kwargs)
            context = template.pt_getEngineContext(namespace)
            TALInterpreter(program, None,
                           context, output, tal=True, showtal=False,
                           strictinsert=0, sourceAnnotations=False)()
            if not request.response.getHeader("Content-Type"):
                request.response.setHeader(
                    "Content-Type", content_type)
            return output.getvalue()

        return render

class ViewPageTemplateFile(ViewPageTemplateFile):
    """View page template file."""

    def __new__(cls, *args, **kwargs):
        inst = object.__new__(cls)
        config.REGISTRY[inst] = (args, kwargs)
        return inst
