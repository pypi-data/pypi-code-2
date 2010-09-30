# -*- coding: utf-8 -*-
"""
Generic Test case for collective.releaser doctest
"""
__docformat__ = 'restructuredtext'

import shutil
import subprocess
import unittest
import doctest
import sys
import os
from os.path import join

from zope.testing import doctest
from zope.testing import renormalizing
from collective.releaser import testing

current_dir = os.path.dirname(__file__)
package_dir = os.path.join(current_dir, 'data', 'my.package')
backup_dir = package_dir + '_backup'

import zc.buildout.tests
import zc.buildout.testing
from zc.buildout.testing import *
from collective.releaser.testing import *

try:
    from subprocess import CalledProcessError
except ImportError:
    CalledProcessError = Exception

def cmd(cmd):
    if cmd == 'svn info':
        return ['Path: .', 'URL: http://xxx/my.package/trunk', '...']
    raise NotImplementedError

def check_cmd(cmd):
    for starter in ('svn ', 'python ', 'bin/buildout', 'bin\\buildout'):
        if cmd.startswith(starter):
            return True
    if 'bin/buildout' in cmd:
        return True
    raise CalledProcessError(cmd, 'ok')

def  _checkout_tag(*args, **kw):
    pass

from setuptools.sandbox import run_setup

def _get_version_txt(package_dir):
    my_package = os.path.split(package_dir)[-1]
    return join(*my_package.split('.') + ['version.txt'])

def setUp(test):
    save(current_dir)

    import collective.releaser.base
    import collective.releaser.packet
    collective.releaser.base.command = cmd
    collective.releaser.base.check_command = check_cmd
    collective.releaser.packet._checkout_tag = _checkout_tag
    collective.releaser.packet._run_setup = _checkout_tag
    import base
    import packet
    base.command = cmd
    base.check_command = check_cmd
    packet._checkout_tag = _checkout_tag
    packet._run_setup = _checkout_tag
    version_txt = _get_version_txt(package_dir)

    files = ('setup.py', 'CHANGES', version_txt)
    for file_ in files:
        target = join(package_dir, file_)
        if not os.path.exists(target):
            continue
        shutil.copyfile(target, target+'.old')
    testing.releaserSetUp(test)

    # setting up home to the current directory
    os.environ['HOME'] = os.path.dirname(__file__)

def tearDown(test):
    version_txt = _get_version_txt(package_dir)
    files = ('setup.py', 'CHANGES', version_txt)
    for file_ in files:
        target = join(package_dir, file_)
        source = target+'.old'
        if not os.path.exists(source):
            continue
        shutil.copyfile(source, target)
        os.remove(source)
    testing.releaserTearDown(test)
    purge(current_dir)

def doc_suite(test_dir, setUp=setUp, tearDown=tearDown, globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    doctest_dir = os.path.join(package_dir, '..', '..', 'docs')

    globs['test_dir'] = os.path.dirname(__file__)

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) \
            if doc.endswith('.txt') and not doc.endswith('buildout_project.txt')]

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags,
                                          globs=globs, setUp=setUp,
                                          tearDown=tearDown,
                                          module_relative=False,
                                          checker=renormalizing.RENormalizing([
                                                    testing.normalize_path,
                                            ])))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

