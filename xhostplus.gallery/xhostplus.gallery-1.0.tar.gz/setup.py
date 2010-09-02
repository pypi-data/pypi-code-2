# -*- coding: utf-8 -*-
"""
This module contains the tool of xhostplus.gallery
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

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
    read('xhostplus', 'gallery', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

tests_require=['zope.testing']

setup(name='xhostplus.gallery',
      version=version,
      description="XHOSTPLUS Gallery",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Gallery Plugin Product Plone XHOSTPLUS',
      author='Andreas Stocker',
      author_email='andreas.stocker@xhostplus.at',
      url='http://www.xhostplus.at',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xhostplus', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Plone',
        'setuptools',
        # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'xhostplus.gallery.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
