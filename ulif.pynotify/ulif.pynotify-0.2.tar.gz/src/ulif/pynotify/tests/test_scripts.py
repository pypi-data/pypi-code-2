##
## test_scripts.py
## Login : <uli@pu.smp.net>
## Started on  Sun Aug  1 16:39:37 2010 Uli Fouquet
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
"""Tests for the commandline scripts delivered with `ulif.pynotify`.
"""
import doctest
import os
import shutil
import sys
import tempfile
import unittest
from StringIO import StringIO
from ulif.pynotify.tests.test_base import TestBase
from ulif.pynotify.ui.pynotify import main

def run_main(argv):
    """Run main script and catch output.
    """
    output = None
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    try:
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        main(argv=argv)
    except:
        pass
    finally:
        output = sys.stdout.getvalue() + sys.stderr.getvalue()
        sys.stdout = save_stdout
        sys.stderr = save_stderr
    return output
    
class TestPyNotifyScript(TestBase):
    
    def test_no_arg(self):
        """
           >>> print run_main([])
           Usage: pynotify [options] [FILE-OR-DIRECTORY]
           <BLANKLINE>
           ...: error: Need at least directory to scan for changes
        """
        return

    def test_not_a_file_or_directory(self):
        """
           >>> print run_main(['not-existent-file'])
           Usage: pynotify [options] [FILE-OR-DIRECTORY]
           <BLANKLINE>
           ...: error: No such file or directory: not-existent-file
        """
        return

    def test_help(self):
        """
           >>> print run_main(['--help'])
           Usage: pynotify [options] [FILE-OR-DIRECTORY]
           <BLANKLINE>
           Options:
             --version             show program's version number and exit
             -h, --help            show this help message and exit
             -c CONFFILE, --config=CONFFILE
                                   read configuration from CONFFILE
             -s, --sqlite          Use an SQLite database to store scan
                                   results.  By default files are
                                   considered modified if their
                                   timestamp is newer than the
                                   timestamp given. Using `--sqlite'
                                   scan results are stored in an
                                   SQLite database whose path you can
                                   set with `--dbpath'.
             -t TIMESTAMP, --timestamp=TIMESTAMP
                                   list files changed since
                                   `TIMESTAMP'.  The timestamp is a
                                   number representing seconds passed
                                   since Jan, 1st 1970. Default is
                                   zero which on most systems will
                                   mean: list all files found. If you
                                   specify `--sqlite' no timestamp is
                                   needed.
             -l LOGGERNAME, --loggername=LOGGERNAME
                                   use `LOGGERNAME' for logging.
             --dbpath=DBPATH       Use file in DBPATH to store scan results.
                                   This option is only active if you choose
                                   also some database backend (sqlite for
                                   instance). 'pynotify.db' by default.
        """

    def test_simple_file(self):
        """
           >>> tmpdir = tempfile.mkdtemp()
           >>> samplefile = os.path.join(tmpdir, 'samplefile')
           >>> open(samplefile, 'wb').write('foo')
           >>> print run_main([samplefile])
           /.../samplefile
           
           >>> shutil.rmtree(tmpdir)
        """

    def test_broken_links(self):
        if sys.platform.startswith('win'):
            # No symlinks on Win32
            return
        # Create a broken symlink...
        src = os.path.join(self.workdir, 'source')
        dst = os.path.join(self.workdir, 'dest')
        os.symlink(src, dst)
        output = run_main([self.workdir])
        # Should give False, but no abort.
        self.assertFalse(src in output)
        return

    def test_sqlite_add(self):
        output = run_main(['-s', self.workdir])
        output = output.replace(self.workdir, '')
        self.assertTrue('A /sampletree/treesample' in output)
        return

    def test_sqlite_modify(self):
        run_main(['-s', self.workdir])
        mtime = os.stat(self.treesamplefile).st_mtime + 0.1
        os.utime(self.treesamplefile, (mtime, mtime))
        output = run_main(['-s', self.workdir])
        output = output.replace(self.workdir, '')
        self.assertTrue('M /sampletree/treesample' in output)
        return

    def test_sqlite_delete(self):
        dbarg = '--dbpath=%s' % self.dbpath
        run_main(['-s', dbarg, self.workdir])
        output = run_main(['-s', self.workdir])
        output = output.replace(self.workdir, '')
        self.assertTrue('A /sampletree/treesample' in output)
        os.unlink(self.treesamplefile)
        output = run_main(['-s', dbarg, self.workdir])
        output = output.replace(self.workdir, '')
        self.assertTrue('D /sampletree/treesample' in output)
        return

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocTestSuite(
                optionflags = (
                    doctest.NORMALIZE_WHITESPACE
                    + doctest.ELLIPSIS
                    + doctest.REPORT_NDIFF
                    ),
                ),
            
            unittest.makeSuite(TestPyNotifyScript),
         ))
    return suite

