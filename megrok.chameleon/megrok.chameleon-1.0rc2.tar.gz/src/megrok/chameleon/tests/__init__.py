##############################################################################
#
# Copyright (c) 2006-2010 Zope Foundation and Contributors.
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
# $Id: __init__.py 112570 2010-05-20 13:18:56Z ulif $ $Rev$ $Author$ $Date$
"""A functional test layer.
"""
import megrok.chameleon
from zope.app.wsgi.testlayer import BrowserLayer

FunctionalLayer = BrowserLayer(megrok.chameleon, 'ftesting.zcml')
