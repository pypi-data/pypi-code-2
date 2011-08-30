# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

version = '1.0.0rc1'

tests_require=['zope.testing']

setup(name='redturtle.imagedevent',
      version=version,
      description="A replacement of the Event content type for Plone, with image field and "
                  "separate keyword and event type fields.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone event image content plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/redturtle.imagedevent',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'archetypes.schemaextender'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'redturtle.imagedevent.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
