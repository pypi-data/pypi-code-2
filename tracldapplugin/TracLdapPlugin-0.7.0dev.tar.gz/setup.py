#!/usr/bin/env python

from setuptools import setup, find_packages

setup (
    name = 'TracLdapPlugin',
    version = '0.7.0',
    description = 'LDAP extensions for Trac 0.12',
    author = 'Stefan Richter, Emmanuel Blot',
    author_email = 'stefan@02strich.de',
    license='BSD', 
    url='http://trac-hacks.org/wiki/LdapPlugin',
    keywords = "trac ldap permission group acl",
    install_requires = [ 'Trac>=0.12' ],
    packages = find_packages(exclude=['ez_setup', '*.tests*']),
    package_data = { },
    entry_points = {
        'trac.plugins': [
            'trac_ldap_plugin.api = trac_ldap_plugin.api',
        ]
    }
)
