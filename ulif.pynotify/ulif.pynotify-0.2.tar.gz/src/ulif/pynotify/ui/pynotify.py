##
## pynotify.py
## Login : <uli@pu.smp.net>
## Started on  Fri Jul 30 15:50:54 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Watch changes in filesystem. UI components.
"""
import os
import pkg_resources
import sys
from optparse import OptionParser
from ulif.pynotify.base import FSWalker, ADDED, MODIFIED, DELETED
from ulif.pynotify.sqlite import SQLiteFSWalker

VERSION = pkg_resources.get_distribution('ulif.pynotify').version

HELP_TIMESTAMP = """list files changed since `TIMESTAMP'.

The timestamp is a number representing seconds passed since Jan, 1st
1970. Default is zero which on most systems will mean: list all
files found. If you specify `--sqlite' no timestamp is needed.
"""

HELP_SQLITE = """Use an SQLite database to store scan results.

By default files are considered modified if their timestamp is newer
than the timestamp given. Using `--sqlite' scan results are stored in
an SQLite database whose path you can set with `--dbpath'.
"""

HELP_DBPATH = """Use file in DBPATH to store scan results.

This option is only active if you choose also some database backend
(sqlite for instance). 'pynotify.db' by default.
"""
def get_options(argv=None):
    """Get and evaluate options for pynotify cmdline script.

    Returns a tuple (`options`, `args`) containing the options
    actually set.
    """
    if argv is None: argv = sys.argv[1:]
    usage = "usage: pynotify [options] [FILE-OR-DIRECTORY]"
    parser = OptionParser(version="pynotify %s" % VERSION, usage=usage)
    parser.add_option(
        "-c", "--config", dest="conffile",
        help="read configuration from CONFFILE")
    parser.add_option(
        "-s", "--sqlite", action="store_true",
        help = HELP_SQLITE,
        )
    parser.add_option(
        "-t", "--timestamp", default=0, type="float",
        help=HELP_TIMESTAMP,
        )
    parser.add_option(
        "-l", "--loggername", default='ulif.pynotify',
        help="use `LOGGERNAME' for logging.")
    parser.add_option(
        "--dbpath", default='pynotify.db',
        help=HELP_DBPATH,
        )
    (options, args) = parser.parse_args(argv)
    if len(args) != 1 and options.conffile is None:
        parser.error("Need at least directory to scan for changes")
    if len(args) == 1:
        if not os.path.exists(args[0]):
            parser.error("No such file or directory: %s" % args[0])
    return (options, args)

def main(argv=None):
    """The main commandline script.
    """
    if argv is None: argv = sys.argv[1:]
    (options, args) = get_options(argv)
    walker = FSWalker()
    if options.sqlite:
        walker = SQLiteFSWalker(options.dbpath)
        for change in walker.walk(args[0]):
            if change.changetype == ADDED:
                print "A",
            elif change.changetype == MODIFIED:
                print "M",
            elif change.changetype == DELETED:
                print "D",
            print change.path
    else:
        for change in walker.walk(args[0], options.timestamp):
            print change.path
    return
