#!/usr/bin/env python
from distutils.core import setup
import os
import fnmatch

ginfo_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'shadowloss', 'generalinformation.py')
execfile(ginfo_file)

data = []
datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
pref = len(datadir) + 1
for x in os.walk(datadir):
    files = []
    for y in x[2]:
        fn = os.path.join(x[0], y)
        if not fnmatch.fnmatch(fn, '*~') and \
                not fnmatch.fnmatch(fn, '#*#'):
            files.append(fn)
    data.append((os.path.join(global_data_dir, x[0][pref:]),
                 files))

readme = open('README.txt').read()
conf = dict(
    name=program_name,
    version=version_text,
    author='Niels Serup',
    author_email='ns@metanohi.org',
    packages=['shadowloss', 'shadowloss.builtinstickfigures', 'shadowloss.external'],
    scripts=['scripts/shadowloss'],
    data_files=data,
    requires=['qvikconfig'],
    url='http://metanohi.org/projects/shadowloss/',
    license='GPLv3+',
    description=program_description,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'License :: DFSG approved',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Games/Entertainment :: Arcade',
                 'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games'
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
