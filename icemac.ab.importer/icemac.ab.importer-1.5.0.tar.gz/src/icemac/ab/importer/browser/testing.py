# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: testing.py 1045 2010-08-25 05:58:29Z icemac $

import zope.app.wsgi.testlayer
import icemac.ab.importer.browser

ImporterLayer = zope.app.wsgi.testlayer.BrowserLayer(
    icemac.ab.importer.browser)
