# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from os.path import join as pathjoin

VERSION = "0.1.0"
LONG_DESCRIPTION = "".join([
    open(pathjoin("src","README.txt")).read(),
    open(pathjoin("src","TODO.txt")).read()])

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Multimedia :: Sound/Audio :: Speech",
]

setup(
     name="ikazuchi.plugins.speech",
     version=VERSION,
     description="Speech handler with ikazuchi",
     long_description=LONG_DESCRIPTION,
     classifiers=CLASSIFIERS,
     keywords=["speech"],
     author="Tetsuya Morimoto",
     author_email="tetsuya dot morimoto at gmail dot com",
     url="http://t2y.bitbucket.org/ikazuchi/build/html/index.html",
     license="Apache License 2.0",
     py_modules=[],
     packages=find_packages("src"),
     package_dir={"": "src"},
     package_data={"": ["buildout.cfg"]},
     namespace_packages=["ikazuchi", "ikazuchi.plugins"],
     include_package_data=True,
     install_requires=["distribute", "pyglet", "ikazuchi>=0.5.1"],
     extras_require={
        "test": ["Nose", "pep8"],
     },
     test_suite="nose.collector",
     tests_require=["Nose", "pep8"],
     entry_points={
        "ikazuchi.plugins": [
            "speech = ikazuchi.plugins.speech",
        ],
    },
)
