#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="cony",
    version="0.1.0",
    description=(
        '"Cony" is a tool that lets you write smart bookmarks in '
        'python and then share them across all your browsers and with a '
        'group of people or the whole world. This project inspired '
        'by Facebook\'s bunny1.'
    ),
    author="Alexander Artemenko",
    author_email='svetlyak.40wt@gmail.com',
    url='http://dev.svetlyak.ru/',
    packages=find_packages(),
    scripts=['cony.py'],
)
