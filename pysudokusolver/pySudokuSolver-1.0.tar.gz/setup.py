#! /usr/bin/python
# -*- coding: UTF-8 -*-
# setup.py    [Sudoku Solver 1.0]

# This is used just for registering this project on PyPI.

__author__ = "Pushpak Dagade (पुष्पक दगड़े)"
__date__   = "$May 19, 2011 10:25:17 PM$"

from setuptools import setup

long_description= """Sudoku Solver is a graphical application for solving
any Sudoku puzzle, almost instantly. Moreover it also shows the steps taken
in solving the same."""

setup(
    name = 'pySudokuSolver',
    version = '1.0',
    scripts = ['README', 'LICENSE', 'Sample Solution',],
    packages = ['.'],
    author = 'Pushpak Dagade',
    author_email = 'guanidene@gmail.com',
    url = 'http://guanidene.blogspot.com/2011/07/sudoku-solver-with-gui-written-in.html',
    description = "A small graphical utility for solving any Sudoku puzzle,"\
                  " almost instantaneoulsy.",
    long_description = long_description,
    )
