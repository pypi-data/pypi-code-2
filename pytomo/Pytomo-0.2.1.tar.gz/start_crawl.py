#!/usr/bin/env python
"""Global launcher for the pytomo package
"""

from os.path import abspath
from sys import path

# assumes the standard distribution paths
PACKAGE_NAME = 'pytomo'
PACKAGE_DIR = abspath(path[0])

if PACKAGE_DIR not in path:
    path.append(PACKAGE_DIR)

import pytomo

if __name__ == '__main__':
    pytomo.start_pytomo.main()

