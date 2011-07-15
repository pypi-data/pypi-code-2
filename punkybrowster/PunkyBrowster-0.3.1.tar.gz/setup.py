"""Punky requires PyQt. How you obtain the PyQt binaries depends on your
platform:

- Mac: Build the binaries yourself (good luck), or find a package installer
- Linux: Use a package manager, such as apt (apt-get install python-qt4)
- Windows: Use the binary installer from Riverbank
  (http://www.riverbankcomputing.co.uk/software/pyqt/download)

"""
import re

from setuptools import setup


# Get __version__, (w/wout spaces, single/doublequoted, w/wout hotfix number).
init = file('./punky/__init__.py').read()
version = re.search(r"__version__ ?= ?(?:'|\")(\d+\.\d+(?:\.\d+)?)(?:'|\")",
                    init)
assert version


setup(
    name="PunkyBrowster",
    version=version.group(1),
    description="Programmatic web browsing module",
    author="Leapfrog Direct Response LLC",
    url="http://bitbucket.org/leapfrogdevelopment/punkybrowster/",
    packages=[
        "punky",
    ],
    tests_require=[
        "nose>=0.11.4",
        "PIL>=1.1.6",
    ],
    test_suite='t.test',
    scripts=[],
    license="GNU Public License v3.0",
    long_description="""\
PunkyBrowster is a programmatic browser with a synchronous API. It is a fork of
the spynner project. We remove unessential stuff like URL filtering, download
handling, and cookie emulation. We also remove some potentially harmful stuff
like JavaScript injection. What's left is a fairly lean core of functionality,
and on top of that we add some extra support for DOM queries and mouse click
emulation.""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
