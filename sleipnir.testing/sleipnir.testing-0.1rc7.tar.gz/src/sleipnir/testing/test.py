#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Base test classes for Sleipnir TestSuite"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "beta"
__version__ = "0.3"
__date__    = "28 March 2010"
__license__ = "See LICENSE file for details"

# Import here required modules
import sys
import __builtin__

from unittest import TextTestRunner
from unittest import TestCase as BaseTest
from unittest import TestSuite, TestLoader

__all__ = ['TestCase', 'create_docsuite', 'create_suite', 'run_suite']


#pylint:disable-msg=R0904
class TestCase(BaseTest):
    """Base Class for Sleipnir Tests"""


def create_suite(test):
    """Sugar to load tests into a new TestSuite from a tuple"""

    from itertools import ifilter

    tests = test[:]
    tcs = ifilter(lambda x: not isinstance(x[1], TestSuite), enumerate(tests))
    for index, value in tcs:
        tests[index] = TestLoader().loadTestsFromTestCase(value)
    return TestSuite(tests)


def create_docsuite(tests, set_up=None, tear_down=None):
    """
    Create a valid Unittest suite for doctest files located at 'tests'
    iterable

    All files MUST be expresed has an absolute path
    """
    #pylint: disable-msg=W0212,C0103
    def setUp(test):
        """Preapre doctest to be runned next to sleipnir code"""
        # if a setup was passed, call it
        if callable(set_up):
            set_up(test)

    def tearDown(test):
        """Set down generic code preapred for doctest suites"""
        # if teardown was passed, call it
        if callable(tear_down):
            tear_down(test)

    # return a valid suite
    from doctest import DocFileSuite
    #pylint: disable-msg=W0142
    return DocFileSuite(
        *tests, module_relative=False, setUp=setUp, tearDown=tearDown)


def executable(parse_func=None):
    """
    Make app to be runned in main appling parse_func to args
    previously
    """
    parse_func = parse_func or (lambda args: (None, args))

    def main_decorator(func):
        """Main decorator"""
        from functools import wraps

        @wraps(func)
        def wrapper(arguments=None):
            """
            Apply parse func to args anf invoke func with returned
            values
            """
            arguments = arguments or sys.argv
            options, arguments = parse_func(arguments)
            sys.exit(func(options, arguments))
        return wrapper
    return main_decorator


def parse_arguments(arguments):
    """Parse arguments pased to command"""

    from optparse import OptionParser, OptionGroup

    parser = OptionParser(usage="Usage: %prog [OPTIONS] [SUITE]")
    prname = parser.get_prog_name()

    # test options
    parser.add_option("-v", dest="verbose", metavar="VERBOSITY", default=2,  \
        help="Run test with VERBOSITY (default is 2)")
    parser.add_option("-s", dest="suite", metavar="SUITE", default='Main',   \
        help="Run suite whith name SUITE (default is 'Main')")

    # profile options
    group = OptionGroup(parser, "Run Options")
    group.add_option("-p", "--profile", dest="profile", action="store_true", \
        help="Profile and save results to ('" + prname + ".profile')")
    group.add_option("-q", "--cover", dest="coverage", action="store_true",  \
        help="Coverage store results into ('" + prname + ".coverage')")
    parser.add_option_group(group)

    option, args = parser.parse_args(arguments[1:])
    if len(args) > 0:
        parser.error("Invalid number of arguments. Expected 0")

    suite_smell, runner_module = 'suite', '__main__'
    candidates = sys.modules[runner_module].__dict__.keys()
    for k in [x for x in candidates if x.endswith(suite_smell)]:
        if k.startswith(option.suite.lower()):
            suite = sys.modules[runner_module].__dict__[k]
            option.suite = suite() if hasattr(suite, 'func_name') else suite
            return (option, args)

    parser.error("Invalid suite '%s'" % option.suite)


#pylint: disable-msg=W0613
@executable(parse_arguments)
def run_suite(options, args):
    """
    Sugar to run a suite in a stadalone mode. Pass 'suite' as default
    suite to be run
    """
    # prepare buitin options
    __builtin__.__profile__ = options.profile
    __builtin__.__coverage__ = options.coverage

    # launch the testing process
    TextTestRunner(verbosity=int(options.verbose)).run(options.suite)
