# Copyright (c) 2010 by Yaco Sistemas <lgs@yaco.es>
#
# This file is part of yaco.hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages

from yaco.hghooks import version


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='yaco.hghooks',
    version=version,
    author='Lorenzo Gil Sanchez',
    author_email='lgs@yaco.es',
    description='Extensions to hghooks used at Yaco Sistemas',
    long_description='\n\n'.join([read('README.txt'), read('CHANGES.txt')]),
    license='LGPL 3',
    keywords='mercurial hooks trac yaco',
    url='http://bitbucket.org/lgs/yaco.hghooks',
    packages=find_packages('.'),
    namespace_packages=['yaco'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hghooks',
        ],
    entry_points={
        'hghooks.trac.ticket_commands': [
            'yaco = yaco.hghooks:yaco_ticket_commands',
            ],
        'hghooks.trac.token_commands': [
            'yaco = yaco.hghooks:yaco_token_commands',
            ]
        },
    )
