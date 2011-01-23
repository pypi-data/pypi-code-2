#!/usr/bin/env python
from distutils.core import setup
import os.path
import tempfile

selfdir = os.path.dirname(os.path.realpath(__file__))

readme = open('README.txt').read()
conf = dict(
    name='dotbox',
    version='0.1.0',
    author='Niels Serup',
    author_email='ns@metanohi.org',
    package_dir={'': '.'},
    py_modules = ['dotbox'],
    url='http://metanohi.org/projects/dotbox/',
    license='COPYING.txt',
    description='A mini library for block-based games',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'Topic :: Multimedia :: Graphics',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Software Development :: Libraries :: pygame',
                 'Environment :: X11 Applications',
                 'License :: DFSG approved',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python'
                 ],
    requires=['pygame']
)

try:
    # setup.py register wants unicode data..
    conf['long_description'] = readme.decode('utf-8')
    setup(**conf)
except Exception:
    # ..but setup.py sdist upload wants byte data
    conf['long_description'] = readme
    setup(**conf)
