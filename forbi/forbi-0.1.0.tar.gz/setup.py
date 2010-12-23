#!/usr/bin/env python
from distutils.core import setup
import sys
import os
import fnmatch

basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, basedir)
import forbi.misc as misc

readme = open('README.txt').read()
conf = dict(
    name=misc.program_name,
    version=misc.version_num_text,
    description=misc.program_description,
    author=misc.program_author,
    author_email=misc.author_email,
    packages=['forbi', 'forbi.external'],
    scripts=['scripts/forbi', 'scripts/forbi-send'],
    requires=['M2Crypto', 'dbus', 'gobject', 'tk'],
    url='http://metanohi.org/projects/forbi/',
    license='AGPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Utilities'
        ]
)

try:
    # setup.py register wants unicode data..
    conf['long_description'] = readme.decode('utf-8')
    setup(**conf)
except Exception:
    # ..but setup.py sdist upload wants byte data
    conf['long_description'] = readme
    setup(**conf)
