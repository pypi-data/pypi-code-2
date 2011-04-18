# -*- coding: utf-8 -*-
# $Id: setup.py 237778 2011-04-18 10:40:52Z glenfant $
"""Packaging and distributing aws.zope2zcmldoc"""

from setuptools import setup, find_packages
import os

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

setup(name='aws.zope2zcmldoc',
      version=read('aws', 'zope2zcmldoc', 'version.txt'),
      description="ZCML documentation browser for Zope 2",
      long_description=(read('README.txt') + "\n" +
                        read('docs', 'HISTORY.txt')),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Zope2",
          "Intended Audience :: Developers",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Topic :: Software Development :: Documentation"
          ],
      keywords='zope2 zcml documentation',
      author='Gilles lenfant',
      author_email='gilles.lenfant@alterway.fr',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['aws'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
