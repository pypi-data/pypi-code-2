#!/usr/bin/env python


"""Distutils distribution file"""


from setuptools import setup

import game.common

setup(name='WordGolf',
      version=game.common.version,
      description='Word game that combines Boggle-like word finding with golf.',
      author='Paul Paterson',
      author_email='ppaterson@gmail.com',
      url='http://www.perpetualpyramid/wordgolf.html',
      download_url=('http://perpetualpyramid.com/WordGolf-%s.tar.gz' % game.common.version),
      packages=[
        'serge', 'serge.blocks', 'game',
      ],
      package_dir={},
      package_data={'': ['*.py', '*.txt', 'graphics/*.png', 'graphics/*.ico', 'sound/*.*', 'words/*.*']},
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Puzzle Games",
        ],
       install_requires=[
       # 'pygame',
       ],
       long_description='''\
Word Golf
---------

An addictive word game based on a combination of the word game Boggle and golf.

You play a series of holes and try to combine words with enough letters to make
it to the hole. Each hole has a par so try to use as few words as possible.

On the harder levels, stay away from bunkers and water traps to avoid penalty strokes.

Requires: Python 2.6+ and pygame 1.9+

''',
         )
     
