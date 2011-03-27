#!/usr/bin/env python

from distutils.core import setup

setup(name='Petapass',
      version='0.2.0',
      description='better passwords using hashes',
      author='Peter Fein',
      author_email='pfein@pobox.com',
      url='http://hg.wearpants.org/petapass',
      license = "BSD",
      packages=['petapass', ],
      scripts=['scripts/petapass', ],
      classifiers = ["Development Status :: 5 - Production/Stable",
                     "Environment :: Console",
                     "Environment :: X11 Applications :: GTK",
                     "Intended Audience :: End Users/Desktop",
                     "License :: OSI Approved :: BSD License",
                     "Topic :: Security",
                     ],
      long_description=open('README.rst').read(),
      )
