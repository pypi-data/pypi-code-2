import unittest
from quant.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(BookTestCase)
    ]
    return unittest.TestSuite(suites)


class BookTestCase(TestCase):

    def setUp(self):
        self.book = self.createBook()
        self.book.europeanOptions.create(
            title="European call #1",
            isPut=False,
            underlying='wti',
            volume=10,
            strikePrice=9,
            expiryTime='2011-01-06',
            deliveryPeriod='2011-01-06'
        )
        self.book.europeanOptions.create(
            title="European put #2",
            isPut=True,
            underlying='wti',
            volume=10,
            strikePrice=9,
            expiryTime='2011-01-06',
            deliveryPeriod='2011-01-06'
        )


    def tearDown(self):
        self.book.delete()

    def test_getResults(self):
        bookResults = self.book.getResults()
        self.assertTrue(bookResults.contracts)
        self.assertTrue(bookResults.lines)
        self.assertTrue(bookResults.value)
        self.assertEqual(round(bookResults.value, 3), 38.320)
        self.assertEqual(len(bookResults.contracts), 2)
        self.assertEqual(len(bookResults.lines), 2)
        self.assertEqual(len(bookResults.greeks), 1)
        line0 = bookResults.lines[0]
        line1 = bookResults.lines[1]
        self.assertEqual(round(line0['value'], 3), 24.160)
        self.assertEqual(line0['underlying'], 'wti')
        self.assertEqual(line0['deliveryPeriod'], '2011-01-06')
        self.assertEqual(line0['error'], 0)
        self.assertEqual(line0['delta'], 1)
        self.assertEqual(round(line1['value'], 3), 14.160)
        self.assertEqual(line1['error'], 0)
        self.assertEqual(line1['delta'], 1)
        greeks0 = bookResults.greeks.values()[0]
        self.assertEqual(greeks0['delta'], 2)

    def createBook(self, *args, **kwds):
        if 'market' not in kwds:
            kwds['market'] = self.getMarket()
        return self.registry.books.create(*args, **kwds)

    def getMarket(self):
        return self.registry.markets.read(title='WTI (Mock)')


