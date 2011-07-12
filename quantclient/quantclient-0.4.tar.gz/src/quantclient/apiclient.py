from dmclient.apiclient import ApiClient
from dmclient.apiclient import ResourceError
from dmclient.apiclient import ContentTypeError

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
        'Image Register': '/images',
        'Image Entity': '/images/%s',
        'Book Register': '/books',
        'Book Entity': '/books/%s',
        'Trade Register': '/%s',
        'Trade Entity': '/%s/%s',
        'Result Register': '/results',
        'Result Entity': '/results/%s',
        'Result Line Register': '/resultLines',
        'Result Line Entity': '/resultLines/%s',
    }

    def getApi(self):
        url = self.getUrl('Base')
        return self.createResponse(url)

    def getExchangeRegister(self):
        return self.getRegister('Exchange Register')

    def postExchangeRegister(self, data):
        return self.postRegister(data, 'Exchange Register')

    def getExchangeEntity(self, entityRef):
        return self.getEntity('Exchange Entity', entityRef)

    def putExchangeEntity(self, entityRef, data):
        return self.putEntity(data, 'Exchange Entity', entityRef)

    def getSymbolRegister(self):
        return self.getRegister('Symbol Register')

    def postSymbolRegister(self, data):
        return self.postRegister(data, 'Symbol Register')

    def getSymbolEntity(self, entityRef):
        return self.getEntity('Symbol Entity', entityRef)

    def putSymbolEntity(self, entityRef, data):
        return self.putEntity(data, 'Symbol Entity', entityRef)

    def getMarketRegister(self):
        return self.getRegister('Market Register')

    def postMarketRegister(self, data):
        return self.postRegister(data, 'Market Register')

    def getMarketEntity(self, entityRef):
        return self.getEntity('Market Entity', entityRef)

    def putMarketEntity(self, entityRef, data):
        return self.putEntity(data, 'Market Entity', entityRef)

    def getImageRegister(self):
        return self.getRegister('Image Register')

    def postImageRegister(self, data):
        return self.postRegister(data, 'Image Register')

    def getImageEntity(self, entityRef):
        return self.getEntity('Image Entity', entityRef)

    def putImageEntity(self, entityRef, data):
        return self.putEntity(data, 'Image Entity', entityRef)

    def getBookRegister(self):
        return self.getRegister('Book Register')

    def postBookRegister(self, data):
        return self.postRegister(data, 'Book Register')

    def getBookEntity(self, entityRef):
        return self.getEntity('Book Entity', entityRef)

    def putBookEntity(self, entityRef, data):
        return self.putEntity(data, 'Book Entity', entityRef)

    def getTradeRegister(self, registerName):
        return self.getRegister('Trade Register', registerName)

    def postTradeRegister(self, registerName, data):
        return self.postRegister(data, 'Trade Register', registerName)

    def getTradeEntity(self, registerName, entityRef):
        return self.getEntity('Trade Entity', registerName, entityRef)

    def putTradeEntity(self, registerName, entityRef, data):
        return self.putEntity(data, 'Trade Entity', registerName, entityRef)

    def getResultRegister(self):
        return self.getRegister('Result Register')

    def postResultRegister(self, data):
        return self.postRegister(data, 'Result Register')

    def getResultEntity(self, entityRef):
        return self.getEntity('Result Entity', entityRef)

    def putResultEntity(self, entityRef, data):
        return self.putEntity(data, 'Result Entity', entityRef)

    def getResultLineRegister(self):
        return self.getRegister('Result Line Register')

    def postResultLineRegister(self, data):
        return self.postRegister(data, 'Result Line Register')

    def getResultLineEntity(self, entityRef):
        return self.getEntity('Result Line Entity', entityRef)

    def putResultLineEntity(self, entityRef, data):
        return self.putEntity(data, 'Result Line Entity', entityRef)

