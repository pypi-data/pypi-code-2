##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: testing.py 77310 2007-07-02 18:14:46Z srichter $
"""
__docformat__ = "reStructuredText"

import os
from zope.app.testing.functional import ZCMLLayer


TestLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=True)
