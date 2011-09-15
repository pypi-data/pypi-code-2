import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="simple-gae-memoize",
    version="0.0.2",
    author="Cesar Canassa",
    author_email="cesar.canassa@gmail.com",
    description="A decorator to memoize App Engine functions using the memcache",
    license="BSD",
    keywords="gae memcache memoize",
    url="http://packages.python.org/simple_gae_memoize",
    packages=['memoize'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)