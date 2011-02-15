#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Environment:
    PYZOMBIEHOME
        pyzombie's home directory.
        Default: current working directory.
        Demon Mode: current user's home directory or empty if user is root.

Directories and Files:
    $PYZOMBIEHOME/etc/pyzombie.conf
        Configuration file.
    
    $PYZOMBIEHOME/var/run/pyzombie.pid
        File that contains the current pyzombie process id.
        
    $PYZOMBIEHOME/var/log/pyzombie
        Directory that contains pyzombie log files.
    
    $PYZOMBIEHOME/var/spool/pyzombie
        Directory that contains executions waiting to run.
    
    $PYZOMBIEHOME/tmp/pyzombie
        Directory to contain temporary files.

Configuration:
    [pyzombie]
        address     The server address or DNS name: default localhost.
        port        The TCP/IP port to listen: default 8008.
    
    [pyzombie_filesystem]
        var         The variable data root directory: default /var
    
    [loggers]       Python logging configuration section.
        Requires two named loggers: root and zombie.
    
    [handlers]      Python logging configuration section.
    
    [formatters]    Python logging configuration section.

License:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__version__ = '1.0.1'
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys
if sys.version_info < (3, 0):
    raise Exception("pyzombie requires Python 3.0 or higher.")

from .ZombieServer import *


