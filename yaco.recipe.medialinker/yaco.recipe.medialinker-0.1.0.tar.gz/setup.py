# Copyright (c) 2010 by Yaco Sistemas  <lgs@yaco.es>
#
# This file is part of yaco.recipe.medialinker.
#
# yaco.recipe.medialinker is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# yaco.recipe.medialinker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with yaco.recipe.medialinker.
# If not, see <http://www.gnu.org/licenses/>.

import os.path
from setuptools import setup, find_packages

name = 'yaco.recipe.medialinker'
version = '0.1.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    url='http://bitbucket.org/lgs/yaco.recipe.medialinker',
    author=('Yaco Sistemas (Lorenzo Gil)'),
    author_email='lgs@yaco.es',
    license='LGPL',
    description='Buildout recipe for sym linking media files in Django projects',
    long_description=(read('README') + '\n\n' + read('CHANGES.txt')),
    keywords='django media',
    classifiers = ["Development Status :: 4 - Beta",
                   "Framework :: Django"],
    packages=find_packages(),
    namespace_packages=['yaco', 'yaco.recipe'],
    install_requires=['setuptools', 'zc.buildout'],
    entry_points = {
        'zc.buildout': ['default = %s:MediaLinker' % name],
        'zc.buildout.uninstall': ['default = %s:uninstall' % name],
        },
    zip_safe=False,
    ),
