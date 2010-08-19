# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 860 2010-03-06 14:51:28Z icemac $

import icemac.addressbook.testing

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'adapter.txt', # Caution: none of these tests can run as unittest!
        'address.txt',
        'addressbook.txt',
        'catalog.txt',
        'person.txt',
        )
