##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

from zope.pluggableauth.interfaces import (
    IAuthenticatorPlugin, IQuerySchemaSearch
    )
from zope.pluggableauth.factories import PrincipalInfo
from zope.pluggableauth.plugins.principalfolder import (
    PrincipalFolder, InternalPrincipal, ISearchSchema,
    )
from zope.container.interfaces import DuplicateIDError
from zope.principalregistry.principalregistry import principalRegistry
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.interface import implements

class PrincipalRegistryAuthenticator(object):
    """An authenticator plugin, that authenticates principals against
    the global principal registry.

    This authenticator does not support own prefixes, because the
    prefix of its principals is already defined in another place
    (site.zcml). Therefore we get and give back IDs as they are.
    """

    implements(IAuthenticatorPlugin, IQuerySchemaSearch)

    schema = ISearchSchema

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        principal = None
        login, password = credentials['login'], credentials['password']
        try:
            principal = principalRegistry.getPrincipalByLogin(login)
        except KeyError:
            return
        if principal and principal.validate(password):
            return PrincipalInfo(u''+principal.id,
                                 principal.getLogin(),
                                 principal.title,
                                 principal.description)
        return

    def principalInfo(self, id):
        principal = principalRegistry.getPrincipal(id)
        if principal is not None:
            return PrincipalInfo(u''+principal.id,
                                 principal.getLogin(),
                                 principal.title,
                                 principal.description)


    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider.
        """
        search = query.get('search')
        if search is None:
            return
        search = search.lower()
        n = 1
        values = [x for x in principalRegistry.getPrincipals('')
                  if x is not None]
        values.sort(cmp=lambda x,y: cmp(str(x.id), str(y.id)))
        for i, value in enumerate(values):
            if (search in value.id.lower() or
                search in value.title.lower() or
                search in value.description.lower() or
                search in value.getLogin().lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield u''+value.__name__


class AutoRegisteringPrincipalFolder(PrincipalFolder):
    """A principalfolder, that autoregisters new principals.
    """
    def __init__(self, prefix='', autopermissions=()):
        super(AutoRegisteringPrincipalFolder, self).__init__(prefix)
        self.__id_by_login = self._newContainerData()
        self.auto_permissions = autopermissions
 
    def authenticateCredentials(self, credentials):
        """An authentication that adds the credentials if possible.
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        id = self.__id_by_login.get(credentials['login'])
        if id is None:
            # Create new principal...
            id = credentials['login']
            principal = InternalPrincipal(id, credentials['password'], id)
            try:
                self[id] = principal
                perm_mgr = IPrincipalPermissionManager(
                    self.__parent__.__parent__.__parent__)
                for perm in self.auto_permissions:
                    perm_mgr.grantPermissionToPrincipal(
                        perm, self.prefix + id)
            except DuplicateIDError:
                pass
            except KeyError:
                pass
        internal = self[id]
        if not internal.checkPassword(credentials["password"]):
            return None
        return PrincipalInfo(self.prefix + id, internal.login, internal.title,
                             internal.description)

