#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Renames files using regular expression matching."""

# This utility should be used whenever possible so we'll try to keep
# Python 2.4 compatibility. Horrible, isn't it?

import os
import re
import sys


MATCH_REGEX = re.compile(r'(\\)(\d+)')
MATCH_REGEX_BRACKETS = re.compile(r'(\\\()(\d+)(\))')


class Renamer(object):
    def __init__(self, test=False):
        self.test = test
        self.targets = {}

    def _apply_match(self, match, target):
        move_to = target
        for prefix, num in MATCH_REGEX.findall(target):
            move_to = move_to.replace(prefix+num, match.group(int(num)))
        for prefix, num, suffix in MATCH_REGEX_BRACKETS.findall(target):
            move_to = move_to.replace(prefix+num+suffix, match.group(int(num)))
        return move_to

    def _process_single(self, entry, match, target):
        if not match:
            return
        move_to = self._apply_match(match, target)
        self.targets.setdefault(move_to, []).append(entry)

    def rename(self, regex, target):
        r = re.compile("^%s$" % regex)
        for entry in os.listdir('.'):
            m = r.search(entry)
            self._process_single(entry, m, target)
        # sanity check
        for target, sources in self.targets.iteritems():
            if len(sources) > 1:
                print >>sys.stderr, ("rename error: multiple files (%s) would "
                                     "be written to %s") % (", ".join(sources),
                                                            target)
                return 1
            if os.path.exists(target):
                print >>sys.stderr, ("rename error: target %s already exists "
                                     "for source %s") % (target, sources[0])
                return 2
        # actual rename
        for target, sources in self.targets.iteritems():
            if self.test:
                print "Would run os.rename(%s, %s)" % (sources[0], target)
            else:
                os.rename(sources[0], target)
        return 0


def run():
    import argparse
    parser = argparse.ArgumentParser(prog='rename')
    parser.add_argument('-t', '--test', action='store_true',
                        help='test only, don\'t actually rename anything')
    parser.add_argument('regex', nargs=1, help='regular expression to match '
                                               'files with')
    parser.add_argument('target', nargs=1, help='target pattern using '
                                                'references to groups in the '
                                                'regular expression')
    values = parser.parse_args()
    sys.exit(Renamer(test=values.test).rename(regex="".join(values.regex),
                                              target="".join(values.target[0])))


if __name__ == '__main__':
    run()
