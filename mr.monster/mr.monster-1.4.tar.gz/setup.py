from setuptools import setup, find_packages
import os

version = '1.4'

setup(name='mr.monster',
      version=version,
      description="A URL rewriting middleware that emulates a VHM url.",
      long_description=open(os.path.join('src', 'mr', 'monster', 'README.txt')).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matt.wilkes@teamrubber.com',
      url='http://www.teamrubber.com',
      license='BSD',
      package_dir = {'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['mr'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'WebOb',
      ],
      entry_points="""
      # -*- Entry points: -*-
[paste.filter_factory]
rewrite = mr.monster.rewrite:RewriteFactory
reroot = mr.monster.drop:DropFactory
      """,
      )
