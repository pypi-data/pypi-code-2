#!/usr/bin/python
#
# File: setup.py
#
# This file is part of the biblio-py project
#
# License:
# 
# Copyright (C) 2009 Juan Fiol This is free software.
# 
# You may redistribute copies of it under the terms of the GNU General Public License
# version 2 or later.  There is NO WARRANTY, to the extent permitted by law.
#
# Written by Juan Fiol <juanfiol@gmail.com>
import os
import glob
from distutils.core import setup
# import distutils

VERSION= '0.5.6'
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES')
    + '\n'
    )

packages = ["yapbib","query_ads"]
scripts= glob.glob('scripts/*.py')

# do the distutils setup
setup(name="biblio-py",
      version = VERSION,
      description = "Package to manage bibliography files",
      long_description = long_description,
      license = "GPLv2",
      url = "http://fisica.cab.cnea.gov.ar/colisiones/staff/fiol/biblio-py.html",
      download_url="http://fisica.cab.cnea.gov.ar/colisiones/staff/fiol/files/biblio-py-%s.tar.gz"%(VERSION),
      keywords= "bibliography, bibtex, converter, html, xml, latex, parser",
      author = "Juan Fiol",
      author_email = "juanfiol@gmail.com",
      packages = packages,
      scripts = scripts,
      )

