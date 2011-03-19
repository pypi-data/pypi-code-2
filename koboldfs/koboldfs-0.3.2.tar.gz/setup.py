# koboldfs
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from setuptools import setup, find_packages

install_requires = [
    'SQLAlchemy>=0.6',
]

tests_require = [
    'pysqlite',
]

extras_require = dict(
    test=tests_require,
    transaction=[
        'transaction',
    ],
)

setup(
    name='koboldfs',
    version='0.3.2',
    url='http://pypi.python.org/pypi/koboldfs',
    license='GPL 2',
    author='Tranchitella Kft.',
    author_email='info@tranchitella.eu',
    description='application-level distributed file system written in Python',
    long_description=(
        open('README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        'Intended Audience :: System Administrators',
        'License :: DFSG approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        "Programming Language :: Python",
        'Topic :: System :: Filesystems',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=install_requires + tests_require,
    test_suite="koboldfs.tests",
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': ['koboldfsd = koboldfs.server:main']
    },
)
