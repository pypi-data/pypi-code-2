#!/usr/bin/env python

from setuptools import setup
setup(name='boggleboard',
      version='1.0.5',
      description='Manipulate and analyse anagrams and variations of Boggle boards.',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['boggleboard'],
      long_description="""
A package to generate and manipulate Boggle-style boards. Boards of different
sizes can be randomly generated, and given a list of acceptable words, the
package can find all words in a particular Boggle board. Currently, the package
offers standard nxn Boggle boards, arbitrary rectangular Boggle boards, and
toroidal Boggle boards (i.e. boards where one can scroll from the top row to the
bottom row and vice-versa, and from the left column to the right column and
vice-versa).

Additionally, the package contains an anagram-type solver, such as finding the
words in a Scrabble hand.

Boards of arbitrary shapes and sizes can be made by subclassing the
AbstractBoggleBoard class and specifying an adjacency graph using the positions
of the board as nodes.

1.0.5: Minor bugfix.
       * Fixed improper use of NotImplemented.
1.0.4: Fixed code to be Python 3 compatible.
       * Changed print statements for Python 3 compatability.
1.0.3: Added hexagonal Boggle board classes:
       * RectangularHexagonalBoggleBoard
       * HexagonalBoggleBoard
       * RectangularToroidalHexagonalBoggleBoard
       * ToroidalHexagonalBoggleBoard.
1.0.2: Added default dice from original Boggle game and changed the name
       of the challenge die as it is not specific to Big Boggle.
1.0.1: Minor fixes and improvements in documentation.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: Puzzle Games',
        ],
      keywords='boggle anagram anagrams board games puzzles',
      license='Apache 2.0'
      )
