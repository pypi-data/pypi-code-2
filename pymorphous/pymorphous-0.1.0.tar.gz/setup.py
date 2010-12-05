import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pymorphous",
    packages = ["pymorphous", "pymorphous.implementation", 
                "pymorphous.implementation.simulator", 
                "pymorphous.implementation.webots_wall", 
                "extensions", "examples"],
    py_modules = ['run_pymorphous', 'run_examples', 'settings', 'make_video', "make_gource"],
    version = "0.1.0",
    description = "Spatial computing library and simulator for Python",
    author = "Charles Dietrich",
    author_email = "charles.m.dietrich at gmail",
    url = "http://www.pymorphous.org/",
    keywords = ["spatial_computing", "amorphous_computing", "simulator", "robotics"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: Multimedia :: Graphics",
        ],
    long_description = read("README"),
)