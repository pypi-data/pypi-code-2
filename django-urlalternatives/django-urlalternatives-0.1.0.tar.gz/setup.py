#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages


setup(
    name="django-urlalternatives",
    version="0.1.0",
    author="GW",
    author_email="gw.2011@tnode.com",
    packages=find_packages(),
    url="http://gw.tnode.com/0483-Django/",
    license="LICENSE.txt",
	description="Django URL alternatives provides a way for dispatching one URL pattern to the first alternative view (callback function) in a list that returns success.",
    long_description=open("README.txt").read(),
)
