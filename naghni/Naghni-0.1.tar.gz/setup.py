#!/usr/bin/env python
from distutils.core import setup
import os
ginfo_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'naghni', 'generalinformation.py')
execfile(ginfo_file) # Gives us a version and a version_text variables

data = []
for x in os.walk(os.path.join(os.path.dirname(__file__), 'data')):
    data.append((os.path.join('/usr/local/share/naghni/', x[0]),
                 [os.path.join(x[0], y) for y in x[2]]))

readme = open('README.txt').read()
conf = dict(
    name='Naghni',
    version=version,
    author='Niels Serup',
    author_email='ns@metanohi.org',
    packages=['naghni', 'naghni.backend', 'naghni.object', 'naghni.external'],
    scripts=['scripts/naghni'],
    data_files=data,
    url='http://metanohi.org/projects/naghni/',
    license=open('GPLv3.txt').read(),
    description='A breath-taking side-scroller focusing on round lifeforms',
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: End Users/Desktop",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "License :: DFSG approved",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Topic :: Games/Entertainment :: Arcade",
                 "Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games"
                 ],
    requires=['pygame', 'pycairo', 'rsvg', 'numpy']
)

try:
    # setup.py register wants unicode data..
    conf['long_description'] = readme.decode('utf-8')
    setup(**conf)
except Exception:
    # ..but setup.py sdist upload wants byte data
    conf['long_description'] = readme
    setup(**conf)
