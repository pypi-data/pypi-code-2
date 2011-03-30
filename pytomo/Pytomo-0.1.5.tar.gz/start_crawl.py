#!/usr/bin/env python
"""Global launcher for the pytomo package
"""

from os.path import abspath, sep
from sys import path

# assumes the standard distribution paths
PACKAGE_NAME = 'pytomo'
PACKAGE_DIR = abspath(path[0])
PACKAGE_SOURCES = sep.join((PACKAGE_DIR, PACKAGE_NAME))

if PACKAGE_DIR not in path:
    path.append(PACKAGE_DIR)
if PACKAGE_SOURCES not in path:
    path.append(PACKAGE_SOURCES)

import pytomo.start_pytomo

pytomo.start_pytomo.main()

