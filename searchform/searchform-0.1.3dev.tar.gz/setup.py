# Copyright (c) 2008 by Yaco Sistemas S.L.
# Contact info: Lorenzo Gil Sanchez <lgs@yaco.es>
#
# This file is part of searchform
#
# searchform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# searchform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with searchform.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup

from searchform import version


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="searchform",
    version=version,
    author="Lorenzo Gil Sanchez",
    author_email="lgs@yaco.es",
    description="An advanced search form application for Django",
    long_description=(read('README.txt') + '\n\n' + read('CHANGES.txt')),
    license="LGPL 3",
    keywords="search django",
    packages=['searchform'],
    include_package_data=True,
    url='https://tracpub.yaco.es/djangoapps/wiki/SearchForm',
    zip_safe=False,
    test_suite="tests",
    )
