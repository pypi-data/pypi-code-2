# Copyright 2010 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from setuptools import setup

import gabi


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='gabi',
    version=gabi.__version__,
    author=gabi.__author__,
    author_email=gabi.__email__,
    description='Google Address Book Importer',
    long_description=(read('README')
                      + '\n\n' +
                      read('CHANGES')),
    license=gabi.__license__,
    keywords='email google mutt backup',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    zip_safe=False,
    url='http://bitbucket.org/lgs/gabi/',
    install_requires=['gdata'],
    entry_points={
        'console_scripts': [
            'gabi = gabi:main',
            ],
        },
    )
