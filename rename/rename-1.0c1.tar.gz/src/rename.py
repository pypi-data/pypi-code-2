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
TRANSFORM = {
    None: lambda x: x,
    'lower': lambda x: x.lower(),
    'upper': lambda x: x.upper(),
}


class Renamer(object):
    def __init__(self, test=False, case_insensitive=False, xform=None,
                 quiet=False, **kwargs):
        self.case_insensitive = case_insensitive
        self.xform = xform
        self.test = test
        self.quiet = quiet
        self.targets = {}

    def _apply_match(self, match, target):
        move_to = target
        for prefix, num in MATCH_REGEX.findall(target):
            move_to = move_to.replace(prefix+num, match.group(int(num)))
        for prefix, num, suffix in MATCH_REGEX_BRACKETS.findall(target):
            move_to = move_to.replace(prefix+num+suffix, match.group(int(num)))
        return TRANSFORM[self.xform](move_to)

    def _process_single(self, entry, match, target):
        if not match:
            return
        move_to = self._apply_match(match, target)
        self.targets.setdefault(move_to, []).append(entry)

    def rename(self, regex, target, except_regex=None, **kwargs):
        if self.quiet:
            INFO, ERROR = open(os.devnull), open(os.devnull)
        else:
            INFO, ERROR = sys.stdout, sys.stderr
        flags = 0
        if self.case_insensitive:
            flags = re.IGNORECASE
        r = re.compile("^%s$" % regex, flags)
        exc = None
        if except_regex:
            exc = re.compile(except_regex, flags)
        for entry in os.listdir('.'):
            m = r.search(entry)
            if exc and exc.search(entry):
                continue
            self._process_single(entry, m, target)
        # sanity check
        for target, sources in self.targets.iteritems():
            if len(sources) > 1:
                print >>ERROR, ("rename error: multiple files (%s) would "
                                "be written to %s") % (", ".join(sources),
                                                       target)
                return 1
            if os.path.exists(target):
                print >>ERROR, ("rename error: target %s already exists "
                                "for source %s") % (target, sources[0])
                return 2
        # actual rename
        for target, sources in self.targets.iteritems():
            if self.test:
                print >>INFO, ("Would run os.rename(%s, %s)" % (sources[0],
                                                                target))
            else:
                os.rename(sources[0], target)
        return 0


def run():
    import argparse
    parser = argparse.ArgumentParser(prog='rename')
    parser.add_argument('-i', '--case-insensitive', action='store_true',
                        help='treat the regular expression as '
                             'case-insensitive')
    parser.add_argument('-l', '--lower', action='store_const', dest='xform',
                        const='lower', help='translate all letters to '
                                            'lower-case')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='don\'t print anything, just return status codes')
    parser.add_argument('-U', '--upper', action='store_const', dest='xform',
                        const='upper', help='translate all letters to '
                                            'upper-case')
    parser.add_argument('-v', '--except', dest='except_regex', action='store',
                        nargs=1, default="", help='exclude files matching the '
                                                   'following regular '
                                                   'expression')
    parser.add_argument('-t', '--test', action='store_true',
                        help='test only, don\'t actually rename anything')
    parser.add_argument('--selftest', action='store_true',
                        help='run internal unit tests')
    parser.add_argument('regex', nargs=1, help='regular expression to match '
                                               'files with')
    parser.add_argument('target', nargs=1, help='target pattern using '
                                                'references to groups in the '
                                                'regular expression')

    stparser = argparse.ArgumentParser(prog='rename')
    stparser.add_argument('--selftest', action='store_true',
                        help='run internal unit tests')
    args = stparser.parse_args()
    if not args.selftest:
        args = parser.parse_args()
        args.regex = "".join(args.regex)
        args.except_regex = "".join(args.except_regex)
        args.target = "".join(args.target[0])
        sys.exit(Renamer(**args.__dict__).rename(**args.__dict__))
    else:
        selftest()

def _runtest(testcase):
    import tempfile
    dirpath = tempfile.mkdtemp(".selftest", "rename")
    try:
        for prefix in ("CaSe", "case"):
            for index in range(1, 4):
                for suffix in "qwertyuiop":
                    path = "".join([dirpath, os.sep, prefix, str(index),
                                    suffix])
                    try:
                        f = open(path, "wb")
                        try:
                            f.write(path)
                            f.write('\r\n')
                        finally:
                            f.close()
                    except (IOError, OSError):
                        print >>sys.stderr, "Cannot create temporary file:", \
                              path
                        sys.exit(1)
        return testcase(dirpath)
    finally:
        files = os.listdir(dirpath)
        for f in files:
            os.unlink(os.sep.join((dirpath, f)))
        os.rmdir(dirpath)


def selftest():
    def dummy(dirpath):
        files = os.listdir(dirpath)
        if len(files) == 60:
            print "Testing on a case-sensitive filesystem."
            return True
        elif len(files) == 30:
            print "Testing on a case-insensitive filesystem."
            return False
        else:
            print >>sys.stderr, ("Not all files were created successfully. "
                                "Expected 60 or 30, got %d." % len(files))
            sys.exit(10)
    def _runcase(**kwargs):
        kwargs['quiet'] = True
        def case(dirpath):
            cwd = os.getcwd()
            os.chdir(dirpath)
            try:
                try:
                    result = Renamer(**kwargs).rename(**kwargs)
                    if result != kwargs.get('result', 0):
                        raise ValueError(result)
                    files = set(os.listdir('.'))
                    if not result and files != set(kwargs.get('files', [])):
                        raise ValueError(11)
                finally:
                    os.chdir(cwd)
                print "Test %(name)s OK." % kwargs
                return 0
            except ValueError:
                print >>sys.stderr, "Test %(name)s (%(desc)s) failed." % kwargs
                return result
            except:
                print >>sys.stderr, "Test %(name)s (%(desc)s) failed." % kwargs
                return 12
        return _runtest(case)

    case_sensitive = _runtest(dummy)
    if not case_sensitive:
        print >>sys.stderr, ("Case-insensitive selftest variants not written "
                             "yet.")
        sys.exit(13)
    i = 0
    i += _runcase(name="1", desc='CaSe -> BrandNew',
             regex=r'CaSe(\d[qwertyuiop])', target=r'BrandNew\1',
             files=['BrandNew1e', 'BrandNew1i', 'BrandNew1o', 'BrandNew1p',
                    'BrandNew1q', 'BrandNew1r', 'BrandNew1t', 'BrandNew1u',
                    'BrandNew1w', 'BrandNew1y', 'BrandNew2e', 'BrandNew2i',
                    'BrandNew2o', 'BrandNew2p', 'BrandNew2q', 'BrandNew2r',
                    'BrandNew2t', 'BrandNew2u', 'BrandNew2w', 'BrandNew2y',
                    'BrandNew3e', 'BrandNew3i', 'BrandNew3o', 'BrandNew3p',
                    'BrandNew3q', 'BrandNew3r', 'BrandNew3t', 'BrandNew3u',
                    'BrandNew3w', 'BrandNew3y', 'case1e', 'case1i', 'case1o',
                    'case1p', 'case1q', 'case1r', 'case1t', 'case1u', 'case1w',
                    'case1y', 'case2e', 'case2i', 'case2o', 'case2p', 'case2q',
                    'case2r', 'case2t', 'case2u', 'case2w', 'case2y', 'case3e',
                    'case3i', 'case3o', 'case3p', 'case3q', 'case3r', 'case3t',
                    'case3u', 'case3w', 'case3y'])
    i += _runcase(name="2", desc='CaSe -> case',
             regex=r'CaSe(\d[qwertyuiop])', target=r'case\1',
             result=2)
    i += _runcase(name="3", desc='CaSe (i) -> case', case_insensitive=True,
             regex=r'CaSe(\d[qwertyuiop])', target=r'case\1',
             result=1)
    i += _runcase(name="4", desc='[Cc][Aa][Ss][Ee] -> case',
             regex=r'[Cc][Aa][Ss][Ee](\d[qwertyuiop])', target=r'case\1',
             case_insensitive=True, result=1)
    i += _runcase(name="5", desc='CaSe -> SeCa (except e$)',
             regex=r'CaSe(\d[qwertyuiop])', target=r'SeCa\1',
             except_regex=r'e$',
             files=['CaSe1e', 'SeCa1i', 'SeCa1o', 'SeCa1p', 'SeCa1q', 'SeCa1r',
                    'SeCa1t', 'SeCa1u', 'SeCa1w', 'SeCa1y', 'CaSe2e', 'SeCa2i',
                    'SeCa2o', 'SeCa2p', 'SeCa2q', 'SeCa2r', 'SeCa2t', 'SeCa2u',
                    'SeCa2w', 'SeCa2y', 'CaSe3e', 'SeCa3i', 'SeCa3o', 'SeCa3p',
                    'SeCa3q', 'SeCa3r', 'SeCa3t', 'SeCa3u', 'SeCa3w', 'SeCa3y',
                    'case1e', 'case1i', 'case1o', 'case1p', 'case1q', 'case1r',
                    'case1t', 'case1u', 'case1w', 'case1y', 'case2e', 'case2i',
                    'case2o', 'case2p', 'case2q', 'case2r', 'case2t', 'case2u',
                    'case2w', 'case2y', 'case3e', 'case3i', 'case3o', 'case3p',
                    'case3q', 'case3r', 'case3t', 'case3u', 'case3w', 'case3y'])
    i += _runcase(name="6", desc='CaSe -> SeCa (U)',
             regex=r'CaSe(\d[qwertyuiop])', target=r'SeCa\1',
             except_regex=r'e$', xform='upper',
             files=['CaSe1e', 'SECA1I', 'SECA1O', 'SECA1P', 'SECA1Q', 'SECA1R',
                    'SECA1T', 'SECA1U', 'SECA1W', 'SECA1Y', 'CaSe2e', 'SECA2I',
                    'SECA2O', 'SECA2P', 'SECA2Q', 'SECA2R', 'SECA2T', 'SECA2U',
                    'SECA2W', 'SECA2Y', 'CaSe3e', 'SECA3I', 'SECA3O', 'SECA3P',
                    'SECA3Q', 'SECA3R', 'SECA3T', 'SECA3U', 'SECA3W', 'SECA3Y',
                    'case1e', 'case1i', 'case1o', 'case1p', 'case1q', 'case1r',
                    'case1t', 'case1u', 'case1w', 'case1y', 'case2e', 'case2i',
                    'case2o', 'case2p', 'case2q', 'case2r', 'case2t', 'case2u',
                    'case2w', 'case2y', 'case3e', 'case3i', 'case3o', 'case3p',
                    'case3q', 'case3r', 'case3t', 'case3u', 'case3w', 'case3y'])
    i += _runcase(name="7", desc='CaSe (i) -> SeCa (U)', case_insensitive=True,
             regex=r'CaSe(\d[qwertyuiop])', target=r'SeCa\1',
             except_regex=r'e$', xform='upper', result=1)
    if not i:
        print "All tests OK."
if __name__ == '__main__':
    run()
