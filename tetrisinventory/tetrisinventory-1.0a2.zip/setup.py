#!/usr/bin/env python

from distutils.core import setup

setup(
    name='tetrisinventory',
    version='1.0a2',
    description=u'Diablo\u00AE-style "tetris inventory"',
    author='Devin Jeanpierre',
    author_email='jeanpierreda@gmail.com',
    url='http://bitbucket.org/devin.jeanpierre/tetris-inventory',
    packages=['tetrisinventory', 'tetrisinventory.test'],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
