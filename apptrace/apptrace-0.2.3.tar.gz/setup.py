# Copyright 2010, 2011 Tobias Rodaebel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Setup script for the apptrace package."""

from distutils.cmd import Command
from distutils.core import setup
from setuptools import setup, find_packages
from unittest import TestLoader, TextTestRunner

import os
import sys


class test(Command):
    """Runs the unit tests for apptrace."""

    description = "Runs unit tests for apptrace."

    user_options = [
        ('appengine-path=', None, 'path to the Google App Engine distribution')
    ]

    def initialize_options(self):
        self.appengine_path = None

    def finalize_options(self):
        pass

    def run(self):
        appengine_path = self.appengine_path or '/'
        extra_paths = [
            appengine_path,
            os.path.join(appengine_path, 'lib', 'antlr3'),
            os.path.join(appengine_path, 'lib', 'django_0_96'),
            os.path.join(appengine_path, 'lib', 'fancy_urllib'),
            os.path.join(appengine_path, 'lib', 'ipaddr'),
            os.path.join(appengine_path, 'lib', 'webob'),
            os.path.join(appengine_path, 'lib', 'yaml', 'lib'),
            os.path.join(appengine_path, 'lib', 'lib', 'simplejson'),
            os.path.join(appengine_path, 'lib', 'lib', 'graphy'),
        ]
        sys.path.extend(extra_paths)

        import apptrace.tests

        loader = TestLoader()
        t = TextTestRunner()
        t.run(loader.loadTestsFromModule(apptrace.tests))

# 'test' is the parameter as it gets added to setup.py
cmdclasses = {'test': test}


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='apptrace',
    version='0.2.3',
    author="Tobias Rodaebel",
    author_email="tobias.rodaebel@googlemail.com",
    description=("WSGI middleware to measure the memory footprint of GAE "
                 "Python applications."),
    long_description=(
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
        ),
    license="Apache License 2.0",
    keywords="google app engine gae heapy guppy",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        ],
    url='http://code.google.com/p/apptrace',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'distribute',
        'guppy',
    ],
    entry_points={
        'console_scripts': [
            'apptracectl = apptrace.scripts.apptracectl:main'
        ],
    },
    zip_safe=False,
    cmdclass=cmdclasses
)
