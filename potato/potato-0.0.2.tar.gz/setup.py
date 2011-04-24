import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "potato",
    version = "0.0.2",
    author = "Sean Ochoa",
    author_email = "sean.m.ochoa@gmail.com",
    description = ("a dynamic class loader"),
    license = "Eclipse Public License -v 1.0",
    keywords = "dynamic class loading",
    url = "https://github.com/seanochoa/potato",
    packages=find_packages(exclude=["test"]),
    long_description=read('README'),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Operating System :: OS Independent"
    ],
    install_requires=['zope.interface']
)
