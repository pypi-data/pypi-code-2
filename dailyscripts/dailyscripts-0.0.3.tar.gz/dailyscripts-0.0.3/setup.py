#!/usr/bin/env python 
try: 
    from setuptools import setup, find_packages 
except ImportError: 
    from ez_setup import use_setuptools 
    use_setuptools() 
    from setuptools import setup, find_packages 

setup( name = 'dailyscripts',
    version = '0.0.3',
    scripts = ['unpackall/unpackall', 'shuffle/shuffle'],

    zip_safe = True,


    #Metadata for PyPI
    url = 'http://github.com/spajus/dailyscripts/',
    author = 'Tomas Varaneckas',
    author_email = 'tomas.varaneckas@gmail.com',
    description = 'Daily Scripts. Utilities for every geek.',
    long_description = 'Daily Scripts. Utilities for every geek.',
    license = 'GPLv3',
    keywords = ['utils'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Archiving',
        'Topic :: Utilities'
    ],
)
