# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 1 - Planning",
    "Natural Language :: Japanese",
    "Programming Language :: Python",
]

long_description = """\
`maro` is a package for exercises.

---------------------
Requirements
---------------------
* Python 2.6 or later (not support 3.x)

---------------------
Features
---------------------
* nothing

---------------------
Setup
---------------------
::

    $ easy_install maro

---------------------
History
---------------------
0.0.1 (2011-06-25)
~~~~~~~~~~~~~~~~~~~~~
* first release

"""

setup(
    name="maro",
    version="0.0.1",
    packages=find_packages(),
    namespace_packages=["maro"],
    description="`maro` is a package for exercises.",
    long_description=long_description,
    classifiers=classifiers,
    keywords=["oyakata", "maro"],
    author="oyakata(imagawa_yakata)",
    author_email="imagawa.yakata+maro at gmail.com",
    url="https://bitbucket.org/imagawa_yakata/maro",
    license="PSL",
)

