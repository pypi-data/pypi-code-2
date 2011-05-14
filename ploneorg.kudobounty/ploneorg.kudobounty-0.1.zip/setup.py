# -*- coding: utf-8 -*-
"""
This module contains the tool of ploneorg.kudobounty
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('ploneorg', 'kudobounty', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='ploneorg.kudobounty',
      version=version,
      description="Bounty Program logo display mechanism for the plone.org",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='mylan at quintagroup.com',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ploneorg', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'Products.PloneFormGen',
                        'Products.ContentWellPortlets',
                        'collective.portlet.collectionmultiview',
                        'plone.i18n',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='ploneorg.kudobounty.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
