from dmclient.apiclient import ApiClient

class QuantApiClient(ApiClient):

    apiKeyHeaderName = 'X-Quant-API-Key'
    resourcePaths = {
        'Base': '',
        'Exchange Register': '/exchanges',
        'Exchange Entity': '/exchanges/%s',
        'Symbol Register': '/symbols',
        'Symbol Entity': '/symbols/%s',
        'Market Register': '/markets',
        'Market Entity': '/markets/%s',
    }

    def getApi(self):
        url = self.getUrl('Base')
        return self.createResponse(url)

    def getExchangeRegister(self):
        return self.getRegister('Exchange Register')

    def postExchangeRegister(self, data):
        return self.postRegister('Exchange Register', data)

    def getExchangeEntity(self, entityRef):
        return self.getEntity('Exchange Entity', entityRef)

    def putExchangeEntity(self, entityRef, data):
        return self.putEntity('Exchange Entity', entityRef, data)

    def getSymbolRegister(self):
        return self.getRegister('Symbol Register')

    def postSymbolRegister(self, data):
        return self.postRegister('Symbol Register', data)

    def getSymbolEntity(self, entityRef):
        return self.getEntity('Symbol Entity', entityRef)

    def putSymbolEntity(self, entityRef, data):
        return self.putEntity('Symbol Entity', entityRef, data)

    def getMarketRegister(self):
        return self.getRegister('Market Register')

    def postMarketRegister(self, data):
        return self.postRegister('Market Register', data)

    def getMarketEntity(self, entityRef):
        return self.getEntity('Market Entity', entityRef)

    def putMarketEntity(self, entityRef, date):
        return self.putEntity('Market Entity', entityRef, data)

