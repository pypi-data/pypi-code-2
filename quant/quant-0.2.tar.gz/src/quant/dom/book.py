from quant.dom.base import SimpleObject, String, HasMany, HasA
from quant.dom.results import BookResults

class Book(SimpleObject):

    isUnique = False

    title = String()
    market = HasA('Market')
    europeanOptions = HasMany('EuropeanOption', 'id')
    americanOptions = HasMany('AmericanOption', 'id')

    def getLabelValue(self):
        return self.title or self.id

    def getResults(self):
        if not hasattr(self, '__results'):
            self.__results = self.calcResults()
        return self.__results

    def calcResults(self):
        bookResults = BookResults()
        bookResults.evaluationDate = self.market.getNowTime()
        # Calculate contract results individually.
        for contract in self.getContracts():
            contractResults = contract.calcResults(market=self.market)
            bookResults.contracts.append(contractResults)
        # Compile contract results into book results.
        for contractResults in bookResults.contracts:
            for underlyingResults in contractResults.underlyings:
                for deliveryPeriodResults in underlyingResults.deliveryPeriods:
                    contractName = contractResults.name
                    underlyingName = underlyingResults.name
                    deliveryPeriodName = deliveryPeriodResults.name
                    pricerName = contractResults.pricer
                    value = deliveryPeriodResults.value
                    #raise Exception, deliveryPeriodResults.value
                    error = deliveryPeriodResults.error
                    delta = deliveryPeriodResults.delta
                    gamma = deliveryPeriodResults.gamma
                    vega = deliveryPeriodResults.vega
                    line = {'contract': contractName, 'underlying':underlyingName, 'deliveryPeriod':deliveryPeriodName, 'pricer':pricerName, 'value':value, 'error':error, 'delta':delta, 'gamma':gamma, 'vega':vega}
                    bookResults.lines.append(line)
               
        for line in bookResults.lines: 
            # Sum value across all lines.
            bookResults.value += line['value']
            # Sum greeks across all underlyings and delivery periods.
            subMarketKey = '%s %s' % (line['underlying'], line['deliveryPeriod'])
            if subMarketKey not in bookResults.greeks:
                subMarketResults = {'value':0, 'delta':0, 'gamma':0, 'vega':0}
                bookResults.greeks[subMarketKey] = subMarketResults 
            else:
                subMarketResults = bookResults.greeks[subMarketKey]
            subMarketResults['value'] += line['value']
            subMarketResults['delta'] += line['delta']
            subMarketResults['gamma'] += line['gamma']
            subMarketResults['vega'] += line['vega']
        return bookResults

    def getContracts(self):
        return list(self.europeanOptions) + list(self.americanOptions)

    def countContracts(self):
        return len(self.europeanOptions) + len(self.americanOptions)

    def delete(self):
        for contract in self.getContracts():
            contract.book = None
            contract.save()
        super(Book, self).delete()


