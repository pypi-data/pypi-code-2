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
"""LDAP PAS Authentication plugin

$Id: authentication.py 118669 2010-12-02 15:42:48Z faassen $
"""
import zope.schema
import zope.interface
from persistent import Persistent
from zope import component

from zope import pluggableauth
from zope.container.contained import Contained

from ldap.filter import filter_format
from ldapadapter.interfaces import ServerDown
from ldapadapter.interfaces import InvalidCredentials
from ldapadapter.interfaces import NoSuchObject
from ldapadapter.interfaces import ILDAPAdapter
from ldappas.interfaces import ILDAPAuthentication


class ILDAPSearchSchema(zope.interface.Interface):
    """A LDAP-specific schema for searching for principals."""

    uid = zope.schema.TextLine(
        title=u'uid',
        required=False)

    cn = zope.schema.TextLine(
        title=u'cn',
        required=False)

    givenName = zope.schema.TextLine(
        title=u'givenName',
        required=False)

    sn = zope.schema.TextLine(
        title=u'sn',
        required=False)


class PrincipalInfo:
    """An implementation of IPrincipalInfo used by the principal folder."""
    zope.interface.implements(pluggableauth.interfaces.IPrincipalInfo)

    def __init__(self, id, login='', title='', description=''):
        self.id = id
        self.login = login
        self.title = title
        self.description = description

    def __repr__(self):
        return 'PrincipalInfo(%r)' % self.id


class LDAPAuthentication(Persistent, Contained):
    """A Persistent LDAP Authentication plugin for PAS.

    An authentication plugin is configured using an LDAP Adapter that
    will be use to check user credentials that encapsulates server
    information, and additional authentication-specific informations.
    """

    zope.interface.implements(
        ILDAPAuthentication,
        pluggableauth.interfaces.IAuthenticatorPlugin,
        pluggableauth.interfaces.IQueriableAuthenticator,
        pluggableauth.interfaces.IQuerySchemaSearch)

    adapterName = ''
    searchBase = ''
    searchScope = ''
    groupsSearchBase = ''
    groupsSearchScope = ''
    loginAttribute = ''
    principalIdPrefix = ''
    idAttribute = ''
    titleAttribute = ''
    groupIdAttribute = ''
    
    schema = ILDAPSearchSchema

    def getLDAPAdapter(self):
        """Get the LDAP adapter according to our configuration.

        Returns None if adapter connection is configured or available.
        """
        da = component.queryUtility(ILDAPAdapter, name=self.adapterName)
        return da

    def authenticateCredentials(self, credentials):
        """See zope.pluggableauth.interfaces.IAuthenticatorPlugin."""

        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None

        da = self.getLDAPAdapter()
        if da is None:
            return None

        login = credentials['login']
        password = credentials['password']

        # Search for a matching entry.
        try:
            conn = da.connect()
        except ServerDown:
            return None
        filter = filter_format('(%s=%s)', (self.loginAttribute, login))
        try:
            res = conn.search(self.searchBase, self.searchScope, filter=filter)
        except NoSuchObject:
            return None
        if len(res) != 1:
            # Search returned no result or too many.
            return None
        dn, entry = res[0]

        # Find the id we'll return.
        id_attr = self.idAttribute
        if id_attr == 'dn':
            id = dn
        elif entry.get(id_attr):
            id = entry[id_attr][0]
        else:
            return None
        id = self.principalIdPrefix + id

        # Check authentication.
        try:
            conn = da.connect(dn, password)
        except (ServerDown, InvalidCredentials):
            return None

        return PrincipalInfo(id, **self.getInfoFromEntry(dn, entry))

    def principalInfo(self, id):
        """See zope.pluggableauth.interfaces.IAuthenticatorPlugin."""
        if not id.startswith(self.principalIdPrefix):   
            return None
        internal_id = id[len(self.principalIdPrefix):]
           
        da = self.getLDAPAdapter()
        if da is None:
            return None

        # Search for a matching entry.
        try:
            conn = da.connect()
        except ServerDown:
            return None
        filter = filter_format('(%s=%s)', (self.idAttribute, internal_id))
        try:
            res = conn.search(self.searchBase, self.searchScope, filter=filter)
        except NoSuchObject:
            res = []
        if len(res) != 1:
            # Search returned no result or too many.
            return self._groupPrincipalInfo(conn, id, internal_id)
        dn, entry = res[0]

        return PrincipalInfo(id, **self.getInfoFromEntry(dn, entry))

    def _groupPrincipalInfo(self, conn, id, internal_id):
        """Return PrincipalInfo for a group, if it exists.
        """
        if (not self.groupsSearchBase or
            not self.groupsSearchScope or
            not self.groupIdAttribute):
            return None
        filter = filter_format('(%s=%s)', (self.groupIdAttribute, internal_id))
        try:
            res = conn.search(self.groupsSearchBase, self.groupsSearchScope,
                              filter=filter)
        except NoSuchObject:
            return None
        if len(res) != 1:
            return None
        dn, entry = res[0]
        return PrincipalInfo(id)
    
    def getInfoFromEntry(self, dn, entry):
        try:
            title = entry[self.titleAttribute][0]
        except (KeyError, IndexError):
            title = dn
        return {'login': entry[self.loginAttribute][0],
                'title': title,
                'description': title,
                }

    def search(self, query, start=None, batch_size=None):
        """See zope.pluggableauth.interfaces.IQuerySchemaSearch."""
        da = self.getLDAPAdapter()
        if da is None:
            return ()
        try:
            conn = da.connect()
        except ServerDown:
            return ()

        # Build the filter based on the query
        filter_elems = []
        for key, value in query.items():
            if not value:
                continue
            filter_elems.append(filter_format('(%s=*%s*)',
                                              (key, value)))
        filter = ''.join(filter_elems)
        if len(filter_elems) > 1:
            filter = '(&%s)' % filter

        if not filter:
            filter = '(objectClass=*)'

        try:
            res = conn.search(self.searchBase, self.searchScope, filter=filter,
                              attrs=[self.idAttribute])
        except NoSuchObject:
            return ()

        prefix = self.principalIdPrefix
        infos = []
        for dn, entry in res:
            try:
                infos.append(prefix+entry[self.idAttribute][0])
            except (KeyError, IndexError):
                pass

        if start is None:
            start = 0
        if batch_size is not None:
            return infos[start:start+batch_size]
        else:
            return infos[start:]
