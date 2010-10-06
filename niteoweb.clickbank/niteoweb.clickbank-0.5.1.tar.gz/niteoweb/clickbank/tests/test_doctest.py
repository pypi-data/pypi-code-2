import unittest
import doctest

from Testing import ZopeTestCase as ztc

from niteoweb.clickbank.tests import ClickBankControlPanelTestCase


def test_suite():
    return unittest.TestSuite([
            
        # Test the ClickBank control panel
        ztc.ZopeDocFileSuite(
            'tests/control_panel.txt', package='niteoweb.clickbank',
            test_class=ClickBankControlPanelTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
