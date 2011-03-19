# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
HTTP request handler. This is where the main magic happens.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['AuthenticationError', 'IdentityLookupError', 'IdentityServiceError',
           'IIdentityService', 'Identity', 'LDAPIdentityService']

from datetime import datetime

import ldap
import ldap.dn
from ldap import LDAPError
from zope.interface import Interface, implements


class IdentityServiceError(Exception):
    """
    Generic class for identity service exceptions. All exceptions raised by this
    module derive from this class.
    """


class AuthenticationError(IdentityServiceError):
    """
    This is the exception raised by IIdentityService.authenticate if wrong
    credentials are given.
    """


class IdentityLookupError(IdentityServiceError):
    """
    This exception is raised when a looked up identity does not exist.
    """


class Identity(object):
    """
    Instances of this class represent identities. They store various
    information, but never passwords or similar information.
    """

    def __init__(self,
                 username,
                 nickname=None,
                 email=None,
                 fullname=None,
                 birthday=None,
                 gender=None,
                 postcode=None,
                 country=None,
                 language=None,
                 timezone=None):
        """
        Initializes an Identity instance using the specified data.
        """
        self.username = username
        self.nickname = nickname
        self.email    = email
        self.fullname = fullname
        self.birthday = birthday
        self.gender   = gender
        self.postcode = postcode
        self.country  = country
        self.language = language
        self.timezone = timezone

    @property
    def name(self):
        """
        Return the most appropriate name for this identity. Returns one of
        fullname, nickname or username, whichever is available (in this order).
        """
        return self.fullname or self.nickname or self.username


class IIdentityService(Interface):
    """
    This interface describes the methods available on an identity service.
    """

    def __init__(configuration, logger):
        """
        Initializes the identity service using the global configuration instance
        and the logger.
        """

    def authenticate(username, password):
        """
        Tries to authenticate the given user using a password. Raises an error
        if not successful. If the user does not exist or the credentials are
        wrong, an AuthenticationError is raised.
        """

    def lookup(username):
        """
        Looks up an identity using the specified username. Returns an Identity
        instance if successful, otherwise it raises an error.
        IdentityLookupError is raised if exactly one identity cannot be found.
        """


class LDAPIdentityService(object):
    implements(IIdentityService)

    def __init__(self, configuration, logger):
        self.configuration = configuration
        self.logger = logger
        self.attributes = dict(nickname = self.configuration.ldap.nickname_attribute,
                               email    = self.configuration.ldap.email_attribute,
                               fullname = self.configuration.ldap.fullname_attribute,
                               birthday = self.configuration.ldap.birthday_attribute,
                               gender   = self.configuration.ldap.gender_attribute,
                               postcode = self.configuration.ldap.postcode_attribute,
                               country  = self.configuration.ldap.country_attribute,
                               language = self.configuration.ldap.language_attribute,
                               timezone = self.configuration.ldap.timezone_attribute)
        self.attributes = dict((key, value.encode('ascii')) for key, value in self.attributes.iteritems() if value)

    def authenticate(self, username, password):
        try:
            connection = ldap.initialize(self.configuration.ldap.server_url)
        except LDAPError, e:
            raise IdentityServiceError(e.args[0]['desc'])
        if self.configuration.ldap.bind_dn and self.configuration.ldap.bind_password:
            try:
                bind_dn = self.configuration.ldap.bind_dn.encode('utf-8')
                bind_password = self.configuration.ldap.bind_password.encode('utf-8')
                connection.simple_bind_s(bind_dn, bind_password)
            except LDAPError, e:
                raise IdentityServiceError('Failed to bind for search: %s' % e.args[0]['desc'])
        elif any([self.configuration.ldap.bind_dn, self.configuration.ldap.bind_password]):
            self.logger.warn('Either both or none of bind_dn and bind_password options from LDAP section need to be specified.')
        if self.configuration.ldap.search_format:
            dn = self.configuration.ldap.search_format.safe_substitute(username=ldap.dn.escape_dn_chars(username)).encode('utf-8')
            fields = dict()
        elif None in (self.configuration.ldap.search_base, self.configuration.ldap.search_scope):
            raise IdentityServiceError('Either search_format or at least search_base and search_scope need to be specified')
        else:
            try:
                filter = self.configuration.ldap.search_filter
                filter = filter.safe_substitute(username=ldap.dn.escape_dn_chars(username)) if filter else '(objectClass=*)'
                results = connection.search_st(self.configuration.ldap.search_base.encode('utf-8'),
                                               self.configuration.ldap.search_scope,
                                               filter.encode('utf-8'),
                                               attrlist=self.attributes.values(),
                                               timeout=self.configuration.ldap.search_timeout)
                if not results or len(results) > 1:
                    raise AuthenticationError('Invalid credentials')
            except LDAPError, e:
                raise IdentityServiceError('Failed to search for identity: %s' % e.args[0]['desc'])
            else:
                dn, fields = results[0]
        try:
            connection.simple_bind_s(dn, password.encode('utf-8'))
        except ldap.INVALID_CREDENTIALS:
            raise AuthenticationError('Invalid credentials')
        except LDAPError, e:
            raise IdentityServiceError('Failed to bind for authentication: %s' % e.args[0]['desc'])
        try:
            results = connection.search_st(dn, ldap.SCOPE_BASE, attrlist=self.attributes.values(),
                                           timeout=self.configuration.ldap.search_timeout)
        except LDAPError:
            pass
        else:
            if len(results) == 1:
                fields.update(results[0][1])
        identity = Identity(username)
        self._populate_identity(identity, fields)
        connection.unbind_s()
        return identity

    def lookup(self, username):
        try:
            connection = ldap.initialize(self.configuration.ldap.server_url)
        except LDAPError, e:
            raise IdentityServiceError(e.args[0]['desc'])
        if self.configuration.ldap.bind_dn and self.configuration.ldap.bind_password:
            try:
                bind_dn = self.configuration.ldap.bind_dn.encode('utf-8')
                bind_password = self.configuration.ldap.bind_password.encode('utf-8')
                connection.simple_bind_s(bind_dn, bind_password)
            except LDAPError, e:
                raise IdentityServiceError('Failed to bind for search: %s' % e.args[0]['desc'])
        elif any([self.configuration.ldap.bind_dn, self.configuration.ldap.bind_password]):
            self.logger.warn('Either both or none of bind_dn and bind_password options from LDAP section need to be specified.')
        if self.configuration.ldap.search_format:
            base = self.configuration.ldap.search_format.safe_substitute(username=ldap.dn.escape_dn_chars(username))
            scope = ldap.SCOPE_BASE
            filter = '(objectClass=*)'
        elif None in (self.configuration.ldap.search_base, self.configuration.ldap.search_scope):
            raise IdentityServiceError('Either search_format or at least search_base and search_scope need to be specified')
        else:
            base = self.configuration.ldap.search_base
            scope = self.configuration.ldap.search_scope
            filter = self.configuration.ldap.search_filter
            filter = filter.safe_substitute(username=ldap.dn.escape_dn_chars(username)) if filter else '(objectClass=*)'
        try:
            results = connection.search_st(base.encode('utf-8'),
                                           scope,
                                           filter.encode('utf-8'),
                                           attrlist=self.attributes.values(),
                                           timeout=self.configuration.ldap.search_timeout)
            if not results or len(results) > 1:
                raise IdentityLookupError('Invalid identity')
        except ldap.NO_SUCH_OBJECT:
            raise IdentityLookupError('Invalid identity')
        except LDAPError, e:
            raise IdentityServiceError('Failed to search for identity: %s' % e.args[0]['desc'])
        else:
            dn, fields = results[0]
        identity = Identity(username)
        self._populate_identity(identity, fields)
        connection.unbind_s()
        return identity

    def _populate_identity(self, identity, fields):
        for name, ldap_name in self.attributes.iteritems():
            try:
                value = fields[ldap_name][0]
            except (KeyError, IndexError):
                continue
            if name == 'birthday':
                try:
                    value = datetime.strptime(value, self.configuration.ldap.birthday_format).date()
                except ValueError:
                    self.logger.warn('Invalid birthday/format: %s/%s.' % (value, self.configuration.ldap.birthday_format))
                    continue
            elif name == 'gender':
                if value == self.configuration.ldap.male_gender:
                    value = 'M'
                elif value == self.configuration.ldap.female_gender:
                    value = 'F'
                else:
                    self.logger.warn('Invalid gender: %s; expected `%s\' or `%s\'.' % \
                                     (value, self.configuration.ldap.male_gender, self.configuration.ldap.female_gender))
                    continue
            else:
                value = value.decode('utf-8')
            setattr(identity, name, value)


