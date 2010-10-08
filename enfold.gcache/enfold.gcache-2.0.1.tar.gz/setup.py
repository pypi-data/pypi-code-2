# Copyright: Enfold Systems, LLC

# Setup script for the 'enfold.gcache' package.

import sys, os
from setuptools import setup, find_packages

version = '2.0.1'

setup(
    name="enfold.gcache",
    version=version,
    author='Enfold Systems',
    author_email='info@enfoldsystems.com',
    description="Simple pluggable caching server.",
    url='http://www.enfoldsystems.com',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      ],
    keywords='cache caching',
    license='LGPL',
    packages = find_packages('src', exclude=['examples', 'tests']),
    package_dir = {'': 'src'},
    namespace_packages=['enfold'],
    zip_safe=False,
    install_requires=[
          'distribute',
          'python-dateutil',
          'zope.interface',
      ],
    include_package_data = True,    # include everything in source control
)
