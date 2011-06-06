#!/usr/bin/env python

""" Run all available unit-tests.

    Designed to fit into the setup tools test framework, where possible.

    Some tests, outside the unittest framework require manual inspection of the results.
"""

import test_autoclosing_queue
import test_autoclosing_queue_autocloses
import test_nonblockingloghandler_units
import test_nonblockingloghandler_stresstest
import test_nonblockingloghandler_termination_tests

import unittest

def additional_tests(): # Name specified by setup tools.
    all_tests = unittest.TestSuite()
    for module_to_test in [
        test_autoclosing_queue,
        test_nonblockingloghandler_units,
        test_nonblockingloghandler_termination_tests
        ]:

        all_tests.addTests(unittest.defaultTestLoader.loadTestsFromModule(module_to_test))

    return all_tests

def main():
    unittest.TextTestRunner(verbosity=10).run(additional_tests())
    test_nonblockingloghandler_stresstest.stress_test() # Not part of the unittest framework.
    test_autoclosing_queue_autocloses.main() # Not part of unittest framework. Must be last

if __name__ == "__main__":
    main()
