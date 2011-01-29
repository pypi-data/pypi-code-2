#!/usr/bin/python

"""GUI to edit databases. Many backend supported (Postgres, Sqlite, MySql,...).
Based on python, GTK, sqlalchemy. It's split into a GUI and a very rich package to create
database interfaces
"""

classifiers = """\
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: MacOS
Operating System :: Microsoft
Operating System :: OS Independent
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Database :: Front-Ends
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Application Frameworks
Topic :: Software Development :: Libraries :: Python Modules"""

import os
import sys
try:
   from setuptools import setup, find_packages
except ImportError, e:
   from distribute_setup import use_setuptools
   use_setuptools()
   from setuptools import setup, find_packages
   
REQUIRES = []

f = open('sqlkit/__init__.py')
for line in f:
   if line.startswith('__version__'):
       version = line.split()[2].strip("'")

if sys.argv[1] == 'install':
   try:
      import pygtk
      pygtk.require('2.0')
   except ImportError:
      print "You need to install also pygtk and I was not able to work out"
      print "  a correct dependency in setup.py"
      sys.exit(1)

# setuptools really fails in understanding which packages are already installed
# pip is much better!
try:
   import sqlalchemy
except ImportError:
   REQUIRES = ['sqlalchemy >= 0.5', ]

try:
   import babel
except ImportError:
   REQUIRES += ['Babel']

try:
   import dateutil
except ImportError:
   REQUIRES += ['python-dateutil']

   
setup(name='sqlkit',
      version=version,
      description=__doc__,
      author='Alessandro Dentella',
      author_email='sandro@e-den.it',
      url='http://sqlkit.argolinux.org/',
      install_requires=REQUIRES,
      packages = find_packages('.'),
      scripts=['bin/sqledit'],
#      package_dir = {'' : 'sqlkit'},
#      package_data = {'sqlkit' : ['locale']},
      classifiers= classifiers.split('\n'),
      include_package_data=True,      
      zip_safe=False,
     )

