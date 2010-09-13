# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.scriptgen
"""
from setuptools import setup, find_packages


README = open('README.txt').read()
HISTORY = open('HISTORY.txt').read()

COLLECTIVE_SVN = 'http://svn.plone.org/svn/collective'

version = '0.2'

entry_point = 'collective.recipe.scriptgen:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='collective.recipe.scriptgen',
      version=version,
      description="zc.buildout recipe for generating a script",
      long_description=README + '\n\n' + HISTORY,
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url=COLLECTIVE_SVN + '/buildout/collective.recipe.scriptgen',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'],
      entry_points=entry_points,
      )
