# Copyright (c) 2011 ActiveState Software Inc. All rights reserved.

from setuptools import setup, find_packages
import sys, os
from os import path


here = os.path.abspath(path.dirname(__file__))
README = open(path.join(here, 'README.rst')).read()
NEWS = open(path.join(here, 'NEWS.rst')).read()


setup(name='django-stackato',
      version='1.0',
      description="Django Stackato Extensions -- non-interactive changepassword",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6', # minimum supported = 2.6
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
      keywords='stackato django activestate',
      author='Sridhar Ratnakumar', 
      author_email='sridharr@activestate.com',
      url='http://github.com/ActiveState/django-stackato',
      license='MIT',
      packages=find_packages(exclude=[
          'examples', 'tests']),
      include_package_data=True,
      )
