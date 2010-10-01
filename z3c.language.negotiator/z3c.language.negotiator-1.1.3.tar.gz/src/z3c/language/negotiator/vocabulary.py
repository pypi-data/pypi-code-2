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
$Id: vocabulary.py 106095 2009-11-29 04:51:14Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
from zope.i18n.interfaces import INegotiator
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from z3c.language.negotiator import interfaces


class OfferedLanguagesVocabulary(SimpleVocabulary):
    """A vocabulary of available (offered) languages."""

    zope.interface.implements(interfaces.IOfferedLanguagesVocabulary)

    def __init__(self, context):
        terms = []
        
        # collect offered languages
        negotiator = zope.component.getUtility(INegotiator)
        languages = negotiator.offeredLanguages

        for lang in languages:
            terms.append(SimpleTerm(lang, lang, lang))

        terms.sort(lambda lhs, rhs: cmp(lhs.title, rhs.title))
        super(OfferedLanguagesVocabulary, self).__init__(terms)
