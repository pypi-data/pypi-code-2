"""
$Id: __init__.py 3418 2010-04-07 21:17:20Z dglick $
"""

import os, sys
from App.Common import package_home

import _patch

pkg_home = package_home( globals() )
lib_path = os.path.join( pkg_home, 'lib' )
if os.path.exists( lib_path ):
    sys.path.append( lib_path )
import catalog
import permissions
