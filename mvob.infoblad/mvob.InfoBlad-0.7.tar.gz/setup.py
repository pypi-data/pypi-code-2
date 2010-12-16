# -*- coding: utf-8 -*-
"""
This module contains the tool of mvob.InfoBlad
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.7'

try:
    long_description=read("README.txt") + "\n" + read("docs", "HISTORY.txt")
except:
    long_description=''

tests_require = ['zope.testing']

setup(name='mvob.InfoBlad',
      version=version,
      description="Type that is similar to Document but is folderish and has a view to display images in a photoalbum",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='type archetype blad info',
      author='David Jonas',
      author_email='david@v2.nl',
      url='https://svn.v2.nl/plone/mvob.InfoBlad',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mvob', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='mvob.InfoBlad.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
