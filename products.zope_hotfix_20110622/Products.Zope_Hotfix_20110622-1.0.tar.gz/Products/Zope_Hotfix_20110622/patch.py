##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import logging
from zExceptions import Forbidden
from zope.traversing import namespace
from zope.interface.interface import InterfaceClass
from zope.traversing.namespace import getResource

log = logging.getLogger('Zope_Hotfix_20110622')

def new_resource_traverse(self, name, ignored):
    # The context is important here, since it becomes the parent of the
    # resource, which is needed to generate the absolute URL.
    res = getResource(self.context, name, self.request)
    if isinstance(res, InterfaceClass):
        raise Forbidden('Access to traverser is forbidden.')
    return res

namespace.resource.traverse = new_resource_traverse

log.info('Patched traverse method of zope.traversing.namespaces.resource.')

def new_init(self, context, request=None):
    raise Forbidden('Access to traverser is forbidden.')

TO_DISABLE = ['acquire', 'attr', 'item', 'lang', 'vh']
for name in TO_DISABLE:
    cls = getattr(namespace, name)
    cls.__init__ = new_init
    cls.traverse = None
    log.info('Disabled %s traverser.' % name)

log.info('Hotfix installed.')
