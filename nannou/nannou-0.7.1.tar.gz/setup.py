import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "nannou",
    version = "0.7.1",
    author = "Niel Faccly",
    author_email = "nyufac@gmail.com",
    description = ("Compiling template engine based on "
                   "pattern matching"),
    license = "BSD",
    keywords = "python web templates",
    url = "http://packages.python.org/nannou",
    packages=['nannou',],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
