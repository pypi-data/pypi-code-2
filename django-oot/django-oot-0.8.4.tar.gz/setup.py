# Copyright (c) 2008-2010 by Yaco Sistemas <precio@yaco.es>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="django-oot",
    version="0.8.4",
    author="Yaco Sistemas S.L.",
    author_email="precio@yaco.es",
    description="Django application to export content to OpenOffice documents",
    long_description=(read('README')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Office/Business :: Office Suites',
    ],
    license="LGPL 3",
    keywords="django openoffice odt",
    url='http://tracpub.yaco.es/djangoapps/wiki/OOT',
    packages=find_packages('.'),
    include_package_data=True,
)
