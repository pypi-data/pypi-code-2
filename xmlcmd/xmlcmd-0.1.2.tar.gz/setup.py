#!/usr/bin/python

from distutils.core import setup

setup(
    name="xmlcmd",
    version="0.1.2",
    description="half-baked support for adding --xml support to POSIX commands",
    long_description=open('README.txt').read(),
    author="Ben Bass",
    author_email="benbass@codedstructure.net",
    url="http://bitbucket.org/codedstructure/xmlcmd",
    packages=["xmlcmd"],
    requires=['which'],
    scripts=['scripts/xmlcmd'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Unix Shell",
    ]
)
