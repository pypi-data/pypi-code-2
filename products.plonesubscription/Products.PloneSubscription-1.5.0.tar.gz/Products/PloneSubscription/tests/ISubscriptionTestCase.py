# -*- coding: utf-8 -*-
## PloneSubscription
## A Plone tool supporting different levels of subscription and notification
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
This module implements subscription interface testcase
"""
__version__ = "$Revision: 18686 $"
# $Source$
# $Id: ISubscriptionTestCase.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from Interface import Attribute, Interface

class ISubscriptionTestCase(Interface):
    """Subscription Interface"""

    def test_getSubscriber(self):
        """Return the subscriber that the subscription depends on"""
        raise NotImplementedError

    def test_getQuery(self):
        """Return the request used for catalog query"""
        raise NotImplementedError

    def test_getQueryBrains(self):
        """Return the list of brains concerned by the mailing"""
        raise NotImplementedError

    def test_afterQueryFilters(self, brains):
        """Filters query result with subscription options"""
        raise NotImplementedError

    def test_getSubscriptionUrl(self):
        """Return the url of the object or concept subscribed on"""
        raise NotImplementedError
