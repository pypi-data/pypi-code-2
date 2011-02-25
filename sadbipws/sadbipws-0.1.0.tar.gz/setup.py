#!/usr/bin/env python3
from distutils.core import setup

conf = dict(
    name='sadbipws',
    version='0.1.0',
    author='Niels Serup',
    author_email='ns@metanohi.org',
    package_dir={'': '.'},
    py_modules = ['sadbipws'],
    url='http://metanohi.org/projects/sadbipws/',
    license='COPYING.txt',
    description='An implementation of the SADBIPWS serializer',
    long_description=open('README.txt').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Utilities',
                 'Environment :: Console',
                 'License :: DFSG approved',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python'
                 ]
)

setup(**conf)
