#!/usr/bin/python

import sys, os

__author__ = 'Luis Carlos Cruz <carlitos.kyo@gmail.com>'
__version__ = '0.1'

# Distutils version
METADATA = dict(
    name = "oauther",
    version = __version__,
    py_modules = ['setup',
                  'oauth/__init__',
                  'oauth/client',
                  'oauth/consumer',
                  'oauth/data',
                  'oauth/exceptions',
                  'oauth/request',
                  'oauth/signature',
                  'oauth/token',
                  'oauth/utils',],
    author = 'Luis C. Cruz',
    author_email = 'carlitos.kyo@gmail.com',
    description = 'An simple oauth base client.',
    long_description = open("README").read(),
    license = 'MIT License',
    url = 'http://github.com/carlitux/Python-OAuth-Client',
    keywords = 'oauth client',
)

# Setuptools version
SETUPTOOLS_METADATA = dict(
    install_requires = ['setuptools'],
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ]
)

def Main():
    try:
        import setuptools
        METADATA.update(SETUPTOOLS_METADATA)
        setuptools.setup(**METADATA)
    except ImportError:
        import distutils.core
        distutils.core.setup(**METADATA)

if __name__ == '__main__':
    Main()
