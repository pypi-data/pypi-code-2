##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
$Id: testing.py 79795 2007-09-21 13:05:43Z srichter $
"""
__docformat__ = 'restructuredtext'

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import IChoice, IDate, IIterableVocabulary
from zope.app.form.interfaces import IInputWidget, IWidgetInputError
from zope.app.form.browser import DateWidget, ChoiceInputWidget
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.app.form.browser.exception import WidgetInputErrorView
from zope.app.testing import setup, ztapi

from z3c.widget.dateselect.browser import DropdownWidget

def setUp(test):
    setup.placefulSetUp()
    ztapi.browserViewProviding(IChoice, ChoiceInputWidget, IInputWidget)
    ztapi.browserViewProviding(IDate, DateWidget, IInputWidget)
    ztapi.provideMultiView((IChoice, IIterableVocabulary), IBrowserRequest,
                           IInputWidget, '', DropdownWidget)
    # errors in forms
    ztapi.browserViewProviding(IWidgetInputError, WidgetInputErrorView,
                               IWidgetInputErrorView)


def tearDown(test):
    setup.placefulTearDown()
