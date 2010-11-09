#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: strategymigrator.py 59863 2008-03-03 13:22:18Z glenfant $

"""%prog [options] SOURCEPATH DESTINATIONPATH

Migrates the storage strategy of a FSS repository in SOURCEPATH
to another strategy in DESTINATIONPATH.

* Purge your FSS storage area using the Plone control panel.
* Activate and re-generate the RDF files if not already done.
  (Before this, reset to standard RDF is a custom RDF is in use)
* Stop your Zope instance.
* Make sure your "umask" and current user/group will let Zope
  process read/write the files we will create in DESTINATIONPATH.
* Run this utility (use"--help" option to read all the doc).
  Note that the DESTINATIONPATH needs free space to hold all
  files of the SOURCEPATH.
* Change your "plone-filesystemstorage.conf" accordingly (RTFM).
* Start your Zope instance and test the content types associated
   with FSS.
* (Backup and) Remove the SOURCEPATH in case of successful tests.
"""

import optparse
import os
import sys
import shutil

__version__ = "1.0.0"
__author__ = "Gilles Lenfant <gilles.lenfant@ingeniweb.com>"

if sys.platform == 'win32':
    import win32file
    def availableSpace(path):
        """Pythonic 'df' in bytes"""

        S, BPS, FC, NC = win32file.GetDiskFreeSpace(path)
        return (long(NC)*long(S)*long(BPS)) / (1024*1024)
else:
    # Unix (Linux, BSD, MacOSX, ...)
    import statvfs
    def availableSpace(path):
        """Pythonic 'df' in bytes"""

        infos = os.statvfs(path)
        free_blocks = infos[statvfs.F_BAVAIL]
        block_size = infos[statvfs.F_FRSIZE]
        return free_blocks * block_size


def usedSpace(path):
    """Pythonic 'du' in bytes"""

    if sys.platform == 'win32':
        # File system supposed to be FAT32 or NTFS
        block_size = 4096
    else:
        # Unix (Linux, BSD, MacOSX, ...)
        infos = os.statvfs(path)
        block_size = infos[statvfs.F_FRSIZE]
    total = 0
    for root, dirs, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            fsize = os.path.getsize(filepath)
            fsize = ((fsize/block_size) + 1) * block_size # Real size on disk
            total += fsize
    return total


class BaseMigrator(object):
    """Base for all FSS migrators"""

    # These 2 attributes mus be provided by subclasses
    _source_strategy = None
    _destination_strategy = None

    def __init__(self, options, sourcepath, destpath, loginfo):
        """Migrator constructor
        @param options: options as provided by an optparse.OptionParser obj
        @param sourcepath: path to the original FSS storage
        @param destpath: path to the destination FSS storage
        @param loginfo: callable that logs messages
        """

        self.options = options
        self.sourcepath = sourcepath
        self.destpath = destpath
        self.loginfo = loginfo
        return


    def run(self):
        """Execution of migration must be provided by subclasses"""

        raise NotImplementedError


class FlatToDirectoryMigrator(BaseMigrator):
    """storage-strategy flat -> directory"""

    _source_strategy = 'flat'
    _destination_strategy = 'directory'

    def run(self):
        """Go baby, go..."""

        self.loginfo(
            1, "Transforming FSS flat storage in %s into directory storage in %s"
            % (self.sourcepath, self.destpath))
        for filename in os.listdir(self.sourcepath):
            self.loginfo(2, "Processing source file '%s'" % filename)
            dir1 = filename[:2]
            dir2 = filename[:4]
            file_destdir = os.path.join(self.destpath, dir1, dir2)
            if not os.path.isdir(file_destdir):
                self.loginfo(2, "Creating '%s' directory" % file_destdir)
                os.makedirs(file_destdir)
            self.loginfo(2, "Copying '%s' to %s" % (filename, file_destdir))
            file_sourcepath = os.path.join(self.sourcepath, filename)
            shutil.copy(file_sourcepath, file_destdir)
            if self.options.remove_source:
                self.loginfo(2, "Deleting original '%s'" % filename)
                os.remove(file_sourcepath)
        self.loginfo(1, "Done")
        return


class DirectoryToFlatMigrator(BaseMigrator):
    """storage-strategy directory -> flat"""

    _source_strategy = 'directory'
    _destination_strategy = 'flat'

    def run(self):
        """Let's go"""

        self.loginfo(
            1, "Transforming FSS directory storage in %s into flat storage in %s"
            % (self.sourcepath, self.destpath))
        for root, dirnames, filenames in os.walk(self.sourcepath):
            for filename in filenames:
                self.loginfo(2, "Processing source file '%s'" % filename)
                file_sourcepath = os.path.join(root, filename)
                shutil.copy(file_sourcepath, self.destpath)
                if self.options.remove_source:
                    self.loginfo(2, "Deleting original '%s'" % filename)
                    os.remove(file_sourcepath)
        self.loginfo(1, "Done")
        return


_migrator_classes = (FlatToDirectoryMigrator, DirectoryToFlatMigrator)


def allStrategies():
    """Set of all known strategies"""

    out = set()
    for klass in _migrator_classes:
        out |= set([klass._source_strategy, klass._destination_strategy])
    return out


def findMigrator(source_strat, dest_strat):
    """Finds the appropriate migrator class or None"""

    for klass in _migrator_classes:
        if (klass._source_strategy, klass._destination_strategy) == (source_strat, dest_strat):
            return klass
    return None


def availableMigrations():
     """For UI and documentation"""

     out = "\nAvailable startegy migrations:"
     for klass in _migrator_classes:
         out += ("\n* --source-strategy=%s --destination-strategy=%s"
                 % (klass._source_strategy, klass._destination_strategy))
     return out


class Application(object):
    """Shell application"""

    def __init__(self):
        """Getting and validating args and options"""

        parser = optparse.OptionParser(usage=__doc__ + availableMigrations(),
                                       version=__version__)
        parser.add_option(
            '-v', '--verbose', action='count', dest='verbosity', default=0,
            help="Add output verbosity for each -v.")
        parser.add_option(
            '-s', '--source-strategy', action='store', type='string', dest='source_strategy', default='flat', metavar='STRATEGY',
            help=("The FSS strategy used in SOURCEPATH, "
                  "one of '%s'. Default: '%%default'."
                  % "', '".join(allStrategies())))
        parser.add_option(
            '-d', '--destination-strategy', action='store', type='string', dest='destination_strategy', default='directory', metavar='STRATEGY',
            help=("The FSS strategy used in DESTINATIONPATH, "
                  "one of '%s'. Default: '%%default'."
                  % "', '".join(allStrategies())))
        parser.add_option(
            '-r', '--remove-source', action='store_true', dest='remove_source', default=False,
            help=("Remove source files successfully migrated "
                  "(Make a backup of SOURCEPATH before using this option). "
                  "Default: %default."))
        self.options, paths = parser.parse_args()

        # Controlling arguments validity
        if len(paths) != 2:
            parser.print_help()
            print "Error: SOURCEPATH and DESTINATIONPATH are required arguments."
            sys.exit(2)
        self.sourcepath, self.destpath = paths
        if not os.path.isdir(self.sourcepath):
            parser.print_help()
            print "Error: SOURCEPATH is not an existing directory."
            sys.exit(2)
        if not os.path.isdir(self.destpath):
            parser.print_help()
            print "Error: DESTINATIONPATH is not an existing directory."
            sys.exit(2)
        if len(os.listdir(self.destpath)) > 0:
            parser.print_help()
            print "Error: DESTINATIONPATH is not empty."
            sys.exit(2)

        # Finding and validating migrator
        migrator = findMigrator(self.options.source_strategy, self.options.destination_strategy)
        if migrator is None:
            parser.print_help()
            print "Error: This strategy migration is not available."
            sys.exit(2)
        self.migrator = migrator

        # Checking available space
        if not self.options.remove_source:
            used = usedSpace(self.sourcepath)
            if availableSpace(self.destpath) < used:
                print ("Error: there is not enough free space in '%s'. "
                       "You need %d free bytes in the destination path, "
                       "or consider making a backup and use the "
                       "'--remove-source' option." % (self.destpath, used))
                sys.exit(2)
            else:
                self.loginfo(
                    1,
                    ("Migration will take approximately %d bytes "
                     "in %s" % (used, self.destpath)))
        return


    def run(self):
        """Let's do the job"""

        migrator = self.migrator(self.options, self.sourcepath, self.destpath, self.loginfo)
        migrator.run()
        return


    def loginfo(self, level, message):
        """Prints the message from the verbosity level"""

        if self.options.verbosity >= level:
            print message
        return


if __name__ == '__main__':
    Application().run()
