# -*- coding:utf8 -*-

from setuptools import setup, find_packages
import os

from distutils.core import setup

setup(name='hangul.translit',
  version='0.1',
  description="Transliteration of Hangul(Korean) to Roman writing system following Revised Romanization of Korean(2000).",
  #long_description=open("README.txt").read(),
  long_description = """
  Usage
    =====
    
    >>> from hangul import translit
    >>> translit.test()
    >>> s = translit.romanize('<some Hangul>')
  """,
  classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
  keywords='korean hangul romanization transliteration', 
  packages=find_packages(exclude=['ez_setup']),
  namespace_packages=['hangul'],
  license='BSD',
  author_email='lee.soonyeon@gmail.com',
  author='Lee Sun-yeon'
)
