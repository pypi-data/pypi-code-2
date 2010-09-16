##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.debugskin package

$Id: setup.py 81038 2007-10-24 14:34:17Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.debugskin',
      version='3.4.1',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Debug -- A Zope 3 ZMI Skin',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 debug skin zmi",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/zope.app.debugskin',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(
          test = ["zope.app.testing",
                  "zope.app.zcmlfiles",
                  "zope.app.securitypolicy"]
      ),
      install_requires=["setuptools",
                        "zope.app.rotterdam",
                        "zope.app.skins",
                        "zope.publisher"],
      include_package_data = True,
      zip_safe = False,
      )
