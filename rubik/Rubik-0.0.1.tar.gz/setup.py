import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
#def read(fname):
#    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Rubik",
    version = "0.0.1",
    author = "Md. Imrul Hassan",
    author_email = "mdimrul_hassan@yahoo.com",
    description = ("A Rucik's Cube game."),
    license = "BSD",
    keywords = "Rubik Cube Game Puzzle",
    url = '',
    packages=['Rubik','Rubik.Model','Rubik.View','Rubik.Controller'],
    long_description='Requires visual module from VPython.',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
)
