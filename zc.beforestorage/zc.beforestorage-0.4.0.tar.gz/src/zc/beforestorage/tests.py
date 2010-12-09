##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import time, unittest
import doctest
import zope.testing.setupstack
import zc.beforestorage


def setUp(test):
    zope.testing.setupstack.setUpDirectory(test)
    now = [time.mktime((2008, 1, 21, 13, 22, 42, 0, 0, 0))]
    def timetime():
        now[0] += 1
        return now[0]

    old_timetime = time.time
    zope.testing.setupstack.register(
        test,
        lambda : setattr(time, 'time', old_timetime)
        )
    time.time = timetime
    zc.beforestorage.startup_time_stamp = zc.beforestorage.time_stamp()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

