# -*- coding: utf-8 -*-
"""
This module contains the tool of Products.Carousel
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.1b3'

long_description = (
    read('Products', 'Carousel', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    )

tests_require=['zope.testing']

setup(name='Products.Carousel',
      version=version,
      description="Carousel allows you to add user-configurable rotating banners to any section of a Plone site.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        ],
      keywords='plone carousel slideshow banners rotating features',
      author='Groundwire',
      author_email='davidglick@groundwire.org',
      url='http://svn.plone.org/svn/collective/Products.Carousel',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plone.app.z3cform',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'Products.Carousel.tests.test_docs.test_suite',
      )
