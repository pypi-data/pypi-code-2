# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#
"""
Configuration framework for the web application.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['Configuration', 'Section', 'Option',
           'AbsolutePath', 'AbsoluteURLPath', 'AsciiString', 'Boolean', 'Filename', 'GenshiOutputType', 'IdentityBackend', 'LDAPSearchScope', 'LDAPURL', 'List', 'OpenIDStore',
           'GeneralSection', 'IdentitySection', 'LDAPSection', 'AuthenticityConfiguration']

import os
import re
import sys
import urlparse
from ConfigParser import Error as ConfigParserError, RawConfigParser
from itertools import chain
from string import Template
from weakref import WeakKeyDictionary

import ldap
from ldapurl import LDAPUrl


# Core configuration classes
#

class Option(object):
    """
    The Option class is a descriptor used in Sections to represent options. The
    type must be a callable which will receive a unicode string as input and
    return an object. The type will be called whenever the option is set with a
    non-False value; a False value will be converted to None.
    """
    def __init__(self, type, default=None, nillable=True):
        if default is None and not nillable:
            raise ValueError('An option cannot be nillable and have None as default in the same time')
        self.type = type
        self.default = default
        self.nillable = nillable
        self.values = WeakKeyDictionary()

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return self.values.get(obj, self.default)

    def __set__(self, obj, value):
        value = self.type(value) if value else None
        if value is None and not self.nillable:
            raise ValueError('Option is not nillable')
        self.values[obj] = value


class SectionType(type):
    """
    Metaclass for Section. Section subclasses (instances of this class) act as
    descriptors in Configuration subclasses.
    """
    def __init__(cls, name, bases, dct):
        if cls.__section__ is None and any(isinstance(base, SectionType) for base in bases):
            raise TypeError('The __section__ attribute must be defined in %s' % cls.__name__)
        own_options = set(attr for attr, value in dct.iteritems() if isinstance(value, Option))
        inherited_options = set(chain(*(base.__options__ for base in bases if isinstance(base, SectionType))))
        cls.__options__ = list(own_options.union(inherited_options))
        cls.values = WeakKeyDictionary()

    def __get__(cls, obj, objtype):
        if obj is None:
            return cls
        try:
            return cls.values[obj]
        except KeyError:
            return cls.values.setdefault(obj, cls())

    def __set__(cls, obj, value):
        raise TypeError('A section cannot be overwritten')


class Section(object):
    """
    A Section groups Options which are read from the configuration section
    named __section__.
    """
    __metaclass__ = SectionType

    __section__ = None


class ConfigurationType(type):
    """
    Metaclass for Configuration.
    """
    def __init__(cls, name, bases, dct):
        own_sections = set(attr for attr, value in dct.iteritems() if isinstance(value, SectionType))
        inherited_sections = set(chain(*(base.__sections__ for base in bases if isinstance(base, ConfigurationType))))
        cls.__sections__ = list(own_sections.union(inherited_sections))


class Configuration(object):
    """
    Top-level object for configurations, which groups Sections. Instances
    can be created by using the read classmethod.
    """
    __metaclass__ = ConfigurationType

    def __new__(cls):
        raise TypeError('%s cannot be instantiated directly' % cls.__name__)

    @classmethod
    def read(cls, file, options, logger):
        """
        Create a new Configuration instance using the values from the INI file
        (which must be a file-like object supporting readline) and the
        mapping options (containing a mapping between keys of the form
        section.name and a value or list of values (this is usually the
        mod_python mp_table structure returned by request.get_options()).
        """
        instance = object.__new__(cls)
        apache_options = {}
        if options is not None:
            for key, value in options.iteritems():
                namespace, sep, key = key.partition('.')
                if sep != '.' or namespace != 'authenticity':
                    continue
                section, sep, option = key.partition('.')
                if sep != '.':
                    logger.warn('Illegal option name (expected section.option): %s.' % key)
                    continue
                if isinstance(value, list):
                    value = value[0]
                apache_options.setdefault(section, {})[option] = value
        parser = RawConfigParser()
        if file is not None:
            try:
                parser.readfp(file)
            except ConfigParserError, e:
                logger.warn('Failed to read configuration file: %s.' % e)
        for name in cls.__sections__:
            section = getattr(instance, name)
            if parser.has_section(section.__section__):
                for (option, value) in parser.items(section.__section__):
                    option = option.replace('-', '_')
                    if option in section.__options__:
                        try:
                            setattr(section, option, value.decode('utf-8'))
                        except ValueError, e:
                            logger.warn('Illegal value for option %s in section %s: %s.' % (option, section.__section__, e))
            if section.__section__ in apache_options:
                for (option, value) in apache_options[section.__section__].iteritems():
                    option = option.replace('-', '_')
                    if option in section.__options__:
                        try:
                            setattr(section, option, value.decode('utf-8'))
                        except ValueError, e:
                            logger.warn('Illegal value for option %s in section %s: %s.' % (option, section.__section__, e))
        return instance

    @classmethod
    def register_section(cls, attribute, section):
        """
        Register a new section under the specified attribute.
        """
        if not isinstance(section, SectionType):
            raise TypeError('Expected Section subclass')
        if hasattr(cls, attribute):
            raise ValueError('The attribute %s is already in use' % attribute)
        setattr(cls, attribute, section)
        cls.__sections__.append(attribute)


# Datatypes
#

class AbsolutePath(unicode):
    """
    A datatype which only accepts absolute filesystem paths.
    """
    def __new__(cls, value):
        value = os.path.normpath(value)
        if not os.path.isabs(value):
            raise ValueError('Expected absolute path')
        return value


class AbsoluteURLPath(unicode):
    """
    A datatype which only accepts absolute URL paths (i.e. which start with /).
    """
    def __new__(cls, value):
        if not value.startswith('/'):
            raise ValueError('Expected absolute path')
        return value


class AsciiString(unicode):
    """
    A datatype which only accepts ASCII strings.
    """
    def __new__(cls, value):
        try:
            value.encode('ascii')
        except UnicodeError:
            raise ValueError('Expected ASCII string')
        else:
            return value


class Boolean(int):
    """
    A datatype which accepts strings of the form 'true'/'false', 'yes'/'no',
    'on'/'off', '1'/'0' and returns a Boolean.
    """
    def __new__(cls, value):
        value = value.lower()
        if value in ('true', 'yes', 'on', '1'):
            return True
        elif value in ('false', 'no', 'off', '0'):
            return False
        else:
            raise ValueError('Illegal boolean value')


class Filename(unicode):
    """
    A datatype which accepts single path components (i.e. which do not contain
    the directory separator (/ or \\) and are not the special filenames which
    denote the current and parent directory (. and ..)).
    """
    def __new__(cls, value):
        is_special_dir = value in (os.path.curdir, os.path.pardir)
        is_separator = os.path.sep in value or (os.path.altsep and os.path.altsep in value)
        if is_special_dir or is_separator:
            raise ValueError('Illegal filename')
        return value


class GenshiOutputType(unicode):
    """
    An output type for the genshi template system. One of xml, xhtml, html or
    text.
    """
    def __new__(cls, value):
        if value not in ('xml', 'xhtml', 'html', 'text'):
            raise ValueError('Illegal output type')
        return value


class IdentityBackend(unicode):
    """
    An identity service backend name. Currently only ldap is supported.
    """
    def __new__(cls, value):
        if value != 'ldap':
            raise ValueError('Illegal identity backend')
        return value


class LDAPSearchScope(int):
    """
    A LDAP search scope. One of base, one or sub.
    """
    def __new__(cls, value):
        try:
            return dict(base=ldap.SCOPE_BASE, one=ldap.SCOPE_ONELEVEL, sub=ldap.SCOPE_SUBTREE)[value]
        except KeyError:
            raise ValueError('Illegal LDAP search scope')


class LDAPURL(unicode):
    """
    A LDAP URL. Must have a scheme of ldap, ldaps or ldapi.
    """
    def __new__(cls, value):
        try:
            LDAPUrl(value)
        except ValueError:
            raise ValueError('Illegal LDAP URL')
        else:
            return value


def List(type=unicode):
    """
    Returns a class which parses a comma separated list of values and applies
    type on each of them. Whitespace around the commas is ignored.
    """
    class List(list):
        list_re = re.compile(r'\s*,\s*')
        def __new__(cls, value):
            return [type(s) for s in cls.list_re.split(value)]
    return List


class OpenIDStore(tuple):
    """
    Returns a parsed URL identifying an OpenID store. The currently supported
    schemes are file and sqlite.
    """
    def __new__(cls, value):
        dbinfo = urlparse.urlsplit(value)
        if dbinfo.scheme not in ('file', 'sqlite'):
            raise ValueError('Only file and sqlite stores are currently supported')
        required_fields = [dbinfo.path]
        illegal_fields = [dbinfo.netloc, dbinfo.query, dbinfo.fragment]
        if dbinfo.scheme in ('file', 'sqlite') and (not all(required_fields) or any(illegal_fields)):
            raise ValueError('A %s URL must specify only a path' % dbinfo.scheme)
        return dbinfo


# Authenticity configuration
#

class GeneralSection(Section):
    __section__ = 'General'

    data_path           = Option(type=AbsolutePath, default=os.path.join(sys.prefix, 'share/authenticity'), nillable=False)
    server_path         = Option(type=AbsoluteURLPath, default='/', nillable=False)
    realm_name          = Option(type=Template, default=Template('$server_host'), nillable=False)
    page_title          = Option(type=Template, default=Template('Authenticity OpenID Server'), nillable=False)
    openid_store        = Option(type=OpenIDStore, default=OpenIDStore('file:///var/lib/authenticity/stores/'), nillable=False)
    templates_directory = Option(type=unicode, default='templates/', nillable=False)
    template            = Option(type=Filename, default='default', nillable=False)


class IdentitySection(Section):
    __section__ = 'Identity'

    backend             = Option(type=IdentityBackend, default='ldap', nillable=False)
    identifier_formats  = Option(type=List(Template), default=[Template('$server_base/id/$username')], nillable=False)
    forced_local_id     = Option(type=Template, default=Template('$server_base/id/$username'), nillable=True)


class LDAPSection(Section):
    __section__ = 'LDAP'

    server_url          = Option(type=LDAPURL, default='ldap://127.0.0.1', nillable=False)
    bind_dn             = Option(type=unicode, default=None, nillable=True)
    bind_password       = Option(type=unicode, default=None, nillable=True)
    search_format       = Option(type=Template, default=None, nillable=True)
    search_base         = Option(type=unicode, default=None, nillable=True)
    search_scope        = Option(type=LDAPSearchScope, default=LDAPSearchScope('sub'), nillable=True)
    search_filter       = Option(type=Template, default=Template('(uid=$username)'), nillable=True)
    search_timeout      = Option(type=int, default=3, nillable=False)
    nickname_attribute  = Option(type=AsciiString, default='uid', nillable=True)
    email_attribute     = Option(type=AsciiString, default='mail', nillable=True)
    fullname_attribute  = Option(type=AsciiString, default='cn', nillable=True)
    birthday_attribute  = Option(type=AsciiString, default=None, nillable=True)
    birthday_format     = Option(type=unicode, default='%Y-%m-%d', nillable=False)
    gender_attribute    = Option(type=AsciiString, default=None, nillable=True)
    male_gender         = Option(type=unicode, default='M', nillable=False)
    female_gender       = Option(type=unicode, default='F', nillable=False)
    postcode_attribute  = Option(type=AsciiString, default='postalCode', nillable=True)
    country_attribute   = Option(type=AsciiString, default='c', nillable=True)
    language_attribute  = Option(type=AsciiString, default=None, nillable=True)
    timezone_attribute  = Option(type=AsciiString, default=None, nillable=True)


class AuthenticityConfiguration(Configuration):
    general     = GeneralSection
    ldap        = LDAPSection
    identity    = IdentitySection


