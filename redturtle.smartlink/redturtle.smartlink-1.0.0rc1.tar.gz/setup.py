# -*- coding: utf-8 -*-
"""
This module contains the tool of redturtle.smartlink
"""
import os
from setuptools import setup, find_packages

version = '1.0.0rc1'

tests_require = ['zope.testing']

setup(name='redturtle.smartlink',
      version=version,
      description=("An advanced Link content type for Plone, "
                   "with image field and internal link feature"),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Plone',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone archetype link internal content plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/smart-link',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Plone',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='redturtle.smartlink.tests.test_docs.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
