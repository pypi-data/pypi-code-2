# Copyright(c) 2011 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of hamster-rc.
# hamster-rc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# hamster-rc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with hamster-rc.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="hamster-rc",
    version="0.1.1",
    author="Lorenzo Gil Sanchez",
    author_email="lorenzo.gil.sanchez@gmail.com",
    description="Hamster Remote Control",
    long_description='\n\n'.join([read('README.txt'), read('CHANGES.txt')]),
    license="GPL 3",
    keywords="hamster",
    packages=find_packages(),
    url='http://bitbucket.org/lgs/hamster-rc/',
    install_requires=[
        'distribute',
        'mako',
        'Routes',
        'WebOb',
        ],
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'hamster-rc = hamster_rc:main',
            ]
        },
    )
