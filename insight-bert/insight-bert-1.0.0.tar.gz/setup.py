#!/usr/bin/env python

from distutils.core import setup

__version__ = '1.0.0'

setup(
    name = 'insight-bert',
    version = __version__,
    description = 'BERT Serialization Library',
    author = 'Samuel Stauffer',
    author_email = 'samuel@lefora.com',
    maintainer='Jordan Bach',
    maintainer_email='jordanbach@gmail.com',
    url = 'https://github.com/jbgo/python-bert/tree/insight-bert',
    packages = ['bert'],
    install_requires = ["erlastic"],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
