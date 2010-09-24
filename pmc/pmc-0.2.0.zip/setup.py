#!/usr/bin/env python

from distutils.core import setup

setup(name='pmc',
      version='0.2.0',
      description='A module to control the mplayer',
      classifiers=['Development Status :: 4 - Beta',
                   #'Development Status :: 5 - Production/Stable'
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Multimedia',
                   'Topic :: Multimedia :: Sound/Audio :: Players',
                   'Topic :: Multimedia :: Video',
                   'Topic :: Multimedia :: Video :: Display'],
      keywords='mplayer control video audio',
      author='David Herberth',
      author_email='admin@dav1d.de',
      #url='http://mplayerctrl.dav1d.de',
      py_modules=['pmc'],
      license='MIT',
      platforms='any'
     )
