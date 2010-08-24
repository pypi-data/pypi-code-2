# tranchitella.recipe.testrunner
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import doctest
import re
import unittest

import zc.buildout.testing

from zope.testing.renormalizing import RENormalizing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('tranchitella.recipe.testrunner', test)
    zc.buildout.testing.install('coverage', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.testrunner', test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.ELLIPSIS,
            checker=RENormalizing(
                    [zc.buildout.testing.normalize_path,
                     zc.buildout.testing.normalize_script,
                     zc.buildout.testing.normalize_egg_py,
                     (re.compile('#!\S+py\S*'), '#!python'),
                     (re.compile('\d[.]\d+ seconds'), '0.001 seconds'),
                     (re.compile('coverage-[^-]+-'), 'coverage-X-'),
                     (re.compile('setuptools-[^-]+-'), 'setuptools-X-'),
                     (re.compile('zc.buildout-[^-]+-'), 'zc.buildout-X-'),
                     (re.compile('zc.recipe.egg-[^-]+-'), 'zc.recipe.egg-X-'),
                     (re.compile('zope.exceptions-[^-]+-'), 'zope.exceptions-X-'),
                     (re.compile('zope.interface-[^-]+-'), 'zope.interface-X-'),
                     (re.compile('zope.recipe.egg-[^-]+-'), 'zope.recipe.egg-X-'),
                     (re.compile('zope.testrunner-[^-]+-'), 'zope.testrunner-X-'),
                     (re.compile("'.*/src'"), "'src'"),
                     ]),
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
