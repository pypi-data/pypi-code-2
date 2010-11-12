# -*- coding: utf-8 -*-
"""
This module contains the tool of pas.plugins.userdeletedevent
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'History\n'
    '**************\n'
    + '\n' +
    read('docs', 'HISTORY.txt')
    )

tests_require=['zope.testing']

setup(name='pas.plugins.userdeletedevent',
      version=version,
      description="A PAS plugin for firing events on user deletion",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        'Intended Audience :: Developers',
        "Intended Audience :: System Administrators",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Simone Orsi [simahawk]',
      author_email='simahawk@gmail.com',
      url='https://svn.plone.org/svn/collective/PASPlugins/pas.plugins.userdeletedevent',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pas', 'pas.plugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=["setuptools",
                        "Products.PluggableAuthService",
                        "Products.PlonePAS",
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'pas.plugins.userdeletedevent.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
