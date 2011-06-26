# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 1 - Planning",
    "Natural Language :: Japanese",
    "Programming Language :: Python",
]

long_description = """\
`django-maro` is utility for django.

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

0.0.2 (2011-06-26)
~~~~~~~~~~~~~~~~~~~~~
* add static_query function.

"""

setup(
    name="django-maro",
    version="0.0.2",
    packages=find_packages(),
    namespace_packages=["maro", "maro.love"],
    description="`django-maro` is utility for django.",
    long_description=long_description,
    classifiers=classifiers,
    keywords=["oyakata", "maro", "django"],
    author="oyakata(imagawa_yakata)",
    author_email="imagawa.yakata+maro at gmail.com",
    url="https://bitbucket.org/imagawa_yakata/django-maro",
    license="PSL",
)

