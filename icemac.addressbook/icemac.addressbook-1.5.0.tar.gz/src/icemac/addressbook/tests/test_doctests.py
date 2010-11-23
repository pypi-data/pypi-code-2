# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1183 2010-11-23 17:17:09Z icemac $

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        # Caution: none of these tests can run as unittest!
        'adapter.txt',
        'address.txt',
        'addressbook.txt',
        'catalog.txt',
        'person.txt',
        'testing.txt',
        )
