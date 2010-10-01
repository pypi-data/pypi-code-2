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
$Id: app.py 117125 2010-10-01 15:29:15Z adamg $
"""
__docformat__ = 'restructuredtext'

import persistent
import zope.interface

from zope.container import contained
from zope.schema.fieldproperty import FieldProperty
from zope.i18n.interfaces import INegotiator
from zope.i18n.negotiator import negotiator

from z3c.language.session.interfaces import ILanguageSession

from z3c.language.negotiator.interfaces import INegotiatorManager
from z3c.language.negotiator.interfaces import language_policies
from z3c.language.negotiator.interfaces import LANGUAGE_CACHE_KEY



class Negotiator(persistent.Persistent, contained.Contained):
    """Local negotiator implementation.

    The negotiator let you change the policy, which is a alias
    for the lookup mechanism.

    'server' -- The server defines the language

    'session' -- The session defines the language (useful for testing)

    'browser' -- The browser defines the language (useful for testing)

    'browser --> session --> server' -- Left criteria first

    'browser --> server' -- Left criteria first

    'session --> browser --> server' -- Left criteria first (default use case)

    'session --> server' -- Left criteria first

    The 'server' criteria is used as a fallback criteria in most use cases.

    """

    zope.interface.implements(INegotiator, INegotiatorManager)

    serverLanguage = FieldProperty(INegotiatorManager['serverLanguage'])
    offeredLanguages = FieldProperty(INegotiatorManager['offeredLanguages'])
    cacheEnabled = FieldProperty(INegotiatorManager['cacheEnabled'])

    def __init__(self):
        self._policy = 'session --> browser --> server'

    @apply
    def policy():
        def get(self):
            """Returns the language policy."""
            return self._policy

        def set(self, policy):
            """Set the language policy."""
            if policy not in language_policies:
                policies = str(language_policies)
                raise ValueError('Not a valid policy name.', policy)
            self._policy = policy
        return property(get, set)

    def getLanguage(self, languages, request):
        """Returns the language dependent on the policy."""
        policyList = self._policy.split(' --> ')

        for policy in policyList:

            # the server is handling the language
            if policy == 'server':
                if self.serverLanguage:
                    return self.serverLanguage

            # the language is handled by a session
            elif policy == 'session':
                if self.cacheEnabled:
                    try:
                        cached = request.annotations[LANGUAGE_CACHE_KEY]
                        return cached
                    except KeyError:
                        session = ILanguageSession(request)
                        lang = session.getLanguage()
                        if lang is not None:
                            request.annotations[LANGUAGE_CACHE_KEY] = lang
                            return lang
                else:
                    session = ILanguageSession(request)
                    lang = session.getLanguage()
                    if lang is not None:
                        return lang

            # the language is handled by the browsers language settings
            elif policy == 'browser':
                lang = negotiator.getLanguage(languages, request)
                if lang is not None:
                    return lang

        return None

    def clearCache(self, request):
        try:
            del request.annotations[LANGUAGE_CACHE_KEY]
        except KeyError:
            pass