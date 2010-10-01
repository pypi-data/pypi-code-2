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
$Id: testing.py 114890 2010-07-21 12:18:55Z adamg $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
from zope.schema import vocabulary
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.publisher.interfaces import IRequest
from zope.session.interfaces import IClientId
from zope.session.interfaces import IClientIdManager
from zope.session.interfaces import ISessionDataContainer
from zope.session.http import CookieClientIdManager
from zope.session import session
from zope.publisher.base import TestRequest

from z3c import testing
from z3c.language.session.interfaces import ILanguageSession
from z3c.language.session.app import LanguageSession
from z3c.language.negotiator import interfaces
from z3c.language.negotiator.vocabulary import OfferedLanguagesVocabulary


###############################################################################
#
# Test component
#
###############################################################################

class TestClientId(object):
    zope.interface.implements(IClientId)
    def __new__(cls, request):
        return 'dummyclientidfortesting'


class LanguageSessionStub(object):

    zope.interface.implements(ILanguageSession)
    zope.component.adapts(IUserPreferredLanguages)

    def __init__(self, request):
        pass

    def getLanguage(self):
        return 'fr'


class EnvStub(TestRequest):
    zope.interface.implements(IUserPreferredLanguages)

    def __init__(self, langs=()):
        self.langs = langs
        TestRequest.__init__(self, '/')

    def getPreferredLanguages(self):
        return self.langs


###############################################################################
#
# placeful setup
#
###############################################################################

from zope.app.testing import setup

def doctestSetUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site

    # session setup
    zope.component.provideAdapter(TestClientId, (IRequest,), IClientId)
    zope.component.provideAdapter(LanguageSession, (IRequest,), 
        ILanguageSession)
    zope.component.provideUtility(CookieClientIdManager(), IClientIdManager)
    rsdc = session.RAMSessionDataContainer()
    zope.component.provideUtility(rsdc, ISessionDataContainer, '')

    # register vocabularies
    vocabulary.setVocabularyRegistry(None)
    vocabulary._clear()
    vr = vocabulary.getVocabularyRegistry()
    
    vr.register('Offered Languages', OfferedLanguagesVocabulary)

def doctestTearDown(test):
    setup.placefulTearDown()
    vocabulary._clear()


###############################################################################
#
# Public base tests
#
###############################################################################

class BaseTestINegotiator(testing.InterfaceBaseTest):
    """Resuable INegotiator base test."""

    def getTestInterface(self):
        return interfaces.INegotiator
