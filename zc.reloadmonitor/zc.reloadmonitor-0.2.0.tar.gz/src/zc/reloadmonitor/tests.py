
##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
from zope.testing import setupstack
import doctest, os, unittest, StringIO, sys
import zc.monitor, zc.ngi.testing, zc.reloadmonitor
import zope.component.testing, zope.configuration.xmlconfig

def basic():
    r"""

The reload plugin is very simple:

    >>> conn = StringIO.StringIO()
    >>> zc.reloadmonitor.reloadmonitor(conn, 'reloadmonitorexample')
    Traceback (most recent call last):
    ...
    KeyError: 'reloadmonitorexample'

    >>> conn.getvalue()
    ''

Here, the reload failed because reloadmonitorexample hadn't been imported.

    >>> import reloadmonitorexample
    importing reloadmonitorexample

    >>> zc.reloadmonitor.reloadmonitor(conn, 'reloadmonitorexample')
    importing reloadmonitorexample


    >>> conn.getvalue()
    'done\n'

    """

def pyintegration():
    r"""
    >>> zc.reloadmonitor.configure()
    >>> import reloadmonitorexample
    importing reloadmonitorexample

    >>> conn = zc.ngi.testing.Connection()
    >>> server = zc.monitor.Server(conn)
    >>> conn.peer.write('reload reloadmonitorexample\n')
    importing reloadmonitorexample
    -> 'done'
    -> '\n'
    -> CLOSE
    """

def zcmkintegration():
    r"""
    >>> _ = zope.configuration.xmlconfig.string(
    ...   '<include package="zc.reloadmonitor" />')

    >>> import reloadmonitorexample
    importing reloadmonitorexample

    >>> conn = zc.ngi.testing.Connection()
    >>> server = zc.monitor.Server(conn)
    >>> conn.peer.write('reload reloadmonitorexample\n')
    importing reloadmonitorexample
    -> 'done'
    -> '\n'
    -> CLOSE
    """

def setUp(test):
    setupstack.setUpDirectory(test)
    here = os.getcwd()
    sys.path.append(here)
    open('reloadmonitorexample.py', 'w').write(
        'print "importing reloadmonitorexample"\n')
    setupstack.register(test, sys.path.remove, here)
    sys.modules.pop('reloadmonitorexample', None)
    setupstack.register(test, sys.modules.pop, 'reloadmonitorexample', None)
    zope.component.testing.setUp()
    setupstack.register(test, zope.component.testing.tearDown)

def test_suite():
    return doctest.DocTestSuite(setUp=setUp, tearDown=setupstack.tearDown)
