#!/usr/bin/env python3

from distutils.core import setup
from desurveil.misc import program as p

setup(
    name=p.name,
    version=p.version.text,
    author=p.author,
    author_email=p.author_email,
    url=p.url,
    description=p.description,
    long_description=open('README.txt').read(),
    license=p.short_license_name,
    packages=['desurveil'],
    scripts=['scripts/desurveil'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'License :: DFSG approved',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Topic :: Utilities',
                 'Topic :: Scientific/Engineering :: Mathematics',
                 'Topic :: Security :: Cryptography',
                 'Topic :: Education',
                 'Topic :: Software Development :: Libraries :: Python Modules'
                 ])
