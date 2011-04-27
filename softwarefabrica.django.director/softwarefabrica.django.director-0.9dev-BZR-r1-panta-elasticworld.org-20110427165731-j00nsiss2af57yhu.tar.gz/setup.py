#! /usr/bin/env python

"""Installation script for softwarefabrica.django.director
Run it with
 './setup.py install', or
 './setup.py --help' for more options
"""

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from softwarefabrica.django.director.version import VERSION, get_version_setuptools
from softwarefabrica.django.director.finddata import find_package_data
#VERSION = "0.9"

# Dynamically calculate the version based on VERSION.
version = get_version_setuptools()

pypi_version = version.replace('_', '-')
pypi_version = version.replace('@', '-')

long_description = (
    read('docs/overview.txt') +
    '\n\n' )

setup(
    name = "softwarefabrica.django.director",
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://cheeseshop.python.org/pypi/softwarefabrica.django.director/',
    download_url = 'http://pypi.python.org/packages/source/s/softwarefabrica.django.director/softwarefabrica.django.director-%s.tar.gz' % pypi_version,
    #download = 'http://www.softwarefabrica.org/downloads/softwarefabrica.django.director.tar.gz',
    license = 'GNU GPL v2',
    description = 'Advanced model manager for SoftwareFabrica django projects',
    long_description = long_description,
    keywords = 'director model manager infrastructure django softwarefabrica',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages=['softwarefabrica', 'softwarefabrica.django'],
    include_package_data = True,
    exclude_package_data = {
        '': ['.bzr'],
    },
    package_data = find_package_data(),
    zip_safe = False,                   # we include templates and tests
    setup_requires=['setuptools',
                    'sflib>=1.0dev-BZR-r45',
                    ],
    install_requires=['setuptools',
                      'django>=1.0',
                      'sflib>=1.0dev-BZR-r45',
                      'softwarefabrica.django.utils',
                      'softwarefabrica.django.forms',
                      'softwarefabrica.django.crud',
                      'softwarefabrica.django.common',
                      # -*- Extra requirements: -*-
                      ],
    test_suite='nose.collector',
    tests_require=['Nose'],
)
