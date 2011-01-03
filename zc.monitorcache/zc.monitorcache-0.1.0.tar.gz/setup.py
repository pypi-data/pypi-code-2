##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import os, setuptools


def read(name):
    fn = os.path.join(os.path.dirname(__file__), *name.split('/'))
    with open(fn) as f:
        return f.read()

setuptools.setup(
    name = 'zc.monitorcache',
    version = '0.1.0',
    author = 'Alex Chapman',
    author_email = 'achapman@zope.com',
    description = 'zc.monitor plugin to modify cache sizes',
    long_description = read('src/zc/monitorcache/README.txt'),
    license = 'ZPL 2.1',
    include_package_data = True,
    packages = setuptools.find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools', 'zc.monitor', 'zc.z3monitor'],
    zip_safe = False,
    extras_require = dict()
    )
