#!/usr/bin/env python

# Copyright (c) 2008-2009 Adroll.com, Valentino Volonghi.
# See LICENSE for details.

"""
Distutils installer for turtl.
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import turtl
version = turtl.__version__

install_requires = ["Twisted>=8.0.1", "PyYAML>=3.0.8"]

description = """\
Turtl is an HTTP proxy whose purpose is to throttle connections to
specific hostnames to avoid breaking terms of usage of those API
providers (like del.icio.us, technorati and so on).
"""

setup(package_data={'turtl': [], 'twisted': ['plugins/turtl_plugin.py']},
      description=description,
      license='MIT License',
      author='Valentino Volonghi',
      author_email='valentino@adroll.com',
      include_package_data=True,
      url='http://adroll.com/labs',
      version='0.1.1',
      zip_safe=False,
      install_requires=['Twisted>=8.0.1', 'PyYAML>=3.0.8'],
      packages=['turtl', 'turtl.test', 'twisted'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Internet'],
      name='turtl')
