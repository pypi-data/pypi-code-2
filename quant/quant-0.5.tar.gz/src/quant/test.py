import unittest
import quant.markettest
import quant.domtest
import quant.priceprocess.test
import quant.contracttype.test
import quant.pricer.test

def suite():
    suites = [
        quant.markettest.suite(),
        quant.domtest.suite(),
        quant.priceprocess.test.suite(),
        quant.contracttype.test.suite(),
        quant.pricer.test.suite(),
    ]
    return unittest.TestSuite(suites)

