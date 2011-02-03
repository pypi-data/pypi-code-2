# -*- coding: utf-8 -*-
"""
MataNui is intending to provide a data serving platform for the Grid that
can replicate between various sites, store/query arbitrary amounts of
meta-data, and is interfaced with a RESTful web service. The concept also
allows for an alternative server front end using the Griffin GridFTP server.
The concept is (initially) based on storing all data/meta-data in the GridFS
mode of the MongoDB NoSQL database. This code consists of a WSGI based
RESTful web service that interfaces directly with the MongoDB, and can be
used together with Apache and mod_wsgi.

The MataNui project is resulting from the ambitions of the New Zealand
BeSTGRID project (https://bestgrid.org/) to provide a reliable and easy to
use "Data Fabric" for the Globus Toolkit based Grid. The implementation is
also aligned with the ambitions of the Australian Research Collaboration
Service ARCS (http://www.arcs.org.au/).

The project has been outlines at the New Zealand eResearch Symposium 2010 in
Auckland on this poster:

http://www.slideshare.net/XEmacs/huge-matanui-building-a-grid-data-infrastructure-that-doesnt-suck

Some external resources used together with this project.

 * MongoDB data base: http://www.mongodb.org/

 * Apache WSGI module: https://code.google.com/p/modwsgi/

 * Griffin GridFTP server (alternative data access service front end):

 * https://projects.arcs.org.au/trac/griffin

 * User end data management GUI application DataFinder:

   * https://wiki.sistec.dlr.de/DataFinderOpenSource

   * https://launchpad.net/datafinder/

The project is hosted on Launchpad.net: http://launchpad.net/matanui
"""

## Created: 2010-09-04 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'
__versioninfo__ = (0, 1, 0)
__version__ = '.'.join(map(str, __versioninfo__)) # pylint: disable=W0141

API_VERSION = '0.1'
