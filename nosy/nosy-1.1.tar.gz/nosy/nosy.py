#!/usr/bin/env python
"""Watch for changes in a collection of source files. If changes, run
nosetests.
"""
from __future__ import absolute_import
import glob
import os
import stat
import subprocess
import sys
import time
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError
from optparse import OptionParser
import nose


class Nosy(object):
    """Watch for changes in all source files. If changes, run nosetests.
    """
    
    def __init__(self):
        """Return an instance with the default configuration, and a
        command line parser.
        """
        self.config = SafeConfigParser()
        self.config.add_section('nosy')
        self.config.set('nosy', 'base_path', '.')
        self.config.set('nosy', 'glob_patterns', '')
        self.config.set('nosy', 'exclude_patterns', '')
        self.config.set('nosy', 'extra_paths', '')
        self.config.set('nosy', 'options',  '')
        self.config.set('nosy', 'tests', '')
        # paths config retained for backward compatibility; use
        # extra_paths for any files or paths that aren't easily
        # included via base_path, glob_patterns, and exclude_patterns
        self.config.set('nosy', 'paths', '*.py')
        self._build_cmdline_parser()


    def _build_cmdline_parser(self):
        description = 'Automatically run nose whenever source files change.'
        self._opt_parser = OptionParser(description=description)
        defaults = dict(config_file='setup.cfg')
        self._opt_parser.set_defaults(**defaults)
        self._opt_parser.add_option(
            '-c', '--config', action='store', dest='config_file',
            help='configuration file path and name; '
                 'defaults to %(config_file)s' % defaults)


    def parse_cmdline(self):
        """Parse the command line and set the config_file attribute.
        """
        options, args = self._opt_parser.parse_args()
        if len(args) > 0:
            self._opt_parser.error('no arguments allowed')
        self.config_file = options.config_file


    def _read_config(self):
        if self.config_file:
            try:
                self.config.readfp(open(self.config_file, 'r'))
            except IOError, msg:
                self._opt_parser.error("can't read config file:\n %(msg)s"
                                       % locals())
        try:
            self.base_path = self.config.get('nosy', 'base_path')
            self.glob_patterns = self.config.get(
                'nosy', 'glob_patterns').split()
            self.exclude_patterns = self.config.get(
                'nosy', 'exclude_patterns').split()
            self.extra_paths = self.config.get('nosy', 'extra_paths').split()
            self.nose_opts = self.config.get('nosy', 'options')
            self.nose_args = self.config.get('nosy', 'tests')
            # paths config retained for backward compatibility; use
            # extra_paths for any files or paths that aren't easily
            # included via base_path, glob_patterns, and
            # exclude_patterns
            self.paths = self.config.get('nosy', 'paths').split()
        except NoSectionError:
            self._opt_parser.error("nosy section not found in config file")
            sys.exit(1)
        except NoOptionError:
            # Use default(s) from __init__()
            pass


    def _checksum(self):
        """Return a long which can be used to know if any files in the
        paths list have changed.
        """
        val = 0
        for path in self.extra_paths + self.paths:
            for f in glob.iglob(path):
                stats = os.stat(f)
                val += stats[stat.ST_SIZE] + stats[stat.ST_MTIME]
        for root, dirs, files in os.walk(self.base_path):
            for dir in dirs:
                exclusions = set()
                for p1 in self.exclude_patterns:
                    for f in glob.iglob(os.path.join(root, dir, p1)):
                        exclusions.add(f)
                    for p2 in self.glob_patterns:
                        for f in glob.iglob(os.path.join(root, dir, p2)):
                            if f not in exclusions:
                                stats = os.stat(f)
                                val += (stats[stat.ST_SIZE]
                                        + stats[stat.ST_MTIME])
        return val


    def run(self):
        """Run nose whenever the source files (default ./*.py) change.

        Re-read the configuration before each nose run so that options
        and aruments may be changed.
        """
        val = 0
        self._read_config()
        while True:
            if self._checksum() != val:
                self._read_config()
                val = self._checksum()
                subprocess.call(
                    ['nosetests']
                    + self.nose_opts.replace('\\\n', '').split()
                    + self.nose_args.replace('\\\n', '').split())
            time.sleep(1)


def main():
    nosy = Nosy()
    nosy.parse_cmdline()
    try:
        nosy.run()
    except KeyboardInterrupt:
        sys.exit(130)
    except SystemExit:
        sys.exit(0)


if __name__ == '__main__':
    main()
