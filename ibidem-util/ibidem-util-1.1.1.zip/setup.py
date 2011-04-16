#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup

def read(filename):
    f = open(filename)
    contents = f.read()
    f.close()
    return contents

classifiers = """
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

setup(
    name = "ibidem-util",
    version = "1.1.1",
    packages = ["ibidem", "ibidem.util"],
    namespace_packages = ["ibidem"],
    zip_safe = True,
    include_package_data = True,

    # Metadata
    author = "Morten Lied Johansen",
    author_email = "mortenjo@ifi.uio.no",
    description = "Ibidem utilities",
    long_description = read("README.rst"),
    license = "LGPL",
    keywords = "ibidem util",
    classifiers = filter(None, classifiers.split("\n")),
    url = "http://ibidem.homeip.net/Misc/wiki/Utils"
)
