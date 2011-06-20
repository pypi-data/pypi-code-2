from kforge.django.apps.kui.views.projectHasMany import ProjectHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
from kforge.django.apps.kui.views import manipulator
from dm.webkit import webkitName, webkitVersion
from kforge.dictionarywords import *
from dm.view.base import HttpResponse

class ServiceView(ProjectHasManyView):

    hasManyClassName = 'Service'
            
    def __init__(self, **kwds):
        super(ServiceView, self).__init__(hasManyName='services', **kwds)

    def setContext(self):
        super(ServiceView, self).setContext()
        self.context.update({
            'service' : self.getAssociationObject(),
        })

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/project/%s/services/' % (
            self.domainObjectKey
        )

    def makePostManipulateLocation(self):
        return '/project/%s/services/' % (
            self.domainObjectKey
        )

    def serviceExtendsDomainModel(self):
        # Todo: Clear up, or explain this method's strange logic. :-)
        service = self.getAssociationObject()
        if not service:
            return False
        if not service.plugin.extendsDomainModel():
            return False
        return True
        
    def createDelayedRedirectResponse(self, transitionMsg):
        delay = self.dictionary[APACHE_WSGI_REDIRECT_DELAY]
        try:
            delay = str(int(delay.strip()))
        except:
            delay = '0'
        if int(delay) > 0 and self.redirectRequiresDelay():
            # Redirect after delay to allow server to restart.
            self.response = HttpResponse('Please wait a few moments (%ss) whilst your service is %s....' % (delay, transitionMsg))
            self.response.status_code = 200
            self.response['Refresh'] = '%s; url=%s' % (delay, self.redirect)
        else:
            super(ServiceView, self).createRedirectResponse()

    def isPostManipulationAndReloadingModWsgi(self):
        return self.isPostManipulation() and self.isReloadingModWsgi()

    def isPostManipulation(self):
        return self.getAssociationObject() and self.redirect == self.makePostManipulateLocation()

    def isReloadingModWsgi(self):
        isModWsgi = self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi'
        isReloading = self.dictionary[APACHE_RELOAD_CMD] and not self.dictionary[SKIP_APACHE_RELOAD]
        #isReloading = isReloading and 'apacheconfig' in self.registry.plugins
        return isModWsgi and isReloading

    isReloadingModWsgi = classmethod(isReloadingModWsgi)  
    # ... just because this method is used to configure tests. :-(


class ServiceListView(ServiceView, AbstractListHasManyView):

    templatePath = 'service/list'
         
    def canAccess(self):
        return self.canReadProject()


class ServiceCreateView(ServiceView, AbstractCreateHasManyView):

    templatePath = 'service/create'
    
    def canAccess(self):
        return self.canCreateService()
        
    def makePostManipulateLocation(self):
        if self.serviceExtendsDomainModel():
            return '/project/%s/services/%s/edit/' % (
                self.domainObjectKey,
                self.getAssociationObject().name
            )
        else:
            return '/project/%s/services/%s/' % (
                self.domainObjectKey,
                self.getAssociationObject().name
            )

    def getManipulatorClass(self):
        return manipulator.ServiceCreateManipulator

    # Todo: Create page template for this message, render and return as content.
    # Todo: Implement countdown timer for page refresh.
    # Todo: Show link to redirect (in case it doesn't work).
    # Todo: Make the redirect time delay configurable.
    def createRedirectResponse(self):
        self.createDelayedRedirectResponse('created')

    def redirectRequiresDelay(self):
        return self.isPostManipulationAndReloadingModWsgi()


class ServiceReadView(ServiceView, AbstractReadHasManyView):

    templatePath = 'service/read'

    def canAccess(self):
        return self.canReadService()

    def getStatusMessage(self):
        service = self.getAssociationObject()
        if service:
            statusMsg = service.getStatusMessage()
        else:
            statusMsg = "Not found"
        return statusMsg

    def getServiceUserHelp(self):
        service = self.getAssociationObject()
        if service:
            try:
                userHelp = service.getUserHelp(self.getServiceLocation())
            except Exception, inst:
                msg = "Error retrieving user help message: %s" % str(inst)
                self.logger.error(msg)
                return ''
            if webkitName == 'django' and webkitVersion == '1.0':
                from django.utils.safestring import mark_safe
                return mark_safe(userHelp)
            else:
                return userHelp
        return ''

    def setContext(self):
        super(ServiceReadView, self).setContext()
        self.context.update({
            'serviceLocation' : self.getServiceLocation(),
            'serviceUserHelp': self.getServiceUserHelp(),
        })

    def getServiceLocation(self):
        service = self.getAssociationObject()
        path = service.getUrlPath()
        host = self.request.META.get('SERVER_NAME', '')
        if host:
            if self.request.is_secure():
                protocol = 'https'
            else:
                protocol = 'http'
            return '%s://%s%s' % (protocol, host, path)
        else:
            return path
        

class ServiceUpdateView(ServiceView, AbstractUpdateHasManyView):

    templatePath = 'service/update'

    def __init__(self, *args, **kwds):
        super(ServiceUpdateView, self).__init__(*args, **kwds)
        self.initExtnView()

    def initExtnView(self):
        if self.serviceExtendsDomainModel():
            self.extnView = ServiceExtnUpdateView(
                request=self.request,
                domainObjectKey=self.domainObjectKey,
                hasManyKey=self.hasManyKey,
            )
        else:
            self.extnView = None

    def canAccess(self):
        return self.canUpdateService()

    def makePostManipulateLocation(self):
        return '/project/%s/services/%s/' % (
            self.domainObjectKey,
            self.getAssociationObject().name,
        )

    def getManipulatorClass(self):
        return manipulator.ServiceUpdateManipulator

    def getFormErrors(self):
        formErrors = super(ServiceUpdateView, self).getFormErrors()
        if self.extnView:
            extnFormErrors = self.extnView.getFormErrors()
            if extnFormErrors:
                formErrors.update(extnFormErrors)
        return formErrors

    def manipulateDomainObject(self):
        super(ServiceUpdateView, self).manipulateDomainObject()
        # Call extention's takeAction() now, so its form errors are involved.
        if self.extnView:
            self.extnView.takeAction()

    def setContext(self):
        super(ServiceUpdateView, self).setContext()
        if self.extnView:
            form = self.extnView.getForm()
            self.context.update({
                'extnForm'       : form,
            })

    def createRedirectResponse(self):
        self.createDelayedRedirectResponse('updated')

    def redirectRequiresDelay(self):
        return self.isPostManipulationAndReloadingModWsgi()


class ServiceExtnUpdateView(ServiceView, AbstractUpdateHasManyView):

    templatePath = 'serviceExtn/update'

    def getManipulatorClass(self):
        return manipulator.ServiceExtnManipulator

    def getManipulatedObjectRegister(self):
        service = self.getAssociationObject()
        return service.getExtnRegister()

    def getManipulatedDomainObject(self):
        service = self.getAssociationObject()
        return service.getExtnObject()

    def makePostManipulateLocation(self):
        return '/project/%s/services/%s/' % (
            self.domainObjectKey,
            self.hasManyKey,
        )


class ServiceDeleteView(ServiceView, AbstractDeleteHasManyView):

    templatePath = 'service/delete'

    def canAccess(self):
        return self.canDeleteService()

    def createRedirectResponse(self):
        self.createDelayedRedirectResponse('deleted')

    def redirectRequiresDelay(self):
        return self.isPostManipulationAndReloadingModWsgi()


def list(request, projectName=''):
    view = ServiceListView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()

def create(request, projectName):
    view = ServiceCreateView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def read(request, projectName, serviceName):
    view = ServiceReadView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()
    
def update(request, projectName, serviceName):
    view = ServiceUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()
    
def delete(request, projectName, serviceName):
    view = ServiceDeleteView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()

