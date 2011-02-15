#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server configuration."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
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
__docformat__ = "reStructuredText en"

__all__ = []

import sys
import os
import io
import time
import threading
import configparser
from datetime import datetime
from datetime import timedelta
import logging
import logging.config

###
### Initial Configuration
###
CONFIG_INIT = """
[pyzombie]
address:        localhost
port:           8008
maxage_dynamic: 3600
maxage_static:  604800

[pyzombie_filesystem]
execbase:   zombie
binary:     image
instance:   run

var=./build/var
log:        %(var)s/log/pyzombie
run:        %(var)s/run/pyzombie.pid
data:       %(var)s/data/pyzombie
cache:      %(var)s/cache/pyzombie
spool:      %(var)s/spool/pyzombie

[loggers]
keys=root,zombie

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_zombie]
level=DEBUG
handlers=consoleHandler
qualname=zombie
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s %(levelname)s %(message)s
datefmt=
"""


###
### Global configuration
###
config = configparser.SafeConfigParser()
config.readfp(io.StringIO(CONFIG_INIT))

def datadir():
    ret = config.get("pyzombie_filesystem", "data")
    if ret.startswith('.'):
        ret = os.path.join(os.getcwd(), ret)
    ret = os.path.normpath(ret)
    if not os.path.isdir(ret):
        os.makedirs(ret)
    return ret


