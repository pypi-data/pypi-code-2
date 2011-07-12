import unittest
import os
import sys
from quantclient.apiclient import QuantApiClient
from quantclient.apiclient import ResourceError
import random

class TestQuantClient(unittest.TestCase):

    randint = random.randint(100000, 999999)

    def setUp(self):
        apiKey = os.environ['QUANT_API_KEY']
        self.client = QuantApiClient('http://quant.dev.localhost/api', apiKey=apiKey)

    def testExchanges(self):
        name = str(self.randint)
        exchange = {'name': name}
        # Get exchange register.
        exchanges = self.client.getExchangeRegister()
        self.failUnlessEqual(type(exchanges), list)
        self.failUnless('NYMX' in exchanges, exchanges)
        # Post exchange register.
        self.client.postExchangeRegister(exchange)
        exchanges = self.client.getExchangeRegister()
        self.failUnless(name in exchanges)
        # Post exchange register errors.
        self.failUnlessRaises(ResourceError, self.client.postExchangeRegister, {})
        self.failUnlessRaises(ResourceError, self.client.postExchangeRegister, exchange)
        # Get exchange entity.
        exchange = self.client.getExchangeEntity(name)
        self.failUnlessEqual(type(exchange), dict)
        self.failUnlessEqual(exchange['name'], name)
        self.failUnless('symbols' in exchange, exchange.keys())
        # Put exchange entity - unchanged.
        self.client.putExchangeEntity(name, exchange)
        self.client.getExchangeEntity(name)
        # Put exchange entity.
        exchange['name'] = name + 'adjusted'
        self.client.putExchangeEntity(name, exchange)
        self.client.getExchangeEntity(name + 'adjusted')

    def testSymbols(self):
        name = str(self.randint)
        symbol = {'name': name, 'exchange': 'NYMX'}
        name = str(self.randint)
        # Get symbol register.
        symbols = self.client.getSymbolRegister()
        self.failUnlessEqual(type(symbols), list)
        self.failUnless('CL' in symbols, symbols)
        # Post symbol register.
        self.client.postSymbolRegister(symbol)
        symbols = self.client.getSymbolRegister()
        self.failUnless(name in symbols)
        # Post symbol register errors.
        self.failUnlessRaises(ResourceError, self.client.postSymbolRegister, {})
        self.failUnlessRaises(ResourceError, self.client.postSymbolRegister, symbol)
        # Get symbol entity.
        symbol = self.client.getSymbolEntity(name)
        self.failUnlessEqual(type(symbol), dict)
        self.failUnlessEqual(symbol['name'], name)
        # Put symbol entity - unchanged.
        self.client.putSymbolEntity(name, symbol)
        self.client.getSymbolEntity(name)
        # Put symbol entity.
        symbol['name'] = name + 'adjusted'
        self.client.putSymbolEntity(name, symbol)
        self.client.getSymbolEntity(name + 'adjusted')

    def testMarkets(self):
        name = str(self.randint)[0:2]
        date = '2012-0%s-0%s' % (random.randint(1,9), random.randint(1,9))
        market = {'symbol': 'CL', 'expiration': date, 'firstDeliveryDate': date, 'lastPrice': 10}
        name = str(self.randint)
        # Get market register.
        markets = self.client.getMarketRegister()
        self.failUnlessEqual(type(markets), list)
        # Post market register.
        self.client.postMarketRegister(market)
        self.failUnless(self.client.lastCreatedLocation)
        marketId = int(self.client.lastCreatedLocation.strip().split('/')[-1])
        markets = self.client.getMarketRegister()
        self.failUnless(marketId in markets, (marketId, markets))
        # Post market register errors.
        self.failUnlessRaises(ResourceError, self.client.postMarketRegister, {})
        self.failUnlessRaises(ResourceError, self.client.postMarketRegister, market)
        # Get market entity.
        market = self.client.getMarketEntity(marketId)
        self.failUnlessEqual(type(market), dict)
        self.failUnlessEqual(market['expiration'], unicode(date))
        self.failUnlessEqual(market['lastPrice'], 10)
        # Put market entity - unchanged.
        self.client.putMarketEntity(marketId, market)
        self.client.getMarketEntity(marketId)
        # Put market entity.
        market['lastPrice'] = 11
        self.client.putMarketEntity(marketId, market)
        market = self.client.getMarketEntity(marketId)
        self.failUnlessEqual(market['lastPrice'], 11)

    def testImages(self):
        name = str(self.randint)[0:2]
        date = '2012-0%s-0%s 00:00:00' % (random.randint(1,9), random.randint(1,9))
        image = {'observationTime': date, 'priceProcess': 1}
        name = str(self.randint)
        # Get image register.
        images = self.client.getImageRegister()
        self.failUnlessEqual(type(images), list)
        # Post image register.
        self.client.postImageRegister(image)
        self.failUnless(self.client.lastCreatedLocation)
        imageId = int(self.client.lastCreatedLocation.strip().split('/')[-1])
        images = self.client.getImageRegister()
        self.failUnless(imageId in images, (imageId, images))
        # Post image register errors.
        self.failUnlessRaises(ResourceError, self.client.postImageRegister, {})
        # Get image entity.
        image = self.client.getImageEntity(imageId)
        self.failUnlessEqual(type(image), dict)
        self.failUnlessEqual(image['observationTime'], unicode(date))
        # Put image entity - unchanged.
        self.client.putImageEntity(imageId, image)
        self.client.getImageEntity(imageId)
        # Put image entity.
        newDate = date.replace('2012', '2013')
        image['observationTime'] = newDate
        self.client.putImageEntity(imageId, image)
        image = self.client.getImageEntity(imageId)
        self.failUnlessEqual(image['observationTime'], newDate)

    def testBooks(self):
        title = str(self.randint)
        book = {'title': title}
        # Get book register.
        books = self.client.getBookRegister()
        self.failUnlessEqual(type(books), list)
        # Post book register.
        self.client.postBookRegister(book)
        self.failUnless(self.client.lastCreatedLocation)
        bookId = int(self.client.lastCreatedLocation.strip().split('/')[-1])
        books = self.client.getBookRegister()
        self.failUnless(bookId in books, (bookId, books))
        # Post book register errors.
        self.failUnlessRaises(ResourceError, self.client.postBookRegister, {})
        # Get book entity.
        book = self.client.getBookEntity(bookId)
        self.failUnlessEqual(type(book), dict)
        self.failUnlessEqual(book['title'], title)
        # Put book entity - unchanged.
        self.client.putBookEntity(bookId, book)
        self.client.getBookEntity(bookId)
        # Put book entity.
        newTitle = title + 'adjusted'
        book['title'] = newTitle
        self.client.putBookEntity(bookId, book)
        book = self.client.getBookEntity(bookId)
        self.failUnlessEqual(book['title'], newTitle)

    def testTrades(self):
        # Just test the DSL contract type for now.
        title = str(self.randint)
        trade = {'title': title, 'specification': '3+3', 'book': 1}
        # Get trade register.
        trades = self.client.getTradeRegister('dsls')
        self.failUnlessEqual(type(trades), list)
        # Post trade register.
        self.client.postTradeRegister('dsls', trade)
        self.failUnless(self.client.lastCreatedLocation)
        tradeId = int(self.client.lastCreatedLocation.strip().split('/')[-1])
        trades = self.client.getTradeRegister('dsls')
        self.failUnless(tradeId in trades, (tradeId, trades))
        # Post trade register errors.
        self.failUnlessRaises(ResourceError, self.client.postTradeRegister, 'dsls', {})
        # Get trade entity.
        trade = self.client.getTradeEntity('dsls', tradeId)
        self.failUnlessEqual(type(trade), dict)
        self.failUnlessEqual(trade['book'], 1)
        # Put trade entity - unchanged.
        self.client.putTradeEntity('dsls', tradeId, trade)
        self.client.getTradeEntity('dsls', tradeId)
        # Put trade entity.
        newTitle = title + 'adjusted'
        trade['title'] = newTitle
        self.client.putTradeEntity('dsls', tradeId, trade)
        trade = self.client.getTradeEntity('dsls', tradeId)
        self.failUnlessEqual(trade['title'], newTitle)

    def testResults(self):
        title = str(self.randint)
        result = {'book': 1, 'image': 1}
        # Get result register.
        results = self.client.getResultRegister()
        self.failUnlessEqual(type(results), list)
        # Post result register.
        self.client.postResultRegister(result)
        self.failUnless(self.client.lastCreatedLocation)
        resultId = int(self.client.lastCreatedLocation.strip().split('/')[-1])
        results = self.client.getResultRegister()
        self.failUnless(resultId in results, (resultId, results))
        # Post result register errors.
        self.failUnlessRaises(ResourceError, self.client.postResultRegister, {})
        # Get result entity.
        result = self.client.getResultEntity(resultId)
        self.failUnlessEqual(type(result), dict)
        self.failUnlessEqual(result['book'], 1)
        # Put result entity - unchanged.
        self.client.putResultEntity(resultId, result)
        self.client.getResultEntity(resultId)
        # Put result entity.




if __name__ == "__main__":
    unittest.main(defaultTest='TestQuantClient')

