#!/usr/bin/env python
# coding:utf-8

import os
from setuptools import setup, find_packages

from lsrsidmodules import __VERSION__, __TITLE__

#~ def read(fname):
    #~ return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup (
    name = __TITLE__,
    version = __VERSION__,
    author = "Daniel Nögel",
    include_package_data=True,
    install_requires = ["pysqlite>=2"],
    #~ homepage = "http://launchpad.net/pymeasure",
    author_email = "lsrsid@post.danielnoegel.de",
    description = ("A SID music database and sidplay frontend"),
    long_description = """lsR.SID?""",
    license = "GPLv3",
    keywords = "sid sidplay frontend music",
    packages = find_packages(),
    scripts = ["lsrsid"], 
    package_data = {
        "": ["*.txt"],
        "lsrsid": ["*.glade", "images/*.png"],
        "pygtk_chart": ["data/*.color"],
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Topic :: Multimedia",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python"
    ]
)
