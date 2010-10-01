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
$Id: evolve1.py 106095 2009-11-29 04:51:14Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.component.interfaces import ISite
from zope.i18n.interfaces import INegotiator
from zope.app.generations.utility import findObjectsProviding
from zope.app.generations.utility import getRootFolder

from z3c.language.negotiator import interfaces


def evolve(context):
    """Evolve the ZODB.

    - Remove sessionLanguage from INegotiator utilities

    - Convert _offeredLangauges attribute to offeredLangauges property

    """
    root = getRootFolder(context)

    for site in findObjectsProviding(root, ISite):

        # check if we got the right object
        obj = zope.component.queryUtility(INegotiator, context=site)
        if interfaces.INegotiatorManager.providedBy(obj):

            # remove old unused ``sessionLanguages`` attr from all objects
            delattr(obj, '_sessionLanguages')

            # migrate ``_serverLanguage`` to ``serverLanguage``
            serverLanguage = getattr(obj, '_serverLanguage')
            if not serverLanguage:
                serverLanguage = u'en'
            setattr(obj, 'serverLanguage', serverLanguage)
            delattr(obj, '_serverLanguage')

            # migrate ``_offeredLanguages`` to ``offeredLanguages``
            offeredLanguages = getattr(obj, '_offeredLanguages')
            setattr(obj, 'offeredLanguages', offeredLanguages)
            delattr(obj, '_offeredLanguages')
