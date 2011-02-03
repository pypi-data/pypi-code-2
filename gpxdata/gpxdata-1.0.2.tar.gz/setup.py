#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='gpxdata',
      version='1.0.2',
      description='Object-Oriented representation of GPX documents and conversion utilities between GPX, KML and OVL',
      author='Frank Pählke',
      author_email='frank@kette-links.de',
      url='http://www.kette-links.de/technik/',
      download_url='http:://www.kette-links.de/technik/gpxdata-1.0.2.tar.gz',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: GIS',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
      py_modules=['gpxdata'],
      scripts=['gpx2kml.py','gpx2ovl.py','kml2gpx.py','kml2ovl.py','ovl2gpx.py','ovl2kml.py'],
      requires=['mx.DateTime']
     )
