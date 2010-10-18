##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
$Id: field.py 91149 2008-09-14 22:39:34Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from z3c.schema.ip import interfaces

def isValidIPAddress(addr):
    """Returns True if the IP address is valid and False if not."""
    # Check that we have four pieces separated by .
    pieces = addr.split('.')
    if len(pieces) != 4:
        return False
    # Now check that each piece is an integer between 0 and 255
    for piece in pieces:
        try:
            num = int(piece)
        except ValueError:
            return False
        if not (num >= 0 and num <= 255):
            return False
    return True


class IPAddress(zope.schema.BytesLine):
    """A valid IP address."""
    zope.interface.implements(interfaces.IIPAddress)

    def _validate(self, value):
        super(IPAddress, self)._validate(value)

        if not isValidIPAddress(value):
            raise interfaces.NotValidIPAdress(value)
