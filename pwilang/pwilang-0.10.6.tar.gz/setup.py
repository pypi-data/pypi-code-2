import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pwilang",
    version = "0.10.6",
    author = "Christophe Eymard",
    author_email = "christophe@ravelsoft.com",
    description = ("A text processor with its own syntax a little nicer than html that uses jinja for complex text rendering."),
    license = "GPLv3",
    keywords = "text processor html jinja",
    url = "http://code.google.com/p/pwilang/",
    packages=['pwilang'],
    scripts=["pwilang/pwilang"],
    long_description=read('README'),
    install_requires=['jinja2>=2.4', 'ply>=3.1', 'beautifulsoup'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
)

