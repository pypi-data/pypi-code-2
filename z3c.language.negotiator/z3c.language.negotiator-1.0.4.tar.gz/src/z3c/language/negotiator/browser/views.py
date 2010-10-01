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
$Id: views.py 81875 2007-11-16 03:52:32Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.i18n.interfaces import INegotiator
from zope.publisher.browser import BrowserView

from z3c.language.negotiator import IOfferedLanguages


class NegotiatorView(BrowserView):

    zope.interface.implements(IOfferedLanguages)

    def getOfferedLanguages(self):
        """View for listing  available (offered) languages."""

        negotiator = zope.component.getUtility(INegotiator, '', self.context)

        try:
            offeredLanguages = negotiator.offeredLanguages
        except AttributeError:
            # we don't have a Negotiator instance
            # we got the global zope.i18n Negotiator
            offeredLanguages = []

        return offeredLanguages

    def hasOfferedLanguages(self):
        """View for to check if we have i18n session support."""

        negotiator = zope.component.getUtility(INegotiator, '', self.context)

        try:
            offeredLanguages = negotiator.offeredLanguages
            return True
        except AttributeError:
            # we don't have a Negotiator instance
            # we got the global zope.i18n Negotiator
            return False
