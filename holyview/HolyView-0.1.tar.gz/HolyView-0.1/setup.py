#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='HolyView',
      version='0.1',
      description='Ncurse tool to help you choose what you want to do',
      long_description=open("README.rst").read(),
      author='Laurent Peuch',
      author_email='cortex@worlddomination.be',
      url='http://blog.worlddomination.be/holyview',
      install_requires=['urwid>=0.9.9.1', 'louie'],
      license="GPLv3+",
      scripts=['holyview'],
      platforms="any",
      keywords="ncurse todo todolist 7habits",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console :: Curses',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Programming Language :: Python',
                   'Topic :: Desktop Environment',
                  ],
     )

# vim:set shiftwidth=4 tabstop=4 expandtab:
