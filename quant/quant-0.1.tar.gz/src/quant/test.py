import unittest
import quant.markettest
import quant.pricer.test
import quant.domtest

def suite():
    suites = [
        quant.markettest.suite(),
        quant.pricer.test.suite(),
        quant.domtest.suite(),
#        quant.plugintest.suite(),
#        quant.djangotest.suite(),
    ]
    return unittest.TestSuite(suites)

