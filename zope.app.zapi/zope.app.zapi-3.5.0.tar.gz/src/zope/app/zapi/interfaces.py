##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Interface definition for the Zope convenience API module

$Id: interfaces.py 120642 2011-03-01 11:55:58Z icemac $
"""
from zope.interface import Attribute
from zope.component.interfaces import IComponentArchitecture
from zope.traversing.interfaces import ITraversalAPI
from zope.traversing.browser.interfaces import IAbsoluteURLAPI
from zope.app.publisher.browser import IDefaultViewNameAPI 

class IZAPI(
    IComponentArchitecture,
    ITraversalAPI, IAbsoluteURLAPI,
    IDefaultViewNameAPI
    ):
    """Convenience API for use with Zope applications.
    """

    def name(obj):
        """Return an object's name

        This is the name the object is stored under in the container
        it was accessed in.  If the name is unknown, None is returned.
        """

    def UserError(*args):
        """Return an error message to a user.

        The error is an exception to be raised.

        The given args will be converted to strings and displayed in
        the message shown the user.
        """

    def queryType(object, type):
        """Returns the interface implemented by object that provides type.

        For example, if you have an Image, you often would like to know
        which interface is recognized as a Content Type interface
        (IContentType).  So you would call queryType(myImage, IContentType)
        which would return IImage.
        """
        
    def isinstance(object, cls):
        """Test whether an object is an instance of the given type

        This function is useful because it works even if the instance
        is security proxied.
        """

    def principals():
        """Return the authentication utility
        """

