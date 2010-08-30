##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
$Id: tests.py 116038 2010-08-30 19:10:45Z srichter $
"""
__docformat__ = "reStructuredText"
import logging
import os
import unittest
import doctest

class TestingHandler(logging.Handler):

    def emit(self, record):
        print record.msg

handler = TestingHandler()

def do_cmd(cmd):
    os.system(cmd)

def setUp(test):
    logging.getLogger().addHandler(handler)

def tearDown(test):
    logging.getLogger().removeHandler(handler)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            globs={'cmd': do_cmd},
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
