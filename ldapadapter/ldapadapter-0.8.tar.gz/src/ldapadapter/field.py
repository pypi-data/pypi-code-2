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
"""LDAP Schema Fields

$Id: field.py 41428 2006-01-25 08:28:46Z rykomats $
"""
import re

import zope.interface

from zope.schema.interfaces import IURI
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import InvalidURI
from zope.schema._bootstrapinterfaces import ValidationError
from zope.schema import URI

from i18n import MessageFactory as _

"""
From RFC 952:

     A "name" (Net, Host, Gateway, or  Domain  name)  is  a  text
     string  up  to  24 characters drawn from the alphabet (A-Z),
     digits (0-9), minus sign (-),  and  period  (.).  Note  that
     periods  are  only  allowed  when they serve to delimit com-
     ponents of "domain style names". (See RFC 921, "Domain  Name
     System  Implementation  Schedule," for background). No blank
     or space characters are permitted as part of a name. No dis-
     tinction  is  made  between  upper and lower case. The first
     character must be an alpha  character.  The  last  character
     must not be a minus sign or period.
"""
_isldapuri = re.compile(
    r"^ldaps?://"         # protocol

    # BEGIN: host
    r"([a-zA-Z]+([a-zA-Z\d\-]*[a-zA-Z\d])*"
    r"(\.[a-zA-Z\d]+([a-zA-Z\d\-]*[a-zA-Z\d])*)*"
    # END: host

    r"|"                  # or

    # BEGIN: IP
    r"([1-9][\d]{0,1}|1[\d]{0,2}|2[0-5]{0,2})"
    r"(\.([\d]{1,2}|1[\d]{0,2}|2[0-5]{0,2})){3})"
    # END: IP

    r"(:[\d]{1,5})?$"     # port
    ).match


# LDAP-Adapter Exeptions
# Note: Located here to avoid circular references.
class InvalidLDAPURI(ValidationError):
    __doc__ = _("""The specified LDAP URI is not valid.""")


class LDAPURI(URI):
    """LDAPURI schema field
    """

    zope.interface.implements(IURI, IFromUnicode)

    def _validate(self, value):
        """
        >>> from ldapadapter.field import LDAPURI
        >>> uri = LDAPURI(__name__='test')
        >>> uri.validate("ldap://www.python.org:389")
        >>> uri.validate("ldaps://www.python.org:389")
        >>> uri.validate("www.python.org")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: www.python.org

        >>> uri.validate("http://www.python.org")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: http://www.python.org

        >>> uri.validate("ldap://www.python.org/foo")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: ldap://www.python.org/foo

        """
        #super(LDAPURI, self)._validate(value)
        if _isldapuri(value):
            return

        raise InvalidLDAPURI, value

    def fromUnicode(self, value):
        r"""
        >>> from ldapadapter.field import LDAPURI
        >>> uri = LDAPURI(__name__='test')
        >>> uri.fromUnicode("ldap://www.python.org:389")
        'ldap://www.python.org:389'
        >>> uri.fromUnicode("ldaps://www.python.org:389")
        'ldaps://www.python.org:389'
        >>> uri.fromUnicode("          ldap://www.python.org:389")
        'ldap://www.python.org:389'
        >>> uri.fromUnicode("      \n    ldap://www.python.org:389\n")
        'ldap://www.python.org:389'
        >>> uri.fromUnicode("ldap://www.pyt hon.org:389")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: ldap://www.pyt hon.org:389

        """
        v = str(value.strip())
        self.validate(v)
        return v
