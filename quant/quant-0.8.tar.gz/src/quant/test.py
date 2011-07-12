import unittest
import quant.markettest
import quant.domtest
import quant.priceprocess.test
import quant.contracttype.test
import quant.pricer.test
import quant.leastsquarestest
import quant.django.apps.eui.views.test

def suite():
    suites = [
        quant.markettest.suite(),
        quant.domtest.suite(),
        quant.priceprocess.test.suite(),
        quant.contracttype.test.suite(),
        quant.pricer.test.suite(),
        quant.leastsquarestest.suite(),
        quant.django.apps.eui.views.test.suite(),
    ]
    return unittest.TestSuite(suites)

