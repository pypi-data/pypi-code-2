#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie service."""
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

import sys
if sys.version_info < (3, 0):
    raise Exception("{0} Requires Python 3.0 or higher.".format(sys.argv[0]))
import os
import logging
from optparse import OptionParser
import pyzombie


###
### Functions
###

def resolvepath(path):
    """Fully resolve the given path into an absolute path taking into account,
    the user, variables, etc.
    """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path


### Parse the arguments
parser = OptionParser(
    description=__doc__,
    version='%%prog %s' % (__version__,),
    usage='usage: %prog [options]')

parser.add_option('', '--home',
    action='store', type='string', dest='home', default=None,
    help='Home directory to override $PYZOMBIEHOME.')
parser.add_option('', '--config',
    action='store', type='string', dest='config', default=None,
    help='Configuration file. Default: $PYZOMBIEHOME/etc/pyzombie.conf')
parser.add_option('', '--deamon',
    action='store_true', dest='deamon', default=False,
    help='Start pyzombie as a deamon under current user.')
parser.add_option('', '--verbose',
    action='store', type='string', dest='verbose', default='info',
    help='Change default logging verbosity: critical, error, warning, info, debug.')
                
options, args = parser.parse_args()


###
### Environment
###
if 'PYZOMBIEHOME' in os.environ:
    os.environ['PYZOMBIEHOME'] = os.environ['PYZOMBIEHOME']
else:
    if options.deamon:
        if os.environ['USER'] == 'root':
            os.environ['PYZOMBIEHOME'] = '/'
        else:
            os.environ['PYZOMBIEHOME'] = os.environ['HOME']
    else:
        os.environ['PYZOMBIEHOME'] = os.curdir

if not os.path.isdir(resolvepath(os.environ['PYZOMBIEHOME'])):
    print("""$PYZOMBIEHOME="{0[PYZOMBIEHOME]}" does not exist or is not a directory.""".format(os.environ), file=sys.stderr)
    sys.exit(1)

if not options.config:
    options.config = os.path.join(resolvepath(os.environ['PYZOMBIEHOME']), 'etc', 'pyzombie.conf')


###
### Setup logging configuration
###
loglevel = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}.get(options.verbose, logging.NOTSET)


### Start the zombie
try:
    zombie = pyzombie.ZombieServer(options.config, loglevel=loglevel)
    zombie.start()
except KeyboardInterrupt:
    print("User cancel.")

