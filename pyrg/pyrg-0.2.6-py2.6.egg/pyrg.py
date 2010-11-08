#!/usr/bin/env python
"""pyrg - colorized Python's UnitTest Result Tool"""
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE
from select import poll, POLLIN
from optparse import OptionParser
import sys
import re
import os
import pwd

__version__ = '0.2.6'
__author__ = 'Hideo Hattroi <hhatto.jp@gmail.com>'
__license__ = 'NewBSDLicense'

__all__ = ['get_color', 'parse_unittest_result_verbose',
           'parse_unittest_result', 'set_configuration']

DEFAULT_CONFIG_PATH = "/home/%s/.pyrgrc" % (pwd.getpwuid(os.getuid())[0])
PRINT_COLOR_SET_DEFAULT = {
        'ok': 'green',
        'fail': 'red',
        'error': 'yellow',
        'function': 'cyan',
}
PRINT_COLOR_SET = PRINT_COLOR_SET_DEFAULT.copy()
COLOR_MAP = {
        'black': '[30m%s[0m',
        'gray': '[1;30m%s[0m',
        #'black ': '[2;30m%s[0m',   ## not work
        'red': '[31m%s[0m',
        'pink': '[1;31m%s[0m',
        'darkred': '[2;31m%s[0m',
        'green': '[32m%s[0m',
        'yellowgreen': '[1;32m%s[0m',
        'darkgreen': '[2;32m%s[0m',
        'brown': '[33m%s[0m',
        'yellow': '[1;33m%s[0m',
        'gold': '[2;33m%s[0m',
        'blue': '[34m%s[0m',
        'lightblue': '[1;34m%s[0m',
        'darkblue': '[2;34m%s[0m',
        'magenta': '[35m%s[0m',
        'lightmagenta': '[1;35m%s[0m',
        'darkmagenta': '[2;35m%s[0m',
        'cyan': '[36m%s[0m',
        'lightcyan': '[1;36m%s[0m',
        'darkcyan': '[2;36m%s[0m',
        'silver': '[37m%s[0m',
        'white': '[1;37m%s[0m',
        'darksilver': '[2;37m%s[0m',
        }


def get_color(key):
    """color name get from COLOR_MAP dict."""
    return COLOR_MAP[PRINT_COLOR_SET[key]]


def parse_result_line(line):
    """parse to test result when fail tests"""
    err = False
    fail = False
    if 'errors' in line:
        err = True
    if 'failures' in line:
        fail = True
    if err and fail:
        f = line.split('=')[1].split(',')[0]
        e = line.split('=')[2].split(')')[0]
        result = "(%s=%s, " % (get_color('fail') % "failures",
                               get_color('fail') % f)
        result += "%s=%s)" % (get_color('error') % "errors",
                              get_color('error') % e)
    elif fail and not err:
        l = line.split('=')[1].split(')')[0]
        result = "(%s=%s)" % (get_color('fail') % "failures",
                              get_color('fail') % l)
    elif err and not fail:
        l = line.split('=')[1].split(')')[0]
        result = "(%s=%s)" % (get_color('error') % "errors",
                              get_color('error') % l)
    return get_color('fail') % "FAILED" + " %s" % result


def parse_lineone(line):
    """parse to test result line1"""
    results = []
    line = line.strip()
    for char in line:
        if '.' == char:
            results.append(get_color('ok') % ".")
        elif 'E' == char:
            results.append(get_color('error') % "E")
        elif 'F' == char:
            results.append(get_color('fail') % "F")
        else:
            results.append(char)
    return "".join(results)


def coloring_method(line):
    """colorized method line"""
    return get_color('function') % line


def parse_unittest_result(lines):
    """parse test result"""
    results = []
    err_verbose = re.compile("ERROR:")
    fail_verbose = re.compile("FAIL:")
    unittests_ok = re.compile("OK")
    unittests_failed = re.compile("FAILED")
    if not lines:
        return ""
    results.append(parse_lineone(lines[0]) + '\n')
    for line in lines[1:]:
        if unittests_ok.match(line):
            result = get_color('ok') % "OK"
        elif unittests_failed.match(line):
            result = parse_result_line(line)
        elif fail_verbose.match(line):
            result = "%s: %s\n" % (get_color('fail') % "FAIL",
                                   coloring_method(line[6:-1]))
        elif err_verbose.match(line):
            result = "%s: %s\n" % (get_color('error') % "ERROR",
                                   coloring_method(line[7:-1]))
        else:
            result = line
        results.append(result)
    return "".join(results)


def parse_unittest_result_verbose(lines):
    """parse test result, verbose print mode."""
    ok = re.compile("ok$")
    fail = re.compile("FAIL$")
    err = re.compile("ERROR$")
    fail_verbose = re.compile("FAIL:")
    err_verbose = re.compile("ERROR:")
    unittests_ok = re.compile("OK")
    unittests_failed = re.compile("FAILED")
    results = []
    for line in lines:
        if ok.search(line):
            tmp = ok.split(line)
            result = tmp[0] + get_color('ok') % "ok" + "\n"
        elif fail.search(line):
            tmp = fail.split(line)
            result = tmp[0] + get_color('fail') % "FAIL" + "\n"
        elif err.search(line):
            tmp = err.split(line)
            result = tmp[0] + get_color('error') % "ERROR" + "\n"
        elif fail_verbose.match(line):
            result = "%s: %s\n" % (get_color('fail') % "FAIL",
                                   coloring_method(line[6:-1]))
        elif err_verbose.match(line):
            result = "%s: %s\n" % (get_color('error') % "ERROR",
                                   coloring_method(line[7:-1]))
        elif unittests_ok.match(line):
            result = get_color('ok') % "OK"
        elif unittests_failed.match(line):
            result = parse_result_line(line)
        else:
            result = line
        results.append(result)
    return "".join(results)


def set_configuration(filename):
    """setting to printing color map"""
    ret = PRINT_COLOR_SET_DEFAULT.copy()
    if not os.path.exists(filename):
        return ret
    configure = ConfigParser()
    configure.read(filename)
    for setkey, color in configure.items('color'):
        if not setkey in PRINT_COLOR_SET:
            continue
        if color in COLOR_MAP:
            ret[setkey] = color
        else:
            ret[setkey] = PRINT_COLOR_SET_DEFAULT[setkey]
    return ret


def get_optionparser():
    """return to optparse's OptionParser object."""
    parser = OptionParser(version="pyrg: %s" % __version__,
                          description=__doc__,
                          usage="Usage: pyrg [options] TEST_SCRIPT.py\n"\
                                "     : python TEST_SCRIPT.py |& pyrg")
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='mode_verbose',
                      help='print to verbose result for unittest.')
    parser.add_option('-d', '--default-color', action='store_true',
                      dest='mode_defaultcolor',
                      help='used to default color setting.')
    parser.add_option('-f', '--config-file', dest='config_filename',
                      help='configuration file path')
    return parser


def check_verbose(line):
    verbose = re.compile("(ok$|ERROR$|FAIL$)")
    return verbose.search(line)


def main():
    """execute command line tool"""
    global PRINT_COLOR_SET
    parser = get_optionparser()
    (opts, args) = parser.parse_args()
    if not opts.mode_defaultcolor:
        if opts.config_filename:
            PRINT_COLOR_SET = set_configuration(opts.config_filename)
        else:
            PRINT_COLOR_SET = set_configuration(DEFAULT_CONFIG_PATH)
    if len(args):
        if opts.mode_verbose:
            cmdline = ['python', args[0], '-v']
            if len(args) >= 2:
                cmdline += [i for i in args[1:]]
            proc = Popen(cmdline, stdout=PIPE, stderr=PIPE)
            result = proc.communicate()[1]
            print parse_unittest_result_verbose(result.splitlines(1))
        else:
            cmdline = ['python']
            cmdline += [i for i in args]
            proc = Popen(cmdline, stdout=PIPE, stderr=PIPE)
            result = proc.communicate()[1]
            print parse_unittest_result(result.splitlines(1))
    else:
        poller = poll()
        poller.register(sys.stdin, POLLIN)
        pollret = poller.poll(1)
        if len(pollret) == 1 and pollret[0][1] & POLLIN:
            lines = sys.stdin.readlines()
            if check_verbose(lines[0]):
                print parse_unittest_result_verbose(lines)
            else:
                print parse_unittest_result(lines)
        else:
            parser.print_help()

if __name__ == '__main__':
    sys.exit(main())
