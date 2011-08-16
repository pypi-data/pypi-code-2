#!/usr/bin/env python

sdict = dict(
    name = 'django-crypto',
    packages = ['django_crypto'],
    version = '0.2.0',
    description = 'Simple 2-way crypto functions for use with Django.',
    long_description = 'Simple 2-way crypto functions for use with Django.',
    url = 'http://github.com/votizen/django-crypto',
    author = 'Matt Snider',
    author_email = 'msnider@votizen.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'msnider@votizen.com',
    keywords = ['cryptography', 'django'],
    license = 'MIT',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

from distutils.core import setup
setup(**sdict)