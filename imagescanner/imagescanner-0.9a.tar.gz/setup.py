#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='imagescanner',
      version='0.9a',
      description='Multi-platform Python library to access scanner devices.',
      author='Sergio Oliveira',
      author_email='seocam@seocam.com',
      url='http://code.google.com/p/imagescanner/',
      packages=find_packages(),
      package_data={'': ['*.tiff']},
      install_requires=['python-cjson', 'autoconnect', 'PIL'],
      classifiers = [
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
      ]
     )

