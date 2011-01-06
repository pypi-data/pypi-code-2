import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "buildboticon",
    version = "0.1.0",
    author = "Marcus Lindblom",
    author_email = "macke@yar.nu",
    description = ("A buildbot monitoring utility"),
    license = "GPL 3.0",
    keywords = "buildbot systemtray pyqt",

    url = "http://bitbucket.org/marcusl/buildboticon",
    download_url = "http://packages.python.org/buildboticon",

    package_dir = {'':'src'},
    packages=find_packages('src'),
    long_description=read('README'),

    entry_points = {
        'setuptools.installation': [
            'eggsecutable = bbicon.bbicon:main',
        ],
        'gui_scripts': [
            'buildboticon = bbicon.bbicon:main',
        ]
    },

# PyQt is not on PyPi
#    install_requires = ['PyQt >= 4.2'],

    zip_safe = True,

    extras_require = {
        'speech':  ["pyspeech>=1.2", "RXP"],
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Desktop Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
)