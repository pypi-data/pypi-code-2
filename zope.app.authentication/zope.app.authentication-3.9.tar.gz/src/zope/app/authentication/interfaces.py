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

$Id: interfaces.py 117633 2010-10-18 09:40:31Z janwijbrand $
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
    AuthenticatedPrincipalCreated,
    FoundPrincipalCreated,
    IAuthenticatedPrincipalCreated,
    IAuthenticatedPrincipalFactory,
    IAuthenticatorPlugin,
    ICredentialsPlugin,
    IFoundPrincipalCreated,
    IFoundPrincipalFactory,
    IGroupAdded,
    IPluggableAuthentication,
    IPlugin,
    IPrincipal,
    IPrincipalCreated,
    IPrincipalFactory,
    IPrincipalInfo,
    IPrincipalsAddedToGroup,
    IPrincipalsRemovedFromGroup,
    IQueriableAuthenticator,
    IQuerySchemaSearch,
    )

# BBB: using zope.pluggableauth
from zope.pluggableauth.plugins.groupfolder import (
    GroupAdded,
    )
