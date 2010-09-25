##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Pluggable Authentication Utility Interfaces

$Id: interfaces.py 113109 2010-06-04 11:54:46Z janwijbrand $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
import zope.security.interfaces
from zope.app.authentication.i18n import ZopeMessageFactory as _

# BBB: the password managers were moved into zope.password package.
from zope.password.interfaces import IPasswordManager

# BBB: using zope.pluggableauth
from zope.pluggableauth.interfaces import (
    IPlugin, IAuthenticatorPlugin, ICredentialsPlugin,
    IPluggableAuthentication, IPrincipalInfo,
    IFoundPrincipalFactory, IPrincipalFactory, IAuthenticatedPrincipalFactory,
    IPrincipalCreated, IAuthenticatedPrincipalCreated,
    AuthenticatedPrincipalCreated, IFoundPrincipalCreated,
    FoundPrincipalCreated, IQueriableAuthenticator)


class IPrincipal(zope.security.interfaces.IGroupClosureAwarePrincipal):

    groups = zope.schema.List(
        title=_("Groups"),
        description=_(
            """ids of groups to which the principal directly belongs.

            Plugins may append to this list.  Mutating the list only affects
            the life of the principal object, and does not persist (so
            persistently adding groups to a principal should be done by working
            with a plugin that mutates this list every time the principal is
            created, like the group folder in this package.)
            """),
        value_type=zope.schema.TextLine(),
        required=False)


class IQuerySchemaSearch(zope.interface.Interface):
    """An interface for searching using schema-constrained input."""

    schema = zope.interface.Attribute("""
        The schema that constrains the input provided to the search method.

        A mapping of name/value pairs for each field in this schema is used
        as the query argument in the search method.
        """)

    def search(query, start=None, batch_size=None):
        """Returns an iteration of principal IDs matching the query.

        query is a mapping of name/value pairs for fields specified by the
        schema.

        If the start argument is provided, then it should be an
        integer and the given number of initial items should be
        skipped.

        If the batch_size argument is provided, then it should be an
        integer and no more than the given number of items should be
        returned.
        """


class IGroupAdded(zope.interface.Interface):
    """A group has been added."""

    group = zope.interface.Attribute("""The group that was defined""")


class GroupAdded:
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = GroupAdded("group")
    >>> verifyObject(IGroupAdded, event)
    True
    """

    zope.interface.implements(IGroupAdded)

    def __init__(self, group):
        self.group = group

    def __repr__(self):
        return "<GroupAdded %r>" % self.group.id


class IPrincipalsAddedToGroup(zope.interface.Interface):
    group_id = zope.interface.Attribute(
        'the id of the group to which the principal was added')
    principal_ids = zope.interface.Attribute(
        'an iterable of one or more ids of principals added')


class IPrincipalsRemovedFromGroup(zope.interface.Interface):
    group_id = zope.interface.Attribute(
        'the id of the group from which the principal was removed')
    principal_ids = zope.interface.Attribute(
        'an iterable of one or more ids of principals removed')


class AbstractMembersChanged(object):

    def __init__(self, principal_ids, group_id):
        self.principal_ids = principal_ids
        self.group_id = group_id

    def __repr__(self):
        return "<%s %r %r>" % (
            self.__class__.__name__, sorted(self.principal_ids), self.group_id)


class PrincipalsAddedToGroup(AbstractMembersChanged):
    zope.interface.implements(IPrincipalsAddedToGroup)


class PrincipalsRemovedFromGroup(AbstractMembersChanged):
    zope.interface.implements(IPrincipalsRemovedFromGroup)
