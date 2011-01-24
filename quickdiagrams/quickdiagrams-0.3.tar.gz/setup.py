#!/usr/bin/env python
from setuptools import setup


setup(name='quickdiagrams',
  version='0.3',
  description='A text-to-class_diagram conversion tool.',
  author='Hugo Ruscitti',
  install_requires=['pygraphviz'],
  author_email='hugoruscitti@gmail.com',
  packages=['quickdiagrams', 'quickdiagrams.gtkclient'],
  scripts=['bin/quickclassdiagram', 'bin/quickclassdiagramgtk'],
  )
