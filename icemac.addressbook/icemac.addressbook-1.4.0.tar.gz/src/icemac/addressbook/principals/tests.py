# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 783 2010-01-09 14:28:06Z icemac $

import gocept.reference.verify
import icemac.addressbook.principals.interfaces
import icemac.addressbook.principals.principals
import icemac.addressbook.testing
import unittest
import zope.interface.verify


class TestInterfaces(unittest.TestCase):

    def test_principal(self):
        principal = icemac.addressbook.principals.principals.Principal()
        # need to call created event handler here, because person
        # attribute is a descriptor wrapping the one verifyObject
        # expects.
        icemac.addressbook.principals.principals.created(principal, None)
        gocept.reference.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IPrincipal, principal)
        zope.interface.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IPasswordFields, principal)
        zope.interface.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IRoles, principal)


def test_suite():
    return icemac.addressbook.testing.AddressBookUnittestSuite(TestInterfaces)

