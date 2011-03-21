# Copyright (c) 2011 by Yaco Sistemas  <lgs@yaco.es>
#
# This file is part of yaco.recipe.cert
#
# yaco.recipe.cert is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# yaco.recipe.cert is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with yaco.recipe.cert.
# If not, see <http://www.gnu.org/licenses/>.

import os.path
from setuptools import setup, find_packages

name = 'yaco.recipe.cert'
version = '0.1.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    url='http://bitbucket.org/lgs/yaco.recipe.cert',
    author=('Yaco Sistemas (Lorenzo Gil)'),
    author_email='lgs@yaco.es',
    license='LGPL',
    description='Buildout recipe for creating self signed certificates',
    long_description=(read('README.txt') + '\n\n' + read('CHANGES.txt')),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Buildout",
        "Framework :: Buildout :: Recipe",
        ],
    keywords='buildout certificate',
    packages=find_packages(),
    namespace_packages=['yaco', 'yaco.recipe'],
    install_requires=['setuptools', 'zc.buildout'],
    entry_points = {
        'zc.buildout': ['default = %s:CertificateGenerator' % name],
        },
    zip_safe=False,
    )
