# encoding: utf-8
from setuptools import setup

setup(
  name='codepad',
  version='0.1',
  url="https://github.com/daltonmatos/codepad",
  license="3-clause BSD",
  description="A Command line interface for codepad.org",
  author="Dalton Barreto",
  author_email="daltonmatos@gmail.com",
  packages=['codepad'],
  scripts=['scripts/codepad'],
  install_requires = ['requests'],
  classifiers = [
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ])

