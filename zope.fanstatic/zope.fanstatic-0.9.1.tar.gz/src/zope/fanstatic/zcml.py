##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
from zope.interface import Interface
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest

import fanstatic

from zope.fanstatic.zopesupport import ZopeFanstaticResource

def create_factory(library):
    def factory(request):
        return ZopeFanstaticResource(request, library)
    return factory

def action_setup(_context):
    """Publish all fanstatic library entry points as resources.
    """
    for library in fanstatic.get_library_registry().values():
        factory = create_factory(library)
        adapts = (IBrowserRequest,)
        provides = Interface
        _context.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (factory, adapts, provides, library.name))

