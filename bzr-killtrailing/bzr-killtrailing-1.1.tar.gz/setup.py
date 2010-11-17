#!/usr/bin/python

import os.path
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name="bzr-killtrailing",
      version="1.1",
      author="Alexander Solovyov",
      author_email="alexander@solovyov.net",
      url="http://hg.piranha.org.ua/bzr-killtrailing/",
      description="Check trailing whitespaces pre-commit hook for bzr.",
      long_description = read('README'),
      license = "GNU GPL v2+",
      packages=[
        'bzrlib.plugins.killtrailing',
        ],
      package_dir={'bzrlib.plugins.killtrailing': '.'},
      platforms='any',
      )
