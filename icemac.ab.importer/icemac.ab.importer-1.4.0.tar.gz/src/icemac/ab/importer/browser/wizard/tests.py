# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 781 2010-01-09 14:24:30Z icemac $

import icemac.addressbook.testing
import icemac.ab.importer.browser.testing

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        "constraints.txt",
        "edgecases.txt",
        "keywords.txt",
        "multientries.txt",
        "wizard.txt",
        "userfields.txt",
        package='icemac.ab.importer.browser.wizard',
        layer=icemac.ab.importer.browser.testing.ImporterLayer,
        )
