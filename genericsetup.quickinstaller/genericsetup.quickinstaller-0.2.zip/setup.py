# -*- coding: utf-8 -*-
"""
This module contains the tool of genericsetup.quickinstaller
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
#    'Detailed Documentation\n'
#    '**********************\n'
#    + '\n' +
#    read('genericsetup', 'quickinstaller', 'README.txt')
#    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require=['zope.testing']

setup(name='genericsetup.quickinstaller',
      version=version,
      description="Import step to install products (without profile) in "
        "QuickInstaller",
      long_description=long_description,
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='KULeuven ICTS',
      author_email='wms@icts.kuleuven.be',
      url='http://svn.plone.org/svn/collective/genericsetup.quickinstaller',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['genericsetup', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'Products.GenericSetup',
                        'Products.CMFQuickInstallerTool',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'genericsetup.quickinstaller.tests.test_docs.test_suite',
      )
