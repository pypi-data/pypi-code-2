#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Łukasz Langa
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

import math
import os
import re
import shutil
import sys


MATCH_REGEX = re.compile(r'(\\)(\d+)')
MATCH_REGEX_BRACKETS = re.compile(r'(\\\()([^)]+)(\))')
TRANSFORM = {
    None: lambda x: x,
    'lower': lambda x: x.lower(),
    'upper': lambda x: x.upper(),
}


class Renamer(object):
    def __init__(self, test=False, case_insensitive=False, xform=None,
                 quiet=False, copy=False, index_first=1, index_step=1,
                 index_digits='auto', index_pad_with='0', **kwargs):
        self.case_insensitive = case_insensitive
        self.copy = copy
        self.xform = xform
        self.test = test
        self.quiet = quiet
        self.index_first = int(index_first)
        self.index_step = int(index_step)
        self.index_digits = index_digits
        self.index_pad_with = index_pad_with
        self.targets = {}

    def _apply_match(self, match, target, index, max_indexes):
        move_to = target
        for prefix, num in MATCH_REGEX.findall(target):
            move_to = move_to.replace(prefix+num, match.group(int(num)))
        for prefix, ref, suffix in MATCH_REGEX_BRACKETS.findall(target):
            ref_string = prefix + ref + suffix
            try:
                replacement = match.group(int(ref))
            except ValueError:
                if ref.lower() != 'index':
                    raise ValueError("Unknown special reference: `%s`" % ref)
                replacement = '%d' % self.index(index)
                if self.index_digits == 'auto':
                    index_digits = int(math.log(self.index(max_indexes),
                        10)) + 1
                else:
                    index_digits = int(self.index_digits)
                pad_count = index_digits - len(replacement)
                if pad_count > 0:
                    replacement = "".join((self.index_pad_with * pad_count,
                        replacement))
            move_to = move_to.replace(ref_string, replacement)
        return TRANSFORM[self.xform](move_to)

    def _process_single(self, entry, match, target, index, max_indexes):
        if not match:
            return
        move_to = self._apply_match(match, target, index, max_indexes)
        self.targets.setdefault(move_to, []).append(entry)

    def index(self, number):
        return self.index_first + (number * self.index_step)

    def same_file(self, file1, file2):
        return (os.path.abspath(file1).lower() == os.path.abspath(file2).lower()
            and os.stat(file1).st_ino == os.stat(file2).st_ino)

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
        index = 0
        files = os.listdir('.')
        if exc:
            files = [f for f in files if not exc.search(f)]
        file_count = len(files)
        for index, entry in enumerate(files):
            m = r.search(entry)
            self._process_single(entry, m, target, index, file_count)
        # sanity check
        for target, sources in self.targets.iteritems():
            if len(sources) > 1:
                print >>ERROR, ("rename error: multiple files (%s) would "
                                "be written to %s") % (", ".join(sources),
                                                       target)
                return 1
            if os.path.exists(target) and not self.same_file(target,
                    sources[0]):
                print >>ERROR, ("rename error: target %s already exists "
                                "for source %s") % (target, sources[0])
                return 2
        # actual rename
        for target, sources in self.targets.iteritems():
            if self.copy:
                if self.test:
                    print >>INFO, ("Would run shutil.copy(%s, %s) (with "
                            "copymode and copystat)" % (sources[0], target))
                else:
                    shutil.copy(sources[0], target)
                    shutil.copymode(sources[0], target)
                    shutil.copystat(sources[0], target)
            else:
                if self.test:
                    print >>INFO, ("Would run os.rename(%s, %s)" % (sources[0],
                                                                    target))
                else:
                    os.rename(sources[0], target)
        return 0


def run():
    import argparse
    parser = argparse.ArgumentParser(prog='rename')
    parser.add_argument('-c', '--copy', action='store_true',
        help='copy files instead of renaming')
    parser.add_argument('-I', '--case-insensitive', action='store_true',
        help='treat the regular expression as case-insensitive')
    parser.add_argument('-l', '--lower', action='store_const', dest='xform',
        const='lower', help='translate all letters to lower-case')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='don\'t print anything, just return status codes')
    parser.add_argument('-U', '--upper', action='store_const', dest='xform',
        const='upper', help='translate all letters to upper-case')
    parser.add_argument('-v', '--except', dest='except_regex', action='store',
        default="", help='exclude files matching the following '
        'regular expression')
    parser.add_argument('-t', '--test', action='store_true', help='test only, '
        'don\'t actually rename anything')
    group = parser.add_argument_group('Configuration for the special \\(index)'
        ' reference')
    group.add_argument('--index-first', default=1, help='specifies '
        'what number will the first \\(index) substitution contain. Default: 1')
    group.add_argument('--index-step', default=1, help='specifies '
        'what number will be added with each step to the first value. Negative '
        'numbers allowed. Default: 1')
    group.add_argument('--index-digits', default='auto',
        help='specifies how many digits will be used in each \\(index) '
        'substitution. If a number has fewer digits, they will be prefixed by '
        'leading zeroes (or another character, see --index-pad-with). Default: '
        'auto (e.g. path enough digits so that each number uses the same amount'
        ' of characters)')
    group.add_argument('--index-pad-with', default='0',
        help='specifies what character will be used for padding. Default: "0"')
    parser.add_argument('--selftest', nargs='?', const=True,
        metavar='use_directory', help='run internal unit tests')
    parser.add_argument('regex', help='regular expression to match '
        'files with')
    parser.add_argument('target', help='target pattern using '
        'references to groups in the regular expression')
    stparser = argparse.ArgumentParser(prog='rename', add_help=False)
    stparser.add_argument('--selftest', nargs='?', const=True,
        help='run internal unit tests')
    args = stparser.parse_known_args()
    if not args[0].selftest:
        args = parser.parse_args()
        args.regex = "".join(args.regex)
        args.except_regex = "".join(args.except_regex)
        args.target = "".join(args.target)
        sys.exit(Renamer(**args.__dict__).rename(**args.__dict__))
    else:
        selftest(args[0].selftest)

def selftest(temp_dir=None):
    if temp_dir == True:
        temp_dir = None
    def _runtest(testcase, show_dir=False):
        import tempfile
        dirpath = tempfile.mkdtemp(".selftest", "rename", temp_dir)
        if show_dir:
            print "Using", os.path.split(dirpath)[0], "as the temporary "\
                "directory base."
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
                            print >>sys.stderr, "Cannot create temporary "\
                                "file:", path
                            sys.exit(1)
            return testcase(dirpath)
        finally:
            files = os.listdir(dirpath)
            for f in files:
                os.unlink(os.sep.join((dirpath, f)))
            os.rmdir(dirpath)

    def dummy(dirpath):
        files = os.listdir(dirpath)
        if len(files) == 60:
            print "Testing on a case-sensitive filesystem."
            return True, True
        elif len(files) == 30:
            preserving = all([f.startswith('CaSe') for f in files])
            if preserving:
                print "Testing on a case-preserving filesystem."
                return False, True
            else:
                print "Testing on a case-insensitive filesystem."
                return False, False
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

    def _case_sensitive_tests():
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
                       'BrandNew3w', 'BrandNew3y', 'case1e', 'case1i',
                       'case1o', 'case1p', 'case1q', 'case1r', 'case1t',
                       'case1u', 'case1w', 'case1y', 'case2e', 'case2i',
                       'case2o', 'case2p', 'case2q', 'case2r', 'case2t',
                       'case2u', 'case2w', 'case2y', 'case3e', 'case3i',
                       'case3o', 'case3p', 'case3q', 'case3r', 'case3t',
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
                files=['CaSe1e', 'SeCa1i', 'SeCa1o', 'SeCa1p', 'SeCa1q',
                       'SeCa1r', 'SeCa1t', 'SeCa1u', 'SeCa1w', 'SeCa1y',
                       'CaSe2e', 'SeCa2i', 'SeCa2o', 'SeCa2p', 'SeCa2q',
                       'SeCa2r', 'SeCa2t', 'SeCa2u', 'SeCa2w', 'SeCa2y',
                       'CaSe3e', 'SeCa3i', 'SeCa3o', 'SeCa3p', 'SeCa3q',
                       'SeCa3r', 'SeCa3t', 'SeCa3u', 'SeCa3w', 'SeCa3y',
                       'case1e', 'case1i', 'case1o', 'case1p', 'case1q',
                       'case1r', 'case1t', 'case1u', 'case1w', 'case1y',
                       'case2e', 'case2i', 'case2o', 'case2p', 'case2q',
                       'case2r', 'case2t', 'case2u', 'case2w', 'case2y',
                       'case3e', 'case3i', 'case3o', 'case3p', 'case3q',
                       'case3r', 'case3t', 'case3u', 'case3w', 'case3y'])
        i += _runcase(name="6", desc='CaSe -> SeCa (U)',
                regex=r'CaSe(\d[qwertyuiop])', target=r'SeCa\1',
                except_regex=r'e$', xform='upper',
                files=['CaSe1e', 'SECA1I', 'SECA1O', 'SECA1P', 'SECA1Q',
                       'SECA1R', 'SECA1T', 'SECA1U', 'SECA1W', 'SECA1Y',
                       'CaSe2e', 'SECA2I', 'SECA2O', 'SECA2P', 'SECA2Q',
                       'SECA2R', 'SECA2T', 'SECA2U', 'SECA2W', 'SECA2Y',
                       'CaSe3e', 'SECA3I', 'SECA3O', 'SECA3P', 'SECA3Q',
                       'SECA3R', 'SECA3T', 'SECA3U', 'SECA3W', 'SECA3Y',
                       'case1e', 'case1i', 'case1o', 'case1p', 'case1q',
                       'case1r', 'case1t', 'case1u', 'case1w', 'case1y',
                       'case2e', 'case2i', 'case2o', 'case2p', 'case2q',
                       'case2r', 'case2t', 'case2u', 'case2w', 'case2y',
                       'case3e', 'case3i', 'case3o', 'case3p', 'case3q',
                       'case3r', 'case3t', 'case3u', 'case3w', 'case3y'])
        i += _runcase(name="7", desc='CaSe (i) -> SeCa (U)',
                case_insensitive=True, regex=r'CaSe(\d[qwertyuiop])',
                target=r'SeCa\1', except_regex=r'e$', xform='upper', result=1)
        i += _runcase(name="8", desc='CaSe -> index (auto)',
                case_insensitive=True,
                regex=r'CaSe(\d[qwertyuiop])', target=r'C\(index)',
                files=['C{0:0>2}'.format(i+1) for i in xrange(60)])
        i += _runcase(name="9", desc='CaSe -> index (100, +2, _, auto)',
                case_insensitive=True,
                regex=r'CaSe(\d[qwertyuiop])', target=r'C\(index)',
                index_first=100, index_step=2, index_pad_with='_',
                files=['C{0:_>3}'.format(i) for i in xrange(100, 220, 2)])
        return i

    def _case_preserving_tests():
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
                       'BrandNew3w', 'BrandNew3y'])
        i += _runcase(name="2", desc='CaSe -> case',
                regex=r'CaSe(\d[qwertyuiop])', target=r'case\1',
                files=['case1e', 'case1i', 'case1o', 'case1p', 'case1q',
                       'case1r', 'case1t', 'case1u', 'case1w', 'case1y',
                       'case2e', 'case2i', 'case2o', 'case2p', 'case2q',
                       'case2r', 'case2t', 'case2u', 'case2w', 'case2y',
                       'case3e', 'case3i', 'case3o', 'case3p', 'case3q',
                       'case3r', 'case3t', 'case3u', 'case3w', 'case3y'])
        i += _runcase(name="3", desc='CaSe (i) -> CAse', case_insensitive=True,
                regex=r'CaSe(\d[qwertyuiop])', target=r'CAse\1',
                files=['CAse1e', 'CAse1i', 'CAse1o', 'CAse1p', 'CAse1q',
                       'CAse1r', 'CAse1t', 'CAse1u', 'CAse1w', 'CAse1y',
                       'CAse2e', 'CAse2i', 'CAse2o', 'CAse2p', 'CAse2q',
                       'CAse2r', 'CAse2t', 'CAse2u', 'CAse2w', 'CAse2y',
                       'CAse3e', 'CAse3i', 'CAse3o', 'CAse3p', 'CAse3q',
                       'CAse3r', 'CAse3t', 'CAse3u', 'CAse3w', 'CAse3y'])
        i += _runcase(name="4", desc='[Cc][Aa][Ss][Ee] -> caSE',
                regex=r'[Cc][Aa][Ss][Ee](\d[qwertyuiop])', target=r'caSE\1',
                case_insensitive=True,
                files=['caSE1e', 'caSE1i', 'caSE1o', 'caSE1p', 'caSE1q',
                       'caSE1r', 'caSE1t', 'caSE1u', 'caSE1w', 'caSE1y',
                       'caSE2e', 'caSE2i', 'caSE2o', 'caSE2p', 'caSE2q',
                       'caSE2r', 'caSE2t', 'caSE2u', 'caSE2w', 'caSE2y',
                       'caSE3e', 'caSE3i', 'caSE3o', 'caSE3p', 'caSE3q',
                       'caSE3r', 'caSE3t', 'caSE3u', 'caSE3w', 'caSE3y'])
        i += _runcase(name="5", desc='CaSe -> SeCa (except e$)',
                regex=r'CaSe(\d[qwertyuiop])', target=r'SeCa\1',
                except_regex=r'e$',
                files=['CaSe1e', 'SeCa1i', 'SeCa1o', 'SeCa1p', 'SeCa1q',
                       'SeCa1r', 'SeCa1t', 'SeCa1u', 'SeCa1w', 'SeCa1y',
                       'CaSe2e', 'SeCa2i', 'SeCa2o', 'SeCa2p', 'SeCa2q',
                       'SeCa2r', 'SeCa2t', 'SeCa2u', 'SeCa2w', 'SeCa2y',
                       'CaSe3e', 'SeCa3i', 'SeCa3o', 'SeCa3p', 'SeCa3q',
                       'SeCa3r', 'SeCa3t', 'SeCa3u', 'SeCa3w', 'SeCa3y'])
        i += _runcase(name="6", desc='CaSe -> SeCa (U)',
                regex=r'CaSe(\d[qwertyuiop])', target=r'SeCa\1',
                except_regex=r'e$', xform='upper',
                files=['CaSe1e', 'SECA1I', 'SECA1O', 'SECA1P', 'SECA1Q',
                       'SECA1R', 'SECA1T', 'SECA1U', 'SECA1W', 'SECA1Y',
                       'CaSe2e', 'SECA2I', 'SECA2O', 'SECA2P', 'SECA2Q',
                       'SECA2R', 'SECA2T', 'SECA2U', 'SECA2W', 'SECA2Y',
                       'CaSe3e', 'SECA3I', 'SECA3O', 'SECA3P', 'SECA3Q',
                       'SECA3R', 'SECA3T', 'SECA3U', 'SECA3W', 'SECA3Y'])
        i += _runcase(name="7", desc='CaSe (i) -> SeCa (U)',
                case_insensitive=True, regex=r'CaSe(\d[qwertyuiop])',
                target=r'SeCa\1', except_regex=r'e$', xform='upper',
                files=['CaSe1e', 'SECA1I', 'SECA1O', 'SECA1P', 'SECA1Q',
                       'SECA1R', 'SECA1T', 'SECA1U', 'SECA1W', 'SECA1Y',
                       'CaSe2e', 'SECA2I', 'SECA2O', 'SECA2P', 'SECA2Q',
                       'SECA2R', 'SECA2T', 'SECA2U', 'SECA2W', 'SECA2Y',
                       'CaSe3e', 'SECA3I', 'SECA3O', 'SECA3P', 'SECA3Q',
                       'SECA3R', 'SECA3T', 'SECA3U', 'SECA3W', 'SECA3Y'])
        i += _runcase(name="8", desc='CaSe -> index (auto)',
                regex=r'CaSe(\d[qwertyuiop])', target=r'C\(index)',
                files=['C{0:0>2}'.format(i+1) for i in xrange(30)])
        i += _runcase(name="9", desc='CaSe -> index (100, +2, _, auto)',
                regex=r'CaSe(\d[qwertyuiop])', target=r'C\(index)',
                index_first=100, index_step=2, index_pad_with='_',
                files=['C{0:_>3}'.format(i) for i in xrange(100, 160, 2)])
        return i

    def _case_insensitive_tests():
        print >>sys.stderr, ("Case-insensitive selftest variants not written "
                             "yet.")
        sys.exit(13)

    case_sensitive, case_preserving = _runtest(dummy, show_dir=True)
    tests = {
        (True, True): _case_sensitive_tests,
        (False, True): _case_preserving_tests,
        (False, False): _case_insensitive_tests,
    }
    i = tests[case_sensitive, case_preserving]()
    if not i:
        print "All tests OK."

if __name__ == '__main__':
    run()
