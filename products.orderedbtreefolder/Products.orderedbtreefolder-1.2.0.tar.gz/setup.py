"""
This module contains a Zope2 product for an ordered btreefolder.
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    data = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return data + '\n\n'

version = '1.2.0'

long_description = (
    '.. contents ::\n\n' +
    read('CHANGES.txt') +
    read('Products', 'orderedbtreefolder', 'README.txt')
    )

tests_require=['zope.testing']

setup(name='Products.orderedbtreefolder',
      version=version,
      description="BTree folder with the option to keep an ordering in the items",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='union.cms zope python content',
      author='union.cms developers',
      author_email='dev@unioncms.org',
      url='http://svn.unioncms.org/repos/Products.orderedbtreefolder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Products.CMFCore',
                        'Zope2 >= 2.12',
                        'zope.interface',
                        ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      test_suite = 'Products.orderedbtreefolder.tests',
      )
