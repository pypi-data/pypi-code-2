#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for distributing PyCant

Typical usage scenario is:
  ./setup.py clean
  ./setup.py bdist --format=bztar
"""

from distutils.core import setup


if __name__ == "__main__":
    setup(
        name = "PyCant",
        version = "11.07.23.0",
        license = "GPLv3",
        description = "Python bindings for IPL Cantata++ test results",
        author = "Guillaume Lemaître",
        author_email = "guillaume.lemaitre@gmail.com",
        url = "http://www.lemaître.eu/PyCant",
        packages = ["pycant"],
        data_files = [
            ("/usr/share/doc/pycant", [
                    "Doc/AUTHOR",
                    "Doc/BUGS",
                    "Doc/CHANGELOG",
                    "Doc/COPYING",
                    ]),
            ],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development :: Quality Assurance",
            "Topic :: Software Development :: Testing",
            ],
        )
