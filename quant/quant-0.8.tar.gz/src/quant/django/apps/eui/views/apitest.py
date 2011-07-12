import unittest
from dm.view.testunit import TestCase
from quant.django.apps.eui.views.testbase import ViewTestCase
from quant.django.apps.eui.views.api import QuantApiView
from dm.webkit import HttpRequest
from dm.on import json
from dm.dictionarywords import URI_PREFIX
from dm.dictionarywords import SYSTEM_VERSION

def suite():
    suites = [
        unittest.makeSuite(TestApi),
        unittest.makeSuite(TestExchange),
        unittest.makeSuite(TestSymbol),
        unittest.makeSuite(TestMarket),
        unittest.makeSuite(TestImage),
        unittest.makeSuite(TestBook),
        unittest.makeSuite(TestDsl),
        unittest.makeSuite(TestResult),
    ]
    return unittest.TestSuite(suites)


class ApiViewTestCase(TestCase):

    viewClass = QuantApiView
    registerName = None
    updatedEntityKey = None

    def setUp(self):
        if not hasattr(self, 'apiKey'):
            person = self.registry.persons['admin']
            apiKeys = self.registry.apiKeys.findDomainObjects(person=person)
            if apiKeys:
                self.apiKey = apiKeys[0]
            else:
                self.apiKey = self.registry.apiKeys.create(person=person)

    def setRequestPath(self, path):
        self.requestPath = self.dictionary[URI_PREFIX] + '/api' + path

    def test_getResponse(self):
        self.failUnlessRegisterGet()
        self.failUnlessRegisterGetNotFound()
        self.failUnlessRegisterPost()
        self.failUnlessRegisterPostBadRequest()
        self.failUnlessRegisterPostNotFound()
        self.failUnlessRegisterPostConflict()
        self.failUnlessEntityGet()
        self.failUnlessEntityGetNotFound()
        self.failUnlessEntityPut()
        self.failUnlessEntityPutBadRequest()
        self.failUnlessEntityPutNotFound()
        self.failUnlessEntityPutConflict()

    def failUnlessRegisterGet(self):
        self.setRequestPath('/%s' % self.registerName)
        self.getResponse()
        self.failUnlessStatusCode(200)
        self.failUnlessDataIsInstance(list)

    def failUnlessRegisterGetNotFound(self):
        self.setRequestPath('/zzz%s' % self.registerName)
        self.getResponse()
        self.failUnlessStatusCode(404)

    def failUnlessRegisterPost(self):
        self.setRequestPath('/%s' % self.registerName)
        self.getResponse(self.newEntity)
        self.failUnlessStatusCode(201)
        self.failUnlessData(None)
        if 'Location' in self.response:
            self.lastLocationHeader = self.response['Location']
            self.entityKey = self.response['Location'].strip('/').split('/')[-1]
            if not self.updatedEntityKey:
                self.updatedEntityKey = self.entityKey

    def failUnlessRegisterPostBadRequest(self):
        self.setRequestPath('/%s' % self.registerName)
        self.getResponse({})
        self.failUnlessStatusCode(400)

    def failUnlessRegisterPostNotFound(self):
        self.setRequestPath('/zzz%s' % self.registerName)
        self.getResponse(self.newEntity)
        self.failUnlessStatusCode(404)

    def failUnlessRegisterPostConflict(self):
        pass

    def failUnlessEntityGet(self):
        self.setRequestPath('/%s/%s' % (self.registerName, self.entityKey))
        self.getResponse()
        self.failUnlessStatusCode(200)
        self.failUnlessDataIsInstance(dict)

    def failUnlessEntityGetNotFound(self):
        self.setRequestPath('/%s/zzz%s' % (self.registerName, self.entityKey))
        self.getResponse()
        self.failUnlessStatusCode(404)

    def failUnlessEntityPut(self):
        self.setRequestPath('/%s/%s' % (self.registerName, self.entityKey))
        self.getResponse(self.changedEntity)
        self.failUnlessStatusCode(200)
        self.failUnlessData(None)
        # Read the entity, check it has been updated.
        self.setRequestPath('/%s/%s' % (self.registerName, self.updatedEntityKey))
        self.getResponse()
        for name in self.changedEntity:
            self.failUnlessEqual(self.data[name], self.changedEntity[name])
        # Check the read entity data can be submitted as an update.
        self.getResponse(self.data)
        self.failUnlessStatusCode(200)
        self.failUnlessData(None)

    def failUnlessEntityPutBadRequest(self):
        pass

    def failUnlessEntityPutNotFound(self):
        pass

    def failUnlessEntityPutConflict(self):
        pass

    def getResponse(self, data=None):
        self.data = None
        view = self.viewClass(request=self.createRequest(data))
        self.response = view.getResponse()
        if self.response.content:
            try:
                self.data = json.loads(self.response.content)
            except Exception, inst:
                raise Exception, "Couldn't get data from content '%s': %s" % (self.response.content, inst)

    def createRequest(self, data=None):
        request = HttpRequest()
        request.path = self.requestPath
        if data != None:
            request.POST[json.dumps(data)] = 1
        request.META['HTTP_X_QUANT_API_KEY'] = self.apiKey.key
        return request

    def failUnlessStatusCode(self, expect=200):
        msg = "Status code '%s' not '%s' for path '%s'. %s" % (self.response.status_code, expect, self.requestPath, self.data)
        self.failUnlessEqual(self.response.status_code, expect, msg)

    def failUnlessData(self, expect):
        self.failUnlessEqual(self.data, expect)

    def failUnlessDataIsInstance(self, expect):
        msg = "Data '%s' is not instance of '%s'." % (self.data, expect)
        self.failUnless(isinstance(self.data, expect), msg)


class TestApi(ApiViewTestCase):

    def test_getResponse(self):
        self.setRequestPath('/')
        self.getResponse()
        self.failUnlessStatusCode(200)
        self.failUnlessData({'version': self.dictionary[SYSTEM_VERSION]})


class TestExchange(ApiViewTestCase):

    registerName = 'exchanges'
    newEntity = {'name': 'XXXX'}
    entityKey = 'XXXX'
    notFoundKey = 'ZZZZ'
    changedEntity = {'name': 'XXXXX'}
    updatedEntityKey = 'XXXXX'

    def tearDown(self):
        key = self.newEntity['name']
        if key in self.registry.exchanges:
            del(self.registry.exchanges[key])
        key = self.changedEntity['name']
        if key in self.registry.exchanges:
            del(self.registry.exchanges[key])
        super(TestExchange, self).tearDown()


class TestSymbol(ApiViewTestCase):

    registerName = 'symbols'
    newEntity = {'name': 'XX', 'exchange': 'NYMX'}
    entityKey = 'XX'
    notFoundKey = 'ZZ'
    changedEntity = {'name': 'XXX', 'exchange': 'NYMX'}
    updatedEntityKey = 'XXX'

    def tearDown(self):
        key = self.newEntity['name']
        if key in self.registry.symbols:
            del(self.registry.symbols[key])
        key = self.changedEntity['name']
        if key in self.registry.symbols:
            del(self.registry.symbols[key])
        super(TestSymbol, self).tearDown()

 
class TestMarket(ApiViewTestCase):

    registerName = 'markets'
    newEntity = {'symbol': 'CL', 'expiration': '2013-01-01', 'lastPrice': 123,
        'firstDeliveryDate': '2013-01-01'}
    entityKey = '1'
    changedEntity = {'symbol': 'HO', 'expiration': '2014-01-01', 'lastPrice': 124,
        'firstDeliveryDate': '2014-01-01'}


class TestImage(ApiViewTestCase):

    registerName = 'images'
    newEntity = {'priceProcess': 1, 'observationTime': '2011-01-01 00:00:00'}
    entityKey = '1'
    changedEntity = {'priceProcess': 1, 'observationTime': '2011-02-01 00:00:00'}

 
class TestBook(ApiViewTestCase):

    registerName = 'books'
    newEntity = {'title': 'Test'}
    entityKey = '1'
    changedEntity = {'title': 'Test2'}


class TestDsl(ApiViewTestCase):

    registerName = 'dsls'
    newEntity = {'specification':'Max(2, 3)', 'book': 1, 'title': 'Test'}
    entityKey = '1'
    changedEntity = {'specification':'4 * Max(2, 3)', 'book': 1, 'title': 'Test'}
    
    def setUp(self):
        super(TestDsl, self).setUp()
        self.book = self.registry.books.create()
        self.newEntity['book'] = self.book.id

    def tearDown(self):
        self.book.delete()
        super(TestDsl, self).tearDown()


class TestResult(ApiViewTestCase):
    registerName = 'results'
    newEntity = {'book': 1, 'image': 1}
    entityKey = '1'
    changedEntity = {'book': 1, 'image': 1}
    
