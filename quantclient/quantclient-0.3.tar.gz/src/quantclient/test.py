import unittest
import os
import sys
from quantclient.apiclient import QuantApiClient

class TestQuantClient(unittest.TestCase):

    def setUp(self):
        self.client = QuantApiClient('http://quant.dev.localhost/api')

    def testExchanges(self):
        exchangeNames = self.client.getExchangeRegister()
        self.failUnless(exchangeNames)
        exchangeName = exchangeNames[0]
        exchange = self.client.getExchangeEntity(exchangeName)
        self.failUnless(exchange)
        self.failUnless(exchange['name'])
        self.failUnlessEqual(exchange['name'], exchangeName)


if __name__ == "__main__":
    unittest.main(defaultTest='TestQuantClient')

