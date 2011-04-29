#!/usr/bin/env python2
# coding:utf-8

import os
from setuptools import setup, find_packages

from pyinputstatsmodules import __VERSION__, __NAME__

#~ def read(fname):
    #~ return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup (
    name = __NAME__.lower(),
    version = __VERSION__,
    author = "Daniel Nögel",
    include_package_data=True,
    install_requires = ["Python_Xlib", "pysqlite>=2"],
    url = "http://launchpad.net/pyinputstats",
    author_email = "pyinputstats@post.danielnoegel.de",
    description = ("An application for keyboard and mouse statistics"),
    long_description = """pyInputStats - An keyboard and mouse statistics tool

pyInputStats watches your mouse and your keyboard in order to generate some statistics. With pyInputStats you are able to answer substantial questions like:
* how many metres do I move my mousepointer every day
* how many times to I press a key on my keyboard
* do I click my mouse more oftenly on fridays?
* to I make more mouse-metres in the morning hours?""",
    license = "GPLv3",
    keywords = "keyboard mouse statistics",
    packages = find_packages(),
    scripts = ["pyinputstats"], 
    package_data = {
        "": ["*.txt"],
        "pyinputstats": ["*.glade", "images/*.png"],
        "pygtk_chart": ["data/*.color"],
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python"
    ]
)
