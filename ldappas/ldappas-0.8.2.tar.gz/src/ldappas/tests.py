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
"""LDAP PAS Plugins tests

$Id: tests.py 118669 2010-12-02 15:42:48Z faassen $
"""
import unittest, doctest

import zope.interface

from zope.app.testing import setup
from pprint import pprint

import ldapadapter.interfaces

class FakeLDAPAdapter:
    zope.interface.implements(ldapadapter.interfaces.ILDAPAdapter)
    _isDown = False
    def connect(self, dn=None, password=None):
        if self._isDown:
            raise ldapadapter.interfaces.ServerDown
        if not dn and not password:
            return FakeLDAPConnection()
        if dn == 'uid=42,dc=test' and password == '42pw':
            return FakeLDAPConnection()
        raise ldapadapter.interfaces.InvalidCredentials

class FakeLDAPConnection:
    def search(self, base, scope='sub', filter='(objectClass=*)', attrs=[]):
        if not base:
            raise ValueError("No base supplied")
        if not scope:
            raise ValueError("No scope supplied")
        
        if base == 'ou=groups':
            return self._groupSearch(filter, attrs)
        dn1 = u'uid=1,dc=test'
        entry1 = {'cn': [u'many'],
                  'uid': [u'1'],
                  'sn': [u'mr1'],
                  }
        dn2 = u'uid=2,dc=test'
        entry2 = {'cn': [u'many'],
                  'uid': [u'2'],
                  'sn': [u'mr2'],
                  }
        dn42 = u'uid=42,dc=test'
        entry42 = {'cn': [u'ok'],
                   'uid': [u'42'],
                   'sn': [u'the question'],
                   'mult': [u'm1', u'm2'],
                   }
        if base.endswith('dc=bzzt'):
            raise ldapadapter.interfaces.NoSuchObject
        if filter == '(cn=none)':
            return []
        if filter in ('(cn=many)', '(cn=*many*)'):
            return [(dn1, entry1), (dn2, entry2)]
        if filter == '(cn=ok)' or filter == '(uid=42)':
            return [(dn42, entry42)]
        if filter in ('(&(sn=*mr2*)(cn=*many*))', '(&(cn=*many*)(sn=*mr2*))'):
            return [(dn2, entry2)]
        if filter == '(objectClass=*)':
            return [(dn1, entry1), (dn2, entry2), (dn42, entry42)]
        return []

    def _groupSearch(self, filter, attrs):
        if filter.startswith('(='):
            raise ValueError("Bad filter")
        if filter == '(cn=mygroup)':
            return [('uid=74,ou=group', {'cn': [u'mygroup']})]
        return []
        
def setUp(test):
    root = setup.placefulSetUp(site=True)
    sm = root.getSiteManager()
    setup.addUtility(sm, 'fake_ldap_adapter',
                     ldapadapter.interfaces.ILDAPAdapter, FakeLDAPAdapter())

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=tearDown,
                             globs={'pprint': pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
