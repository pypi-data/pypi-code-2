# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: testing.py 781 2010-01-09 14:24:30Z icemac $

import zope.app.testing.functional


zope.app.testing.functional.defineLayer(
    'ImporterLayer', 'ftesting.zcml', allow_teardown=True)
