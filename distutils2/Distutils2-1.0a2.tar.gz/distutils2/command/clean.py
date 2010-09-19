"""distutils.command.clean

Implements the Distutils 'clean' command."""

# contributed by Bastian Kleineidam <calvin@cs.uni-sb.de>, added 2000-03-18

__revision__ = "$Id: clean.py 70886 2009-03-31 20:50:59Z tarek.ziade $"

import os
from shutil import rmtree
from distutils2.core import Command
from distutils2 import log

class clean(Command):

    description = "clean up temporary files from 'build' command"
    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build.build-base')"),
        ('build-lib=', None,
         "build directory for all modules (default: 'build.build-lib')"),
        ('build-temp=', 't',
         "temporary build directory (default: 'build.build-temp')"),
        ('build-scripts=', None,
         "build directory for scripts (default: 'build.build-scripts')"),
        ('bdist-base=', None,
         "temporary directory for built distributions"),
        ('all', 'a',
         "remove all build output, not just temporary by-products")
    ]

    boolean_options = ['all']

    def initialize_options(self):
        self.build_base = None
        self.build_lib = None
        self.build_temp = None
        self.build_scripts = None
        self.bdist_base = None
        self.all = None

    def finalize_options(self):
        self.set_undefined_options('build', 'build_base', 'build_lib',
                                   'build_scripts', 'build_temp')
        self.set_undefined_options('bdist', 'bdist_base')

    def run(self):
        # remove the build/temp.<plat> directory (unless it's already
        # gone)
        if os.path.exists(self.build_temp):
            if self.dry_run:
                log.info('Removing %s' % self.build_temp)
            else:
                rmtree(self.build_temp)
        else:
            log.debug("'%s' does not exist -- can't clean it",
                      self.build_temp)

        if self.all:
            # remove build directories
            for directory in (self.build_lib,
                              self.bdist_base,
                              self.build_scripts):
                if os.path.exists(directory):
                    if self.dry_run:
                        log.info('Removing %s' % directory)
                    else:
                        rmtree(directory)
                else:
                    log.warn("'%s' does not exist -- can't clean it",
                             directory)

        # just for the heck of it, try to remove the base build directory:
        # we might have emptied it right now, but if not we don't care
        if not self.dry_run:
            try:
                os.rmdir(self.build_base)
                log.info("removing '%s'", self.build_base)
            except OSError:
                pass

# class clean
