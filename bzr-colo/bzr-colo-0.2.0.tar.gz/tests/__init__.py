from unittest import TestLoader, TestSuite

import test_colo, test_sync, test_qcommands

def test_suite():
    suite = TestSuite()
    for t in [test_colo, test_sync, test_qcommands]:
        suite.addTests(TestLoader().loadTestsFromModule(t))
    return suite

