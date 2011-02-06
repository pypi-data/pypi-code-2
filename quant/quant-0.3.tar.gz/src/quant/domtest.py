import unittest
import quant.testunit
import quant.dom.basetest
import quant.dom.forwardcontracttest
import quant.dom.binaryoptiontest
import quant.dom.europeanoptiontest
import quant.dom.americanoptiontest
import quant.dom.buildertest
import quant.dom.booktest
import quant.dom.markettest

def suite():
    suites = [
        quant.dom.basetest.suite(),
        quant.dom.forwardcontracttest.suite(),
        quant.dom.binaryoptiontest.suite(),
        quant.dom.europeanoptiontest.suite(),
        quant.dom.americanoptiontest.suite(),
        quant.dom.buildertest.suite(),
        quant.dom.booktest.suite(),

    ]
    return unittest.TestSuite(suites)

