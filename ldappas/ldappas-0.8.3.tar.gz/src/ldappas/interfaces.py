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
"""LDAP Pluggable Authentication Plugin interfaces

$Id$
"""
import re
import zope.interface
import zope.schema

from i18n import MessageFactory as _


class ILDAPAuthentication(zope.interface.Interface):
    """LDAP-specifc Autentication Plugin for the Pluggable Authentication."""

    adapterName = zope.schema.Choice(
        title=_(u"LDAP Adapter Name"),
        description=_(u"The LDAP adapter name for the connection to be used."),
        vocabulary="LDAP Adapter Names",
        required=True,
        )

    searchBase = zope.schema.TextLine(
        title=_("Search base"),
        description=_(u"The LDAP search base where principals are found."),
        default=u'dc=example,dc=org',
        required=True,
        )

    searchScope = zope.schema.TextLine(
        title=_("Search scope"),
        description=_(u"The LDAP search scope used to find principals."),
        default=u'sub',
        required=True,
        )

    groupsSearchBase = zope.schema.TextLine(
        title=_("Group search base"),
        description=_(u"The LDAP search base where groups are found."),
        required=False,
        )

    groupsSearchScope = zope.schema.TextLine(
        title=_("Group search scope"),
        description=_(u"THe LDAP search scope used to find groups."),
        required=False,
        )
    
    loginAttribute = zope.schema.TextLine(
        title=_("Login attribute"),
        description=_(u"The LDAP attribute used to find principals."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'uid',
        required=True,
        )

    principalIdPrefix = zope.schema.TextLine(
        title=_("Principal id prefix"),
        description=_(u"The prefix to add to all principal ids."),
        default=u'ldap.',
        required=False,
        )

    idAttribute = zope.schema.TextLine(
        title=_("Id attribute"),
        description=_(
            u"The LDAP attribute used to determine a principal's id."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'uid',
        required=True,
        )

    titleAttribute = zope.schema.TextLine(
        title=_("Title attribute"),
        description=_(
            u"The LDAP attribute used to determine a principal's title."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'cn',
        required=True,
        )

    groupIdAttribute = zope.schema.TextLine(
        title=_("Group Id attribute"),
        description=_(
        u"The LDAP attribute (on a group entry) used to determine the "
        "group's id."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'cn',
        required=False,
        )
    
    # searchObjectClasses
