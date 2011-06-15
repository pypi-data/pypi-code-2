from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Zarkov',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Rick Copeland',
      author_email='rick@geek.net',
      url='http://sf.net/p/zarkov',
      license='Apache 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'ming',
        'gevent',
        'pyyaml'
          # -*- Extra requirements: -*-
      ],
      scripts=[
        'scripts/zarkov-server', 'scripts/zarkov-perftest'
        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
