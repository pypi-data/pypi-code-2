##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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
$Id:$
"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'p01.recipe.setup',
    version = '0.5.0',
    author = 'Roger Ineichen and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'Application installation support recipes',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'p01', 'recipe', 'setup', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope3 p01 dev recipe setup installation installer',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/p01.recipe.setup',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01', 'p01.recipe'],
    extras_require = dict(
        test = [
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'supervisor',
        'superlance',
        ],
    entry_points = {
        'zc.buildout': [
             'mkfile = p01.recipe.setup.mkfile:MKFileRecipe',
             'mkdir = p01.recipe.setup.mkdir:MKDirRecipe',
             'download = p01.recipe.setup.download:DownloadRecipe',
             'template = p01.recipe.setup.template:TemplateRecipe',
             'supervisor = p01.recipe.setup.supervisor:SupervisorRecipe',
             'cmd = p01.recipe.setup.cmd:CMDRecipe',
             'copy = p01.recipe.setup.copy:COPYRecipe',
             'cmmi = p01.recipe.setup.cmmi:CMMIRecipe',
         ]
    },
)
