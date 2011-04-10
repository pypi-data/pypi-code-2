# Copyright (c) 2007-2010 Thomas Lotze
# See also LICENSE.txt

"""Test suite for tl.buildout_apache.
"""

import re
import unittest

import zope.testing.doctest
import zope.testing.renormalizing
import zc.buildout.testing


flags = (zope.testing.doctest.NORMALIZE_WHITESPACE |
         zope.testing.doctest.ELLIPSIS |
         zope.testing.doctest.REPORT_NDIFF)


def setUp(test):
    import zc.recipe.cmmi
    import tl.buildout_apache
    import tl.buildout_virtual_python
    import zc.recipe.egg
    import virtualenv
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop("zc.recipe.cmmi", test)
    zc.buildout.testing.install_develop("tl.buildout_apache", test)
    zc.buildout.testing.install_develop("tl.buildout_virtual_python", test)
    zc.buildout.testing.install_develop("zc.recipe.egg", test)
    zc.buildout.testing.install_develop("virtualenv", test)


# XXX patch normalize_path to cope with --prefix=/sample-buildout/...
regex, _normalize_path = zc.buildout.testing.normalize_path
pattern = regex.pattern[:2] + '=' + regex.pattern[2:]
normalize_path = (re.compile(pattern), _normalize_path)


checker = zope.testing.renormalizing.RENormalizing([
    normalize_path,
    ])


def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(
        "httpd.txt",
        "modpython.txt",
        "root.txt",
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        package="tl.buildout_apache",
        optionflags=flags,
        checker=checker,
        ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
