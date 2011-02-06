import unittest
from dm.view.testunit import TestCase
from dm.view.base import *
from dm.ioc import *
from dm.exceptions import *
from dm.strategy import MakeCookieString
from dm.util.datastructure import MultiValueDict
from dm.webkit import HttpRequest
from dm.dictionarywords import WEBKIT_NAME

def suite():
    suites = [
        unittest.makeSuite(TestSessionView),
        unittest.makeSuite(TestAbstractClassView),
        unittest.makeSuite(TestAbstractInstanceView),
        unittest.makeSuite(TestAbstractFormView),
        unittest.makeSuite(TestAbstractHasManyView),
        unittest.makeSuite(TestAbstractListView),
        unittest.makeSuite(TestAbstractSearchView),
        unittest.makeSuite(TestAbstractCreateView),
        unittest.makeSuite(TestAbstractReadView),
        unittest.makeSuite(TestAbstractUpdateView),
        unittest.makeSuite(TestAbstractDeleteView),
    ]
    return unittest.TestSuite(suites)


class ViewTestCase(TestCase):
    """Base class for testing View classes.

    View objects present a fairly simple interface: they are normally
    constructed with a request object and other parameters taken from an
    incoming HTTP request to a Web server. Testing view classes involves
    synthesizing the request object and other parameters, constructing the
    view with them, calling the response, and checking the resulting state.
    
    The ViewTestCase templates a test method, a setUp method, and a
    tearDown method. Class variables allow concrete view test cases to
    configure the requested and expected values. Rather than repetitions of
    the view create/call cycle code, concrete view test cases are concise
    declarations of differences from the basic routine. At the same time, the
    test method can be extended to check any extended behaviour of the form.

    For example, if the 'viewerName' attribute is set on a view-under-test, a
    session for that person will be created directly in the model, and its 
    session key will be encoded and set as a cookie in the request. The view-
    under-test will receive the session key, and behave as if the person was
    logged in. Other attributes are described below.

    The test method 'test_getResponse()' . It uses the class
    variables (listed below) to set things up. It calls getResponse() on the
    instatiated view, and checks the resulting state of the view.

    viewerName: The name of the person to be "logged in" (inspires session).
    viewClass:  View class under test.
    viewKwds: Dict passed to the view class constructor (norm. by resolver).
    requestPath: Path passed to view class constructor (norm. by resolver).
    COOKIES: MultiValueDict of get parameters passed to the view.
    GET: MultiValueDict of get parameters passed to the view.
    POST: MultiValueDict of get parameters passed to the view.
    requiredViewContext: Expected value of view.context.
    requiredResponseClassName: Expected name of type of response.
    requiredResponseContent: Expected content fragment (str or dict of strs).
    requiredRedirect: Expected redirect destination (no return path).
    requiredRedirectPath: Expected path for redirection (includes return path).
    requiredFormErrors: Expected form errors (boolean or list of strings).
    """

    viewerName = None
    viewClass = None
    viewKwds = {}
    requestPath = ''
    GET = MultiValueDict()
    POST = MultiValueDict()
    COOKIES = MultiValueDict()
    requiredViewContext = None
    requiredResponseClassName = 'HttpResponse'
    requiredResponseContent = None
    requiredRedirect = ''
    requiredRedirectPath = ''
    requiredFormErrors = None
    URI_PREFIX = TestCase.dictionary[TestCase.dictionary.words.URI_PREFIX]

    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.response = None
        self.viewSession = None
        self.initViewSession()
        self.COOKIES = self.COOKIES.copy()
        self.POST = self.POST.copy()
        self.GET = self.GET.copy()
        self.initCookies()
        self.initPost()
        self.initGet()
        self.request = self.buildRequest()
        self.view = self.buildView()
        self.failUnless(self.view)
        self.failUnless(self.view.dictionary, "No system dictionary.")
        self.failUnless(self.view.logger, "No logger.")

    def initViewSession(self):
        if self.viewerName:
            viewer = self.registry.persons[self.viewerName]
            self.viewSession = viewer.sessions.create()

    def initCookies(self):
        if self.viewSession != None:
            self.initAuthCookie()

    def initAuthCookie(self):
        cookieName = self.dictionary['auth_cookie_name']
        cookieStringStrategy = MakeCookieString(self.viewSession.key)
        cookieString = cookieStringStrategy.make()
        self.COOKIES[cookieName] = cookieString

    def initPost(self):
        pass

    def initGet(self):
        pass

    def buildRequest(self):
        request = HttpRequest()
        request.GET = self.GET.copy()
        request.POST = self.POST.copy()
        request.COOKIES = self.COOKIES.copy()
        request.path = self.requestPath
        return request

    def buildView(self):
        if not self.viewClass:
            raise "No viewClass set on test class %s" % self.__class__.__name__
        viewKwds = self.createViewKwds()
        return self.viewClass(**viewKwds)

    def createViewKwds(self):
        """Generates viewKwds, starting with a copy of the class's value."""
        viewKwds = self.viewKwds.copy()
        viewKwds['request'] = self.request
        return viewKwds

    def tearDown(self):
        self.view = None
        if self.viewSession:
            self.viewSession.delete()

    def test_getResponse(self):
        self.response = self.view.getResponse()
        self.failUnless(self.response, "No response?")
        self.checkFormErrors()
        self.checkViewContext()
        self.checkResponseContent()
        self.checkResponseClass()
        self.failUnlessEqual(self.view.redirect, self.requiredRedirect)
        self.failUnlessEqual(self.view.redirectPath, self.requiredRedirectPath)

    def checkResponseClass(self):
        self.failUnlessEqual(self.response.__class__.__name__, self.requiredResponseClassName,
            "'%s' fails required '%s':\n\n%s" % (
                self.response.__class__.__name__, self.requiredResponseClassName, self.response
            )
        )

    def checkFormErrors(self):
        self.failUnlessFormErrors()

    def failUnlessFormErrors(self):
        if self.requiredFormErrors != None:
            formErrors = self.view.formErrors
            if type(self.requiredFormErrors) == bool:
                errmsg = "%s => %s failed required %s" % (repr(formErrors), bool(formErrors), self.requiredFormErrors)
                self.failUnlessEqual(bool(formErrors), self.requiredFormErrors, errmsg)
            elif type(self.requiredFormErrors) == list:
                errmsg = "%s failed required %s" % (repr(formErrors), self.requiredFormErrors)
                for error in self.requiredFormErrors:
                    self.failUnless(error in repr(formErrors), errmsg + " ----> " + error)
            else:
                errmsg = "%s failed required %s" % (repr(formErrors), self.requiredFormErrors)
                self.failUnless(self.requiredFormErrors in repr(formErrors), errmsg)

    def checkResponseContent(self):
        self.failUnlessResponseContent()

    def failUnlessResponseContent(self):
        if self.requiredResponseContent != None:
            requiredContent = self.requiredResponseContent
            actualContent = self.response.content
            if issubclass(type(requiredContent), basestring):
                self.failUnless(requiredContent in actualContent, "%s %s" % (
                    repr(requiredContent), repr(actualContent)
                ))
            else:
                for fragment in requiredContent:
                    self.failUnless(fragment in actualContent, "%s %s" % (
                        repr(fragment), repr(actualContent)
                    ))

    def checkViewContext(self):
        self.failUnlessViewContext()

    def failUnlessViewContext(self):
        for (name, value) in self.getRequiredViewContext().items():
            self.failUnless(self.view.context.has_key(name), "Name '%s' not in context: %s" % (name, self.view.context))
            contextValue = self.view.context[name]
            self.failUnlessEqual(value, contextValue)

    def getRequiredViewContext(self):
        return {}


class MockView(ControlledAccessView):

    def assertActionObjectAuthorised(self, *args, **kwds):
        raise KforgePersonActionObjectDeclined

class MockSessionView(MockView, SessionView):
    pass

class MockAbstractClassView(MockView, AbstractClassView):
    pass

class MockAbstractInstanceView(MockView, AbstractInstanceView):
    pass

class MockAbstractFormView(MockView, AbstractFormView):
    pass

class MockAbstractHasManyView(MockView, AbstractHasManyView):
    pass

class MockAbstractListView(MockView, AbstractListView):
    pass

class MockAbstractSearchView(MockView, AbstractSearchView):
    pass

class MockAbstractCreateView(MockView, AbstractCreateView):
    pass

class MockAbstractReadView(MockView, AbstractReadView):

    domainClassName = 'Person'
    domainObjectKey = 'admin'


class MockAbstractUpdateView(MockView, AbstractUpdateView):
    pass

class MockAbstractDeleteView(MockView, AbstractDeleteView):
    pass


class TestSessionView(ViewTestCase):

    viewClass = MockSessionView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'

    def test_authoriseActionObject(self):
        object = None
#        self.failIf(self.view.authoriseActionObject('Read', object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.authoriseActionObject('Create', object))
#        self.failUnless(self.view.authoriseActionObject('Read', object))
#        self.failIf(self.view.authoriseActionObject('Update', object))
#        self.failIf(self.view.authoriseActionObject('Delete', object))
#        object = self.registry.getDomainClass('Person')
#        self.failUnless(self.view.authoriseActionObject('Create', object))
#        self.failUnless(self.view.authoriseActionObject('Read', object))
#        self.failIf(self.view.authoriseActionObject('Update', object))
#        self.failIf(self.view.authoriseActionObject('Delete', object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.authoriseActionObject('Create', object))
#        self.failUnless(self.view.authoriseActionObject('Read', object))
#        self.failIf(self.view.authoriseActionObject('Update', object))
#        self.failIf(self.view.authoriseActionObject('Delete', object))

    def test_canRead(self):
        object = None
        self.failIf(self.view.canRead(object))
#        object = self.registry.getDomainClass('Project')
#        self.failUnless(self.view.canRead(object))
#        object = self.registry.getDomainClass('Person')
#        self.failUnless(self.view.canRead(object))
#        object = self.registry.getDomainClass('Member')
#        self.failUnless(self.view.canRead(object))
#        object = self.registry.getDomainClass('Service')
#        self.failUnless(self.view.canRead(object))

    def test_canCreate(self):
        object = None
        self.failIf(self.view.canCreate(object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.canCreate(object))
#        object = self.registry.getDomainClass('Person')
#        self.failUnless(self.view.canCreate(object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.canCreate(object))

    def test_canUpdate(self):
        object = None
        self.failIf(self.view.canUpdate(object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.canUpdate(object))
#        object = self.registry.getDomainClass('Person')
#        self.failIf(self.view.canUpdate(object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.canUpdate(object))

    def test_canDelete(self):
        object = None
        self.failIf(self.view.canDelete(object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.canDelete(object))
#        object = self.registry.getDomainClass('Person')
#        self.failIf(self.view.canDelete(object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.canDelete(object))



class TestAbstractClassView(ViewTestCase):

    viewClass = MockAbstractClassView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractInstanceView(ViewTestCase):

    viewClass = MockAbstractInstanceView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractFormView(ViewTestCase):

    viewClass = MockAbstractFormView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractHasManyView(ViewTestCase):

    viewClass = MockAbstractHasManyView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractListView(ViewTestCase):

    viewClass = MockAbstractListView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractSearchView(ViewTestCase):

    viewClass = MockAbstractSearchView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractCreateView(ViewTestCase):

    viewClass = MockAbstractCreateView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractReadView(ViewTestCase):

    viewClass = MockAbstractReadView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'

    def test_getNextDomainObject(self):
        self.failUnlessEqual(self.view.domainClassName, 'Person')
        self.failUnlessEqual(self.view.domainObjectKey, 'admin')
        self.failUnless(self.view.getManipulatedDomainObject())
        self.failUnless(self.view.getNextDomainObject())

    def test_getPreviousDomainObject(self):
        self.failUnlessEqual(self.view.domainClassName, 'Person')
        self.failUnlessEqual(self.view.domainObjectKey, 'admin')
        self.failUnless(self.view.getManipulatedDomainObject())
        self.failIf(self.view.getPreviousDomainObject())

    def test_getPreviousNextDomainObjects(self):
        self.failUnlessEqual(self.view.domainClassName, 'Person')
        self.failUnlessEqual(self.view.domainObjectKey, 'admin')
        self.failUnless(self.view.getManipulatedDomainObject())
        (previous, next) = self.view.getPreviousNextDomainObjects()
        self.failIf(previous)
        self.failUnless(next)


class TestAbstractUpdateView(ViewTestCase):

    viewClass = MockAbstractUpdateView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractDeleteView(ViewTestCase):

    viewClass = MockAbstractDeleteView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class AdminSessionViewTestCase(ViewTestCase):

    viewerName = 'admin'

