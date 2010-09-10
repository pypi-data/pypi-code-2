#!/usr/bin/env python
from distutils.core import setup
import os
ginfo_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'kvigall', 'generalinformation.py')
execfile(ginfo_file) # Gives us a version and a version_text variables

readme = open('README.txt').read()
conf = dict(
    name='kvigall',
    version=version,
    author='Niels Serup',
    author_email='ns@metanohi.org',
    packages=['kvigall', 'kvigall.frontend', 'kvigall.external'],
    scripts=['scripts/kvigall'],
    requires=['qvikconfig', 'termcolor', 'htmlentitiesdecode'],
    url='http://metanohi.org/projects/kvigall/',
    license='GPLv3+',
    description='A customizable calendar program meant for use in terminals',
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: End Users/Desktop",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "License :: DFSG approved",
                 "Operating System :: OS Independent",
                 "Operating System :: POSIX",
                 "Operating System :: Unix",
                 "Programming Language :: Python",
                 "Topic :: Utilities"
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
