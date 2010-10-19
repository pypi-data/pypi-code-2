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

import re
import unittest
import doctest
from zope.testing import renormalizing

import zc.buildout.testing


def test_start_error():
    """The start script will setup a egg based start hook for a Zope 3 setup.
    Let's create a buildout that installs it as an ordinary script:

    >>> write('buildout.cfg',
    ... '''
    ... [winservice]
    ... recipe = z3c.recipe.winservice:service
    ... eggs = z3c.recipe.winservice
    ... ''')

    >>> print system(join('bin', 'buildout')),

    """


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.winservice', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('ZConfig', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile("""['"][^\n"']+z3c.recipe.dev[^\n"']*['"],"""),
     "'/z3c.recipe.dev',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    ])


def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=(
                doctest.NORMALIZE_WHITESPACE|
                doctest.ELLIPSIS),
            checker=checker),
        )


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
