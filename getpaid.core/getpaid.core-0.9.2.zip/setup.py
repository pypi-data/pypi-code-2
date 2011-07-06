"""
$Id: setup.py 3901 2011-07-06 20:38:41Z dglick@gmail.com $

Copyright (c) 2007 - 2010 ifPeople, Kapil Thangavelu, and Contributors
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup

"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.9.2'

setup(
    name='getpaid.core',
    version=version,
    license = 'ZPL2.1',
    author='Getpaid Community',
    author_email='getpaid-dev@googlegroups.com',
    description='Core ecommerce functionality for zope and python projects',
    long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'getpaid', 'core', 'order.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    classifiers = [
        "Framework :: Plone",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
        ],
    url='http://code.google.com/p/getpaid',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['getpaid'],
    include_package_data=True,
    install_requires = [ 'hurry.workflow',
                         'setuptools',
                         'zope.annotation',
                         'zope.index',
                         'zope.interface',
                         'zope.intid',
                         'zope.event',
                         'zope.schema',
                       ],
    zip_safe = False,
    )
