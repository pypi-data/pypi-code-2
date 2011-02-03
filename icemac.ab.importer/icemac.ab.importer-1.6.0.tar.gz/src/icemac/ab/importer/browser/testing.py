# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: testing.py 1230 2011-01-29 17:10:18Z icemac $

import zope.app.wsgi.testlayer
import icemac.ab.importer.browser

ImporterLayer = zope.app.wsgi.testlayer.BrowserLayer(
    icemac.ab.importer.browser)
