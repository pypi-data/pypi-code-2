# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name = 'hghudson',
      version = version,
      description = "Mercurial integration with Hudson",
      long_description = file('README.rst').read(),
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Version Control'
      ],
      keywords = '',
      author = u'Néstor Salceda',
      author_email = 'nestor.salceda@gmail.com',
      url = 'http://www.gitorious.org/hghudson',
      license = 'MIT/X11',
      packages = find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data = True,
      zip_safe = True,
      install_requires = [
          # -*- Extra requirements: -*-
      ],
      entry_points = """
      # -*- Entry points: -*-
      """,
      )
