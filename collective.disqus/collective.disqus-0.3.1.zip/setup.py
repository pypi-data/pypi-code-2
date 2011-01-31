from setuptools import setup, find_packages
import os

version = '0.3.1'

setup(name = 'collective.disqus',
      version = version,
      description = "Integrates DISQUS comment system with Plone.",
      long_description = open("README.txt").read() + "\n" +
                         open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords = 'plone disqus discusion blog comment',
      author = 'Wojciech Lichota',
      author_email = 'wojciech@lichota.pl',
      url = 'http://lichota.pl/blog/topics/disqus',
      license = 'Zope Public License, Version 2.1 (ZPL)',
      packages = find_packages('src'),
      include_package_data = True,
      package_dir = {'':'src'},
      namespace_packages = ['collective'],
      zip_safe = False,
      install_requires = [
          'setuptools',
          'z3c.autoinclude',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
        'tests': [
            'plone.app.testing',
            ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
