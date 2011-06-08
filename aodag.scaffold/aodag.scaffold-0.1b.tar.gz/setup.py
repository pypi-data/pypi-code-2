from setuptools import setup, find_packages

import os
import sys

requires = []

if sys.version_info < (2, 7):
    requires.append('argparse')

if sys.version_info[0] == 3 and sys.version_info < (3, 2):
    requires.append('argparse')

here = os.path.dirname(__file__)

readme = open(os.path.join(here, "README.txt")).read()
changes = open(os.path.join(here, "CHANGES.txt")).read()

setup(
    name="aodag.scaffold",
    author="Atsushi Odagiri",
    author_email="aodagx@gmail.com",
    version="0.1b",
    description="tool for manage scaffolds",
    long_description=readme + "\r\n" + changes,
    license="MIT",
    test_suite="aodag.scaffold",
    packages=find_packages(),
    namespace_packages=['aodag'],
    install_requires=requires,
    entry_points={
        "console_scripts":[
            "scaffold=aodag.scaffold.commands:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Code Generators",
    ],
)
