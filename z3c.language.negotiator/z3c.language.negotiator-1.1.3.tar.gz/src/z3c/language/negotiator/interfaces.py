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
$Id: interfaces.py 114887 2010-07-21 12:06:15Z adamg $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.i18nmessageid
import zope.schema
from zope.schema.interfaces import IVocabularyTokenized

_ = zope.i18nmessageid.MessageFactory('z3c')


language_policies = ['server', 'session', 'browser',
    'browser --> session --> server', 'browser --> server',
    'session --> browser --> server', 'session --> server']

LANGUAGE_CACHE_KEY = 'z3c.language.negotiator.cache'

class INegotiatorManager(zope.interface.Interface):
    """Local negotiator utility manager interface."""

    policy = zope.schema.Choice(
        title=_("Language lookup policy"),
        description=_("Defines how the language lookup is working."),
        values=language_policies,
        default='session --> browser --> server',
        required=True)

    serverLanguage = zope.schema.TextLine(
        title=_(u"Server language"),
        description=_(u"The language used for server policy."),
        default=u"en",
        required=True,
        )

    offeredLanguages = zope.schema.List(
        title=_(u"Offered languages"),
        description=_(u"A list of offered languages. Can be used for "
                      "let the user to select languages which are offered in "
                      "a skin."""),
        value_type = zope.schema.TextLine(title=_(u"A i18n language."),
            description=_(u"A i18n locale string.")),
        default=[],
        required=False,
        )

    cacheEnabled = zope.schema.Bool(
        title=_(u"Language caching enabled"),
        description=_(u"Language caching enabled (per request)"),
        default=False,
        )

    def clearCache(request):
        """Clear the cached language value"""


class IOfferedLanguages(zope.interface.Interface):

    def getOfferedLanguages():
        """A list of available (offered) languages."""

    def hasOfferedLanguages():
        """Retruns a boolean for available offered languages."""


class IOfferedLanguagesVocabulary(IVocabularyTokenized):
    """A vocabulary of available (offered) languages."""


class IAvailableTranslationDomainLanguagesVocabulary(IVocabularyTokenized):
    """Available translation domain languages.

    If you use this, take care on that you use the right translation domain.
    So you probably have to implement your own vocabulary for your ``correct``
    translation domain.
    """
