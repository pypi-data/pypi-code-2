##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""LDAP Adapter interfaces.

$Id: interfaces.py 84074 2008-02-20 12:29:24Z torsti $
"""
import zope.interface
import zope.schema

from ldapadapter.field import LDAPURI
from i18n import MessageFactory as _


# LDAP Adapter management errors

class LDAPURIParseError(Exception):
    """The given ldap uri is not valid."""

LDAP_uri_parse_error = _(u'The LDAP URI could not be parsed.')


# LDAP Adapter exceptions

class LDAPException(Exception):
    """LDAP exception"""

class ServerDown(LDAPException):
    """The server doesn't answer"""

class InvalidCredentials(LDAPException):
    """The credentials are incorrect"""

class NoSuchObject(LDAPException):
    """The base object doesn't exist"""


class ILDAPAdapter(zope.interface.Interface):
    """Adapter to an LDAP server."""
    host = zope.schema.TextLine(
        title=_("Host"),
        default=u'localhost',
        required=True,
        )
    port = zope.schema.Int(
        title=_("Port"),
        default=389,
        required=True,
        )
    useSSL = zope.schema.Bool(
        title=_("Use SSL"),
        default=False,
        )
    bindDN = zope.schema.TextLine(
        title=_("Bind DN"),
        default=u'',
        required=False,
        )
    bindPassword = zope.schema.Password(
        title=_("Bind password"),
        default=u'',
        required=False,
        )

    def connect(dn, password=None):
        """Connect to the server.

        Returns an ILDAPConnection.

        May raise InvalidCredentials.
        """

class ILDAPAdapterManagement(zope.interface.Interface):
    serverURL = LDAPURI(
        title=_("Server URL"),
        description=_(
            "Specify the LDAP URL of the server. Examples:\n"
            "\n"
            "ldap:///\n",
            "ldaps://localhost:389/\n",
            ),
        default="ldap://localhost",
        )
    bindDN = zope.schema.TextLine(
        title=_("Bind DN"),
        default=u'',
        required=False,
        )
    bindPassword = zope.schema.Password(
        title=_("Bind password"),
        default=u'',
        required=False,
        )

class IManageableLDAPAdapter(ILDAPAdapter,
                             ILDAPAdapterManagement):
    """LDAP Adapter with management functions."""


class ILDAPConnection(zope.interface.Interface):
    """LDAP connection to a server, bound to a user."""

    def add(dn, entry):
        """Add an entry.

        - dn is a unicode dn.

        - entry is a mapping whose values are lists.
        """

    def delete(dn):
        """Delete an entry.

        dn is a unicode dn.
        """

    def modify(dn, entry):
        """Modify an entry.

        - dn is a unicode dn.

        - entry is the subset of attributes we want to modify.

        May raise NoSuchObject.
        """

    def search(base, scope='one', filter='(objectClass=*)', attrs=None):
        """Search an LDAP server.

        - base is a unicode dn.

        - scope is 'base, 'one' or 'sub'.

        - filter is a unicode LDAP filter (rfc2254).

        - attrs may be a list of entry attributes to return, or None to
          return them all.

        Returns a sequence of (dn, entry), where dn is unicode and entry
        is a mapping whose values are lists of unicode strings.

        May raise NoSuchObject.
        """
        # TODO: some values are binary and should not be converted to unicode


class ICheckLDAPAdapter(zope.interface.Interface):
    """A test adapter for to test the connection between Zope and LDAP."""

    def testConnection():
        """Test the LDAP connection.

        Returns a report about connecting the LDAP server.

        Each step of connecting the server is reported as a string
        in a report (list).
        """
