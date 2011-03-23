##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Zope's HTTP-specific Publisher interfaces.

$Id: http.py 97651 2009-03-08 08:32:59Z nadako $
"""
from zope.publisher.interfaces import IView


class IHTTPView(IView):
    "HTTP View"


class ILogin(IHTTPView):
    """A simple login interface."""

    def login():
        """Login the user.

        This method should generate some sort of UI to request the username
        and password.
        """


class ILogout(IHTTPView):
    """A simple logout interface."""

    def logout():
        """Logout the user.

        This can mean different things. For example, when dealing with
        cookie-based logins (browser), then it simply means deleting the
        cookie. If we deal with HTTP Authentication, we just want to send
        another challenge.
        """
