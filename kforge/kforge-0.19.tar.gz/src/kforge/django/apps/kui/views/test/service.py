import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.service import ServiceListView
from kforge.django.apps.kui.views.service import ServiceCreateView
from kforge.django.apps.kui.views.service import ServiceReadView
from kforge.django.apps.kui.views.service import ServiceUpdateView
from kforge.django.apps.kui.views.service import ServiceDeleteView
from kforge.django.apps.kui.views.service import ServiceView
from dm.util.datastructure import MultiValueDict

# Todo: Indicate whether apache restarted since service was created
# so that the user knows whether a new service will respond.

# Todo: Redirect delay for service update and delete.

def suite():
    suites = [
        unittest.makeSuite(TestServiceListView),
        unittest.makeSuite(TestServiceListViewNatasha),
        unittest.makeSuite(TestServiceCreateView),
        unittest.makeSuite(TestServiceCreateViewNatasha),
        unittest.makeSuite(TestServiceCreateViewNatashaPOST),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTErrorInUse),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTErrorRequired),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTErrorInvalid),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTSvn),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTTrac),
        unittest.makeSuite(TestServiceReadView),
        unittest.makeSuite(TestServiceReadViewNatasha),
        unittest.makeSuite(TestServiceUpdateView),
        unittest.makeSuite(TestServiceUpdateViewNatasha),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOST),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTTrac),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTTracSvn),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTTracHg),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTErrorInUse),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTErrorRequired),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTErrorInvalid),
        unittest.makeSuite(TestServiceDeleteView),
        unittest.makeSuite(TestServiceDeleteViewNatasha),
        unittest.makeSuite(TestServiceDeleteViewNatashaPOST),
    ]
    return unittest.TestSuite(suites)


class ServiceTestCase(ViewTestCase):

    projectName = 'warandpeace'

    def createViewKwds(self):
        viewKwds = super(ServiceTestCase, self).createViewKwds()
        viewKwds['domainObjectKey'] = self.projectName
        if hasattr(self, 'serviceName'):
            viewKwds['hasManyKey'] = self.serviceName
        return viewKwds


class TestServiceListView(ServiceTestCase):

    viewClass = ServiceListView

    def test_canCreate(self):
        object = None
        self.failIf(self.view.canCreateService())

    def test_canRead(self):
        object = None
        self.failUnless(self.view.canReadService())

    def test_canUpdate(self):
        object = None
        self.failIf(self.view.canUpdateService())

    def test_canDelete(self):
        object = None
        self.failIf(self.view.canDeleteService())


class TestServiceListViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceListView

    def test_canCreate(self):
        object = None
        self.failUnless(self.view.canCreateService())

    def test_canRead(self):
        object = None
        self.failUnless(self.view.canReadService())

    def test_canUpdate(self):
        object = None
        self.failUnless(self.view.canUpdateService())

    def test_canDelete(self):
        object = None
        self.failUnless(self.view.canDeleteService())


class TestServiceCreateView(ServiceTestCase):

    viewClass = ServiceCreateView
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX 
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceCreateViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'


class TestServiceCreateViewNatashaPOSTErrorInUse(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['example'], 'plugin': ['example']})
    requiredFormErrors = "A service called 'example' already exists. Please choose another service name."
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''


class TestServiceCreateViewNatashaPOSTErrorRequired(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': [''], 'plugin': ['example']})
    requiredFormErrors = ['name', 'This field is required.']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''


class TestServiceCreateViewNatashaPOSTErrorInvalid(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['/'], 'plugin': ['example']})
    requiredFormErrors = ['name', 'Enter a valid value.']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''

class TestServiceCreateViewNatashaPOSTErrorInUse(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['example'], 'plugin': ['example']})
    requiredFormErrors = "A service called 'example' already exists. Please choose another service name."
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''

class TestServiceCreateViewNatashaPOST(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['example2'], 'plugin': ['example']})
    requiredRedirect = '/project/warandpeace/services/example2/'
    if ServiceView.isReloadingModWsgi():
        requiredResponseClassName = 'HttpResponse'
    else:
        requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def tearDown(self):
        super(TestServiceCreateViewNatashaPOST, self).tearDown()
        if 'example2' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['example2']
            service.delete()
            service.purge()


class TestServiceCreateViewNatashaPOSTSvn(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['svn'], 'plugin': ['svn']})
    requiredRedirect = '/project/warandpeace/services/svn/'
    if ServiceView.isReloadingModWsgi():
        requiredResponseClassName = 'HttpResponse'
    else:
        requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def setUp(self):
        super(TestServiceCreateViewNatashaPOSTSvn, self).setUp()
        if 'svn' in self.registry.plugins:
            self.enabledSvnPlugin = False
        else: 
            self.registry.plugins.create('svn')
            self.enabledSvnPlugin = True

    def tearDown(self):
        super(TestServiceCreateViewNatashaPOSTSvn, self).tearDown()
        if 'svn' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['svn']
            service.delete()
            service.purge()
        if self.enabledSvnPlugin:
            del(self.registry.plugins['svn'])


class TestServiceCreateViewNatashaPOSTTrac(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['trac'], 'plugin': ['trac']})
    requiredRedirect = '/project/warandpeace/services/trac/edit/'
    if ServiceView.isReloadingModWsgi():
        requiredResponseClassName = 'HttpResponse'
    else:
        requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def setUp(self):
        super(TestServiceCreateViewNatashaPOSTTrac, self).setUp()
        if 'trac' in self.registry.plugins:
            self.enabledTracPlugin = False
        else: 
            self.registry.plugins.create('trac')
            self.enabledTracPlugin = True

    def test_getResponse(self):
        super(TestServiceCreateViewNatashaPOSTTrac, self).test_getResponse()
        service = self.registry.projects[self.projectName].services['trac']
        tracProject = service.getExtnObject()
        self.failIf(tracProject.isEnvironmentInitialised, repr(tracProject))

    def tearDown(self):
        super(TestServiceCreateViewNatashaPOSTTrac, self).tearDown()
        if 'trac' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['trac']
            service.delete()
            service.purge()
        if self.enabledTracPlugin:
            del(self.registry.plugins['trac'])


class TestServiceReadView(ServiceTestCase):

    viewClass = ServiceReadView
    serviceName = 'example'


class TestServiceReadViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceReadView
    serviceName = 'example'


class TestServiceUpdateView(ServiceTestCase):

    viewClass = ServiceUpdateView
    serviceName = 'example'
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceUpdateViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example'
    viewClass = ServiceUpdateView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'


class TestServiceUpdateViewNatashaPOST(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example2'
    viewClass = ServiceUpdateView
    POST = MultiValueDict({'name': ['example3']})
    requiredRedirect = '/project/warandpeace/services/example3/'
    requiredResponseClassName = 'HttpResponseRedirect'
    if ServiceView.isReloadingModWsgi():
        requiredResponseClassName = 'HttpResponse'
    else:
        requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def setUp(self):
        if 'example2' not in self.registry.projects[self.projectName].services:
            plugin = self.registry.plugins['example']
            self.domainObject = self.registry.projects[self.projectName].services.create('example2', plugin=plugin)
        super(TestServiceUpdateViewNatashaPOST, self).setUp()

    def tearDown(self):
        super(TestServiceUpdateViewNatashaPOST, self).tearDown()
        if 'example2' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['example2']
            service.delete()
            service.purge()
        if 'example3' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['example3']
            service.delete()
            service.purge()


class TestServiceUpdateViewNatashaPOSTTrac(TestServiceUpdateViewNatashaPOST):
    # Check update trac service, without setting repository.

    serviceName = 'trac'
    requiredRedirect = ''
    POST = MultiValueDict({'name': ['trac1']})
    requiredRedirect = '/project/warandpeace/services/trac1/'

    def setUp(self):
        if 'svn' in self.registry.plugins:
            svnPlugin = self.registry.plugins['svn']
            self.enabledSvnPlugin = False
        else: 
            svnPlugin = self.registry.plugins.create('svn')
            self.enabledSvnPlugin = True
        if 'svn' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['svn']
                service.delete()
                service.purge()
        self.registry.projects[self.projectName].services.create('svn', plugin=svnPlugin)
        if 'trac' in self.registry.plugins:
            tracPlugin = self.registry.plugins['trac']
            self.enabledTracPlugin = False
        else: 
            tracPlugin = self.registry.plugins.create('trac')
            self.enabledTracPlugin = True
        if 'trac' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac']
                service.delete()
                service.purge()
        self.registry.projects[self.projectName].services.create('trac', plugin=tracPlugin)
        super(TestServiceUpdateViewNatashaPOSTTrac, self).setUp()
    
    def initPost(self):
        self.POST['name'] = 'trac1'

    def test_getResponse(self):
        super(TestServiceUpdateViewNatashaPOSTTrac, self).test_getResponse()
        service = self.registry.projects[self.projectName].services['trac1']
        tracProject = service.getExtnObject()
        self.failIf(tracProject.isEnvironmentInitialised, repr(tracProject))
        
    def tearDown(self):
        super(TestServiceUpdateViewNatashaPOSTTrac, self).tearDown()
        try:
            if 'trac' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac']
                service.delete()
                service.purge()
            if 'trac1' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac1']
                service.delete()
                service.purge()
            if 'svn' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['svn']
                service.delete()
                service.purge()
        finally:
            try:
                if self.enabledSvnPlugin:
                    plugin = self.registry.plugins['svn']
                    plugin.delete()
                    plugin.purge()
            finally:
                if self.enabledTracPlugin:
                    plugin = self.registry.plugins['trac']
                    plugin.delete()
                    plugin.purge()


class TestServiceUpdateViewNatashaPOSTTracSvn(TestServiceUpdateViewNatashaPOST):
    # Check update trac service, with setting repository (svn).

    serviceName = 'trac'
    requiredRedirect = ''
    POST = MultiValueDict({'name': ['trac']})
    requiredRedirect = '/project/warandpeace/services/trac/'

    def setUp(self):
        if 'svn' in self.registry.plugins:
            svnPlugin = self.registry.plugins['svn']
            self.enabledSvnPlugin = False
        else: 
            svnPlugin = self.registry.plugins.create('svn')
            self.enabledSvnPlugin = True
        if 'svn' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['svn']
                service.delete()
                service.purge()
        self.registry.projects[self.projectName].services.create('svn', plugin=svnPlugin)
        if 'trac' in self.registry.plugins:
            tracPlugin = self.registry.plugins['trac']
            self.enabledTracPlugin = False
        else: 
            tracPlugin = self.registry.plugins.create('trac')
            self.enabledTracPlugin = True
        if 'trac' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac']
                service.delete()
                service.purge()
        self.registry.projects[self.projectName].services.create('trac', plugin=tracPlugin)
        super(TestServiceUpdateViewNatashaPOSTTracSvn, self).setUp()
    
    def initPost(self):
        self.POST['svn'] = self.registry.projects[self.projectName].services['svn'].id

    def test_getResponse(self):
        super(TestServiceUpdateViewNatashaPOSTTracSvn, self).test_getResponse()
        service = self.registry.projects[self.projectName].services['trac']
        tracProject = service.getExtnObject()
        self.failUnless(tracProject.isEnvironmentInitialised, repr(tracProject))
        
    def tearDown(self):
        super(TestServiceUpdateViewNatashaPOSTTracSvn, self).tearDown()
        try:
            if 'trac' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac']
                service.delete()
                service.purge()
            if 'svn' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['svn']
                service.delete()
                service.purge()
        finally:
            try:
                if self.enabledSvnPlugin:
                    plugin = self.registry.plugins['svn']
                    plugin.delete()
                    plugin.purge()
            finally:
                if self.enabledTracPlugin:
                    plugin = self.registry.plugins['trac']
                    plugin.delete()
                    plugin.purge()


class TestServiceUpdateViewNatashaPOSTTracHg(TestServiceUpdateViewNatashaPOST):
    # Check update trac service, with setting repository (svn).

    serviceName = 'trac'
    requiredRedirect = ''
    POST = MultiValueDict({'name': ['trac']})
    requiredRedirect = '/project/warandpeace/services/trac/'

    def setUp(self):
        if 'mercurial' in self.registry.plugins:
            hgPlugin = self.registry.plugins['mercurial']
            self.enabledHgPlugin = False
        else: 
            hgPlugin = self.registry.plugins.create('mercurial')
            self.enabledHgPlugin = True
        if 'mercurial' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['mercurial']
                service.delete()
                service.purge()
        self.registry.projects[self.projectName].services.create('mercurial', plugin=hgPlugin)
        if 'trac' in self.registry.plugins:
            tracPlugin = self.registry.plugins['trac']
            self.enabledTracPlugin = False
        else: 
            tracPlugin = self.registry.plugins.create('trac')
            self.enabledTracPlugin = True
        if 'trac' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac']
                service.delete()
                service.purge()
        self.registry.projects[self.projectName].services.create('trac', plugin=tracPlugin)
        super(TestServiceUpdateViewNatashaPOSTTracHg, self).setUp()
    
    def initPost(self):
        self.POST['svn'] = self.registry.projects[self.projectName].services['mercurial'].id

    def test_getResponse(self):
        super(TestServiceUpdateViewNatashaPOSTTracHg, self).test_getResponse()
        service = self.registry.projects[self.projectName].services['trac']
        tracProject = service.getExtnObject()
        self.failUnless(tracProject.isEnvironmentInitialised, repr(tracProject))
        

    def tearDown(self):
        super(TestServiceUpdateViewNatashaPOSTTracHg, self).tearDown()
        try:
            if 'trac' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['trac']
                service.delete()
                service.purge()
            if 'mercurial' in self.registry.projects[self.projectName].services:
                service = self.registry.projects[self.projectName].services['mercurial']
                service.delete()
                service.purge()
        finally:
            try:
                if self.enabledHgPlugin:
                    plugin = self.registry.plugins['mercurial']
                    plugin.delete()
                    plugin.purge()
            finally:
                if self.enabledTracPlugin:
                    plugin = self.registry.plugins['trac']
                    plugin.delete()
                    plugin.purge()


class TestServiceUpdateViewNatashaPOSTErrorInUse(TestServiceUpdateViewNatashaPOST):

    POST = MultiValueDict({'name': ['example']})
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredFormErrors = "A service called 'example' already exists. Please choose another service name."
    

class TestServiceUpdateViewNatashaPOSTErrorRequired(TestServiceUpdateViewNatashaPOST):

    POST = MultiValueDict({'name': ['']})
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredFormErrors = ['name', 'This field is required.']
    

class TestServiceUpdateViewNatashaPOSTErrorInvalid(TestServiceUpdateViewNatashaPOST):

    POST = MultiValueDict({'name': [' ']})
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredFormErrors = ['name', 'Enter a valid value.']
    

class TestServiceDeleteView(ServiceTestCase):

    viewClass = ServiceDeleteView
    serviceName = 'example'
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceDeleteViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example'
    viewClass = ServiceDeleteView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'


class TestServiceDeleteViewNatashaPOST(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example2'
    viewClass = ServiceDeleteView
    POST = MultiValueDict({'Submit': ['submit']})
    requiredRedirect = '/project/warandpeace/services/'
    if ServiceView.isReloadingModWsgi():
        requiredResponseClassName = 'HttpResponse'
    else:
        requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def setUp(self):
        if 'example2' not in self.registry.projects[self.projectName].services:
            plugin = self.registry.plugins['example']
            self.domainObject = self.registry.projects[self.projectName].services.create('example2', plugin=plugin)
        super(TestServiceDeleteViewNatashaPOST, self).setUp()

    def tearDown(self):
        super(TestServiceDeleteViewNatashaPOST, self).tearDown()
        if 'example2' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['example2']
            service.delete()
            service.purge()
            self.fail("Project still has a service called 'example2'.")
