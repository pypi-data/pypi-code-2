#############################################################################
#
# Copyright (c) 2010 Falko Lab and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
import os
import falkolab.cacheburster

from zope.publisher.interfaces.browser import IBrowserSkinType,\
    IDefaultBrowserLayer
from zope.interface.declarations import alsoProvides, implements
from zope.app.testing.functional import ZCMLLayer
from zope.publisher.browser import BrowserView
from zope.browserresource.resource import Resource
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound

from falkolab.cacheburster.interfaces import IVersionedResourceLayer

testsPath = os.path.join(
    os.path.dirname(falkolab.cacheburster.__file__),
    'tests')

class NoFileResource(BrowserView, Resource):
    implements(IBrowserPublisher)
    def publishTraverse(self, request, name):
        raise NotFound(None, name)

    def browserDefault(self, request):
        return self._getBody, ()
    
    def _getBody(self):
        return 'no file resource body'

def NoFileResourceFactory(request):
    return NoFileResource(None, request)

class ITestSkin(IVersionedResourceLayer, IDefaultBrowserLayer):
    pass

alsoProvides(ITestSkin, IBrowserSkinType)

CacheBursterLayer = ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CacheBursterLayer', allow_teardown=True)