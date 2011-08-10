import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Spike Count Models",
    version = "0.1",
    author = "Arno Onken",
    author_email = "aonken@cs.tu-berlin.de",
    description = ("This package provides a multitude of statistical tests, copulas and marginal distribution with functions for fitting data, calculating likelihoods and generate samples... Its intended purpose was modeling spike counts, but it can be used for other tasks."),
    license = "GNU",
    keywords = "copula distributions statistical modelling tests marginals maximum likelihood spike computational neuroscience",
    packages=['spikecountmodels'],
    classifiers=[
        "Development Status :: 5 - Production/Stable ",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 2.6",
        "Topic :: Scientific/Engineering",
    ],
)
