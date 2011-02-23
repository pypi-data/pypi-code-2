from dm.messagedigest import md5
from dm.ioc import *
from dm.exceptions import *
from dm.dictionarywords import *
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.view.manipulator import FormWrapper
from dm.strategy import MakeCheckString
from dm.strategy import MakeCookieString
from dm.strategy import ValidateCookieString
from dm.util.datastructure import MultiValueDict
from dm.webkit import HttpResponse
from dm.webkit import HttpResponseRedirect
from dm.webkit import Context
from dm.webkit import RequestContext
from dm.webkit import template_loader
import dm.times
import os

moddebug = False

class ControlledAccessView(object):

    responseStatusCode = 200
    accessController = RequiredFeature('AccessController')
    dictionary       = RequiredFeature('SystemDictionary')
    commands         = RequiredFeature('CommandSet')
    logger           = RequiredFeature('Logger')
    registry         = RequiredFeature('DomainRegistry')
    debug            = RequiredFeature('Debug')  # deprecated
    isDebug          = RequiredFeature('Debug')  # rename for debug
    systemMode       = RequiredFeature('SystemMode')

    authSessionCookieName = dictionary[AUTH_COOKIE_NAME]
    noAuthSessionCookieString = dictionary[NO_AUTH_COOKIE_NAME]
    if AUTH_COOKIE_DOMAIN in dictionary:
        authCookieDomain = dictionary[AUTH_COOKIE_DOMAIN]
    else:
        # Default to just matching requested domain.
        authCookieDomain = None  

    def __init__(self, request=None, masterView=None, **kwds):
        self.request = request
        self.masterView = masterView
        self.response = None
        self.path = None
        self.session = None
        # todo: clarify meaning of redirect and redirectPath
        self.redirect = ''
        self.redirectPath = ''
        self.returnPath = ''
        if self.isSlaveView():
            self.initFromMaster()

        # Todo: Clean up all this guff.
        self._canReadSystem = None
        self._canUpdateSystem = None
        self._canCreatePerson = None
        self._canApprovePerson = None
        self._canApprovePersons = None
        self._canReadPerson = None
        self._canReadPersons = None
        self._canUpdatePerson = None
        self._canDeletePerson = None
        self._canCreateProject = None
        self._canReadProject = None
        self._canUpdateProject = None
        self._canDeleteProject = None
        self._canCreateMember = None
        self._canReadMember = None
        self._canUpdateMember = None
        self._canDeleteMember = None
        self._canCreateService = None
        self._canReadService = None
        self._canUpdateService = None
        self._canDeleteService = None

    def initFromMaster(self):
        self.path = self.masterView.path
        self.session = self.masterView.session

    def isSlaveView(self):
        return self.masterView != None

    def getMethodName(self):
        if self.request.POST:
            return 'POST'
        else:
            return 'GET'
        
    def setSessionFromCookieString(self, cookieString):
        if not cookieString:
            msg = '%s: No authentication session cookie in request.' % self.__class__.__name__
            self.logger.error(msg)
            return
        if moddebug:
            self.logger.info(
                '%s: Resuming session from cookie %s...' % (
                    self.__class__.__name__, cookieString[0:10] 
                )
            )
        if cookieString == self.noAuthSessionCookieString:
            if moddebug:
                msg = '%s: Unauthenticated session cookie in request.' % self.__class__.__name__
                self.logger.debug(msg)
            return
        if moddebug:
            msg = '%s: Session cookie in request.' % (
                self.__class__.__name__
            )
            self.logger.debug(msg)
        try:
            sessionKey = self.makeSessionKeyFromCookieString(cookieString)
        except KforgeSessionCookieValueError:
            self.session = None
            self.logger.error(
                '%s: Session cookie value error: %s' % (self.__class__.__name__, cookieString)
            )
        else:
            try:
                self.session = self.findSession(sessionKey)
                if self.session:
                    self.session.updateLastVisited()
                    if moddebug:
                        self.logger.debug(
                            '%s: Session %s resumed from cookie.' % (
                                self.__class__.__name__, sessionKey
                            )
                        )
                else:
                    self.logger.error(
                        '%s: No session for key in cookie: %s' % (self.__class__.__name__, sessionKey)
                    )
                    self.isSessionStopping = True
            except Exception, inst:
                self.logger.error(
                    '%s: Error finding session: %s' % (self.__class__.__name__, cookieString)
                )
                self.isSessionStopping = True

    def makeSessionKeyFromCookieString(self, cookieString):
        validateCookieStrategy = ValidateCookieString(cookieString)
        plainString = validateCookieStrategy.validate()
        return plainString

    def makeCookieStringFromSessionKey(self, sessionKey):
        cookieStringStrategy = MakeCookieString(sessionKey)
        cookieString = cookieStringStrategy.make()
        return cookieString

    def makeCheckString(self, sessionKey):
        checkStringStrategy = MakeCheckString(sessionKey)
        checkString = checkStingSrategy.make()
        return checkString

    def findSession(self, sessionKey):
        try:
            return self.registry.sessions[sessionKey]
        except KforgeRegistryKeyError:
            return None

    def checkAccessControl(self):
        if self.canAccess():
            return True
        else:
            self.setRedirectAccessDenied()
            return False

    def canAccess(self):
        return False

    def authoriseActionObject(self, actionName, protectedObject):
        if self.session:
            person = self.session.person
        else:
            person = None
        return self.isAuthorised(
            person=person,
            actionName=actionName, 
            protectedObject=protectedObject
        )

    def isAuthorised(self, *args, **kwds):
        return self.accessController.isAuthorised(*args, **kwds)
    
    def canCreate(self, protectedObject):
        return self.authoriseActionObject('Create', protectedObject)

    def canApprove(self, protectedObject):
        return self.authoriseActionObject('Approve', protectedObject)

    def canRead(self, protectedObject):
        return self.authoriseActionObject('Read', protectedObject)

    def canUpdate(self, protectedObject):
        return self.authoriseActionObject('Update', protectedObject)

    def canDelete(self, protectedObject):
        return self.authoriseActionObject('Delete', protectedObject)

    def getDomainClass(self, domainClassName):
        if self.registry != None:
            return self.registry.getDomainClass(domainClassName)
        else:
            return None

    def canReadSystem(self):
        if self._canReadSystem == None:
            protectedObject = self.getDomainClass('System')
            self._canReadSystem = self.canRead(protectedObject)
        return self._canReadSystem

    def canUpdateSystem(self):
        if self._canUpdateSystem == None:
            protectedObject = self.getDomainClass('System')
            self._canUpdateSystem = self.canUpdate(protectedObject)
        return self._canUpdateSystem

    def canCreatePerson(self):
        if self._canCreatePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canCreatePerson = self.canCreate(protectedObject)
        return self._canCreatePerson

    def canApprovePerson(self):
        if self._canApprovePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canApprovePerson = self.canApprove(protectedObject)
        return self._canApprovePerson

    def canApprovePersons(self):
        if self._canApprovePersons == None:
            protectedObject = self.getDomainClass('Person')
            self._canApprovePersons = self.canApprove(protectedObject)
        return self._canApprovePersons

    def canReadPersons(self):
        if self._canReadPersons == None:
            protectedObject = self.getDomainClass('Person')
            self._canReadPersons = self.canRead(protectedObject)
        return self._canReadPersons

    def canReadPerson(self):
        if self._canReadPerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canReadPerson = self.canRead(protectedObject)
        return self._canReadPerson

    def canUpdatePerson(self):
        if self._canUpdatePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canUpdatePerson = self.canUpdate(protectedObject)
        return self._canUpdatePerson

    def canDeletePerson(self):
        if self._canDeletePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canDeletePerson = self.canDelete(protectedObject)
        return self._canDeletePerson

    def canCreateProject(self):
        if self._canCreateProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canCreateProject = self.canCreate(protectedObject)
        return self._canCreateProject

    def canReadProject(self):
        if self._canReadProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canReadProject = self.canRead(protectedObject)
        return self._canReadProject

    def canUpdateProject(self):
        if self._canUpdateProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canUpdateProject = self.canUpdate(protectedObject)
        return self._canUpdateProject

    def canDeleteProject(self):
        if self._canDeleteProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canDeleteProject = self.canDelete(protectedObject)
        return self._canDeleteProject

    def canCreateMember(self):
        if self._canCreateMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canCreateMember = self.canCreate(protectedObject)
        return self._canCreateMember

    def canReadMember(self):
        if self._canReadMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canReadMember = self.canRead(protectedObject)
        return self._canReadMember

    def canUpdateMember(self):
        if self._canUpdateMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canUpdateMember = self.canUpdate(protectedObject)
        return self._canUpdateMember

    def canDeleteMember(self):
        if self._canDeleteMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canDeleteMember = self.canDelete(protectedObject)
        return self._canDeleteMember

    def canCreateService(self):
        if self._canCreateService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canCreateService = self.canCreate(protectedObject)
        return self._canCreateService

    def canReadService(self):
        if self._canReadService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canReadService = self.canRead(protectedObject)
        return self._canReadService

    def canUpdateService(self):
        if self._canUpdateService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canUpdateService = self.canUpdate(protectedObject)
        return self._canUpdateService

    def canDeleteService(self):
        if self._canDeleteService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canDeleteService = self.canDelete(protectedObject)
        return self._canDeleteService

    def getResponse(self):
        msg = 'The getResponse() method is not implemented on class %s' % (
            self.__class__
        )
        return HttpResponse(msg)


class SessionView(ControlledAccessView):

    templatePath = None
    majorNavigation = []
    majorNavigationItem = "/"
    minorNavigation = []
    minorNavigationItem = "/"

    def __init__(self, **kwds):
        super(SessionView, self).__init__(**kwds)
        self.requestParams = None
        self.template = None
        self.context = None
        self.sessionCookieString = ''
        self.person = None
        self.project = None
        self.member = None
        self.service = None
        self.handlingStarted = dm.times.getLocalNow()
        self.readRequest()
        self.requiresCsrfToken = bool(RequestContext)

    def __repr__(self):
        return "<%s redirect='%s' redirectPath='%s'>" % (
            self.__class__.__name__, self.redirect, self.redirectPath
        )

    def readRequest(self):
        if not self.request:
            if moddebug:
                self.logger.info('%s: No request object.' % self.__class__.__name__)
            return
        self.setPathFromRequest()
        self.logger.info('%s: Handling %s request to path %s' % (
            self.__class__.__name__, self.getMethodName(), self.path
        ))
        self.readRequestSession()

    def setPathFromRequest(self):
        if self.path != None:
            return
        uriPrefix = self.dictionary[URI_PREFIX]
        requestPath = self.request.path 
        if uriPrefix and requestPath.startswith(uriPrefix):
            self.path = requestPath.replace(uriPrefix, '', 1)
        else:
            self.path = requestPath

    def readRequestSession(self):
        "Determines session from a cookie in request."
        if self.session != None:
            return
        cookieName = self.authSessionCookieName
        cookieString = self.request.COOKIES.get(cookieName, '')
        if cookieString:
            self.setSessionFromCookieString(cookieString)
        else:
            pass
        
    def getRequestParam(self, paramName, default=None):
        params = self.getRequestParams()
        param = params.get(paramName, default)
        return param

    def getRequestParams(self):
        if self.requestParams == None:
            if moddebug:
                msg = "%s: Reading request params from request." % (self.__class__.__name__)
                self.logger.debug(msg)
            if self.request.POST:
                self.requestParams = self.request.POST.copy()
            elif self.request.GET:
                self.requestParams = self.request.GET.copy()
            else:
                self.requestParams = self.getZeroRequestParams()
            #if self.request.FILES:
            #    self.requestParams.update(self.request.FILES)
            if moddebug:
                msg = "%s: Request params: %s" % (self.__class__.__name__, self.requestParams)
                self.logger.debug(msg)
        return self.requestParams

    def getZeroRequestParams(self):
        return {}
        #return MultiValueDict()

    def getResponse(self):
        if self.checkAccessControl():
            self.takeAction()
        if not self.redirect:
            self.createContext()
        if not self.redirect:
            self.markNavigation()
        if not self.redirect:
            webkitName = self.dictionary[WEBKIT_NAME]
            if webkitName == 'django':
                self.setContext()
        self.createResponse()
        self.setSessionCookie()
        if moddebug:
            msg = "%s: Returning response: %s" % (self.__class__.__name__, repr(self.response))
            self.logger.info(msg)
        return self.response

    def logViewResponse(self, methodName, accessDecisionName):
        if self.session:
            userName = self.session.person.name
        else:
            userName = 'visitor'
        self.logger.info(
            "%s: Response summary: %s %s %s %s" % (
                self.__class__.__name__,
                accessDecisionName,
                userName,
                methodName,
                self.path,
            )
        )

    def takeAction(self):
        pass

    def createContext(self):
        webkitName = self.dictionary[WEBKIT_NAME]
        if webkitName == 'django':
            if RequestContext:
                self.context = RequestContext(self.request)
            else:
                self.context = Context()
    
    def markNavigation(self):
        self.markMajorNavigation()
        self.markMinorNavigation()

    def markMajorNavigation(self):
        self.setMajorNavigationItem()
        self.setMajorNavigationItems()
        self.markCurrentNavigationItem(
            self.majorNavigation, self.getMajorNavigationItem()
        )
    
    def getMajorNavigationItem(self):
        return self.majorNavigationItem

    def markMinorNavigation(self):
        self.setMinorNavigationItem()
        self.setMinorNavigationItems()
        self.markCurrentNavigationItem(
            self.minorNavigation, self.getMinorNavigationItem()
        )

    def getMinorNavigationItem(self):
        return self.minorNavigationItem

    def setMajorNavigationItems(self):
        pass
    
    def setMinorNavigationItems(self):
        pass
    
    def setMajorNavigationItem(self):
        pass
    
    def setMinorNavigationItem(self):
        pass
    
    def markCurrentNavigationItem(self, items, value):
        self.setCurrentItem(items, value, 'url')

    def setCurrentItem(self, items, value='', name=''):
        for item in items:
            if name and (item[name] == value):
                item['isCurrentItem'] = True
            else:
                item['isCurrentItem'] = False

    def createResponse(self):
        webkitName = self.dictionary[WEBKIT_NAME]
        if self.redirect:
            if webkitName == 'django':
                self.response = HttpResponseRedirect(self.redirect)
        else:
            self.createContent()
            if self.redirect:
                if webkitName == 'django':
                    self.response = HttpResponseRedirect(self.redirect)
            else:
                if webkitName == 'django':
                    self.response = HttpResponse(self.content)
                    self.response.status_code = self.responseStatusCode
                elif webkitName == 'pylons':
                    self.response = self.content
           
    def createContent(self):
        webkitName = self.dictionary[WEBKIT_NAME]
        if webkitName == 'django':
            self.content = self.renderContextWithTemplate()
    
    def renderContextWithTemplate(self):
        template = self.getTemplate()
        context = self.getContext()
        if moddebug:
            self.logger.debug("Rendering template '%s' for context: %s" % (
                self.templatePath, "context printing suspended" #context
            ))
        return template.render(context)

    def getTemplate(self):
        if self.template == None:
            self.loadTemplate()
        return self.template

    def loadTemplate(self):
        templatesDir = self.dictionary[DJANGO_TEMPLATES_DIR]
        if not os.path.exists(templatesDir):
            msg = "Templates dir doesn't exist on path: %s" % templatesDir
            raise Exception(msg)
        templatePath = self.getTemplatePath()
        templatePath += ".html"
        if moddebug:
            self.logger.debug("Loading template: %s" % templatePath)
        try:
            self.loadTemplateFromPath(templatePath)
        except Exception, inst:
            msg = "Failed to load template %s from %s: %s" % (
                templatePath, templatesDir, inst
            )
            self.logger.error(msg)
            raise Exception(msg)
 
    def getTemplatePath(self):
        if self.templatePath == None:
            self.templatePath = self.makeTemplatePath()
        if not self.templatePath:
            raise Exception("No templatePath set on %s" % self)
        return self.templatePath

    def makeTemplatePath(self):
        raise Exception("No templatePath for view: %s" % self)

    def loadTemplateFromPath(self, templatePath):
        self.template = template_loader.get_template(templatePath)

    def getViewPosition(self):
        return self.getTemplatePath()

    def getContext(self):
        if self.context == None:
            self.createContext()
            self.setContext()
        return self.context

    def setContext(self, **kwds):
        domainName = self.dictionary[DOMAIN_NAME]
        if self.dictionary[HTTP_PORT] != '80':
            systemServicePort = self.dictionary[HTTP_PORT]
            systemServiceSocket = domainName +":"+ systemServicePort
        else:
            systemServiceSocket = domainName
            
        mediaHost = self.dictionary[MEDIA_HOST]
        if not mediaHost:
            try:
                mediaHost = self.request.META['SERVER_NAME']
            except:
                mediaHost = domainName
        if self.dictionary[MEDIA_PORT] != '80':
            mediaPort = self.dictionary[MEDIA_PORT]
            systemMediaSocket = mediaHost +":"+ mediaPort
        else:
            systemMediaSocket = mediaHost
        localNow = dm.times.getLocalNow()
        self.context.update({
            'pageCreated'       : localNow.strftime('%c'),
            'localNow'          : localNow,
            'view'              : self,
            'uriPrefix'         : self.dictionary[URI_PREFIX],
            'mediaPrefix'       : self.dictionary[MEDIA_PREFIX],
            'isDebug'           : self.isDebug,
            'systemVersion'     : self.dictionary[SYSTEM_VERSION],
            'viewClassName'     : self.__class__.__name__,
            'path'              : self.path,
            'session'           : self.session,
            'redirect'          : self.redirectPath,
            'returnPath'        : self.returnPath,
            'systemServiceName' : self.dictionary[SYSTEM_SERVICE_NAME],
            'systemServiceSocket': systemServiceSocket,
            'systemMediaSocket' : systemMediaSocket,
        })
        self.setWiderContext(**kwds)
        self.setMinorNavigationContext()

    def setWiderContext(self, **kwds):
        self.setMajorNavigationContext()

    def setMajorNavigationContext(self):
        self.context.update({
            'majorNavigation': self.majorNavigation,
        })

    def setMinorNavigationContext(self):
        self.context.update({
            'minorNavigation': self.minorNavigation,
        })

    def setRedirect(self, redirectPath):
        if redirectPath:
            redirectPath = self.dictionary[URI_PREFIX] + redirectPath
            self.logger.info('%s: Redirecting to: %s' % (self.__class__.__name__, redirectPath))
            self.redirect = redirectPath
    
    def setRedirectLogin(self, returnPath=''):
        if not returnPath:
            if self.request:
                returnPath = self.path
        if returnPath:
            self.logger.debug('%s: Returning later to: %s' % (self.__class__.__name__, returnPath))
        self.setRedirect('/login/' + returnPath)
    
    def setRedirectAccessDenied(self):
        if self.session:
            deniedPath = self.path
            self.setRedirect('/accessDenied/' + deniedPath)
        else:
            self.setRedirectLogin()
    
    def setSessionCookie(self):
        "Sets (or deletes) a cookie identifying the session in the response."
        cookieName = self.authSessionCookieName
        cookieDomain = self.authCookieDomain
        cookiePath = self.dictionary[URI_PREFIX].strip() or '/'
        if hasattr(self, 'isSessionStopping'):
            if moddebug:
                msg = "%s: Deleting '%s' cookie." % (
                    self.__class__.__name__, cookieName
                )
                self.logger.info(msg)
            webkitName = self.dictionary[WEBKIT_NAME]
            self.response.delete_cookie(
                cookieName, domain=cookieDomain, path=cookiePath
            )
        elif self.session and hasattr(self, 'isSessionStarting'):
            cookieString = self.makeCookieStringFromSessionKey(self.session.key)
            if self.getRequestParam('rememberme'):
                maxAge = 315360000
            else:
                maxAge = None
            if moddebug:
                msg = "%s: Setting '%s' cookie: %s." % (
                    self.__class__.__name__, cookieName, self.session.key[0:32]
                )
                self.logger.info(msg)
            webkitName = self.dictionary[WEBKIT_NAME]
            self.response.set_cookie(
                cookieName, cookieString, domain=cookieDomain, 
                max_age=maxAge, expires=maxAge, path=cookiePath
            )

    def startSession(self, person):
        self.person = person
        self.session = person.sessions.create()
        self.isSessionStarting = True
        if moddebug:
            msg = "%s: Started session: %s" % (
                self.__class__.__name__, self.session.key
            )
            self.logger.info(msg)
        
    def stopSession(self):
        if self.session:
            oldKey = self.session.key
            if moddebug:
                self.logger.info("%s: Stopping session: %s" % (self.__class__.__name__, oldKey))
            self.isSessionStopping = True
            try:
                self.session.delete()
            except Exception, inst:
                self.logger.error("%s: Error deleting session %s: %s" % (self.__class__.__name__, oldKey, repr(inst)))
            self.session = None
        else:
            self.logger.warn("%s: Stopping session, but there was no session." % (self.__class__.__name__))

    def showInlineHelp(self):
        return False

    def hasListallPage(self):
        return False

    def showSystemStatusMsg(self):
        return not self.systemMode.isProduction()

    def getSystemStatusMsg(self):
        msg = "%s" % self.dictionary.get(SYSTEM_MODE)
        msg +=" %s " % self.dictionary[LOG_LEVEL]
        import dm
        import dm.db
        import dm.webkit
        msg +=" domainmodel==%s" % (dm.__version__)
        msg +=" %s==%s" % (dm.webkit.webkitName, dm.webkit.webkitVersionFull or dm.webkit.webkitVersion)
        msg +=" sqlobject==%s" % (dm.db.sqoVer)
        msg +=" (%ss)" % (dm.times.getLocalNow() - self.handlingStarted).seconds
        return msg

class AbstractClassView(SessionView):

    registerSizeThreshold = 50
    domainObjectKey = None

    def __init__(self, domainClassName=None, **kwds):
        super(AbstractClassView, self).__init__(**kwds)
        if domainClassName:
            self.domainClassName = domainClassName
        self.domainObject = None

    def getDomainObjectRegister(self):
        domainClass = self.getDomainClass(self.domainClassName)
        return domainClass.createRegister()

    def getManipulatedObjectRegister(self):
        return self.getDomainObjectRegister()

    def setContext(self):
        super(AbstractClassView, self).setContext()
        self.context.update({
            'domainClassName' : self.domainClassName,
        })

    def getDomainObject(self):
        if self.domainObject == None:
            if self.domainObjectKey:
                objectRegister = self.getDomainObjectRegister()
                if objectRegister.isStateful:
                    self.domainObject = objectRegister.getAll()[self.domainObjectKey]
                else:
                    self.domainObject = objectRegister[self.domainObjectKey]
            
        return self.domainObject
        
    def getManipulatedDomainObject(self):
        return self.getDomainObject()


class AbstractInstanceView(AbstractClassView):

    def __init__(self, domainObjectKey=None, **kwds):
        super(AbstractInstanceView, self).__init__(**kwds)
        if domainObjectKey:
            self.domainObjectKey = domainObjectKey
        self.manipulator = None

    def setContext(self):
        super(AbstractInstanceView, self).setContext()
        domainObject = self.getDomainObject()
        self.context.update({
            'domainObjectKey' : self.domainObjectKey,
            'domainObject'    : domainObject,
        })

    def getManipulator(self):
        if self.manipulator == None:
            self.manipulator = self.buildManipulator()
        return self.manipulator

    def buildManipulator(self):
        manipulatorClass = self.getManipulatorClass()
        objectRegister = self.getManipulatedObjectRegister()
        domainObject = self.getManipulatedDomainObject()
        fieldNames = self.getManipulatedFieldNames()
        if moddebug:
            msg = "%s: Building manipulator %s for position %s" % (
                self.__class__.__name__,
                manipulatorClass.__name__,
                self.getViewPosition()
            )
            self.logger.info(msg)
        return manipulatorClass(objectRegister, domainObject, fieldNames, self)

    def getManipulatedFieldNames(self):
        return []

    def manipulateDomainObject(self):
        pass


class AbstractFormView(AbstractInstanceView):

    def __init__(self, **kwds):
        super(AbstractFormView, self).__init__(**kwds)
        self.form = None
        self.formErrors = None
        
    def takeAction(self):
        if self.isSubmissionRequest():
            self.manipulateDomainObject()
            if not self.getFormErrors():
                self.setPostManipulateRedirect()
            else:
                self.logger.warning("%s: Form errors: %s" % (
                    self.__class__.__name__, self.formErrors
                ))
        elif self.getRequestParams():
            # Initialise the form fields with request params.
            self.getValidationErrors()
        else:
            self.requestParams = self.getInitialParams()
            self.formErrors = self.getZeroFormErrors() 
                
    def getInitialParams(self):
        return {}
        #return MultiValueDict()

    def isSubmissionRequest(self):
        requestParams = self.getRequestParams()
        countParams = len(requestParams)
        isInitialSubmission = requestParams.has_key('initialise')
        return countParams and not isInitialSubmission

    def getFormErrors(self):
        if self.formErrors == None:
            if self.getRequestParams():
                self.formErrors = self.getValidationErrors()
                if moddebug:
                    self.logger.debug("Form errors: %s" % self.formErrors)
            else:
                self.formErrors = self.getZeroFormErrors() 
        return self.formErrors

    def getZeroFormErrors(self):
        return {}

    def getValidationErrors(self):
        manipulator = self.getManipulator()
        requestParams = self.getRequestParams()
        validationErrors = manipulator.getValidationErrors(requestParams)
        if moddebug:
            self.logger.debug("Validation errors: %s" % validationErrors)
        return validationErrors
            
    def getForm(self):
        if self.form == None:
            self.form = self.buildForm()
        return self.form

    def buildForm(self):
        manipulator = self.getManipulator()
        requestParams = self.getRequestParams()
        if not self.skipFormErrorChecks():
            formErrors = self.getFormErrors()
        else:
            formErrors = self.getZeroFormErrors()
        return FormWrapper(manipulator, requestParams, formErrors)

    def skipFormErrorChecks(self):
        if not self.getRequestParams():
            return False
        elif self.isSubmissionRequest():
            return False
        else:
            return True

    def getManipulatorClass(self):    
        return DomainObjectManipulator

    def setContext(self):
        super(AbstractFormView, self).setContext()
        self.context.update({
            'form'   : self.getForm(),
        })

    def setPostManipulateRedirect(self):
        self.setRedirect(self.makePostManipulateLocation())
        
    def makePostManipulateLocation(self):
        msg = "Abstract method not implemented on class %s." % (
            self.__class__.__name__
        )
        raise Exception(msg)


class AbstractInputFormView(AbstractFormView):

    def manipulateDomainObject(self):
        super(AbstractInputFormView, self).manipulateDomainObject()
        if not self.getFormErrors():
            manipulator = self.getManipulator()
            manipulator.decodeHtml(self.getRequestParams())
        

class AbstractListView(AbstractClassView):

    def setContext(self):
        super(AbstractListView, self).setContext()
        domainClassRegister = self.registry.getDomainClassRegister()
        objectRegister = self.getManipulatedObjectRegister()
        objectCount = len(objectRegister)
        isCountSingle = objectCount == 1
        isCountZero = objectCount == 0
        isCountLow = objectCount < self.registerSizeThreshold
        self.context.update({
            'domainClassNameList' : domainClassRegister.keys(), # todo: remove
            'domainObjectList': objectRegister,
            'domainClassName': objectRegister.typeName,
            'objectRegister': objectRegister,
            'objectCount': objectCount,
            'isCountSingle': isCountSingle,
            'isCountZero': isCountZero,
            'isCountLow': isCountLow,
            'showRegisterAllLink': not isCountLow,
            'showRegisterTable': isCountLow,
            'showRegisterIndex': not isCountLow,
            'showRegisterSearch': False,
        })

    def present(self):
        register = self.getManipulatedObjectRegister()
        if dm.webkit.webkitName == 'django' and dm.webkit.webkitVersion == '1.0':
            list = [o for o in register]
        elif dm.webkit.webkitName == 'django' and dm.webkit.webkitVersion == '0.96':
            list = [o.present() for o in register]
        return list


class AbstractPendingView(AbstractListView):

    def getManipulatedObjectRegister(self):
        r = super(AbstractPendingView, self).getManipulatedObjectRegister()
        return r.getPending()
        

class AbstractSearchView(AbstractClassView):

    def __init__(self, startsWith='', **kwds):
        super(AbstractSearchView, self).__init__(**kwds)
        self.userQuery = ''
        self.startsWith = startsWith
        if not self.startsWith and self.request.POST:
            self.requestParams = self.request.POST.copy()
            if self.requestParams.has_key('startsWith'):
                self.startsWith = self.requestParams['startsWith']
            else:
                self.userQuery = self.requestParams['userQuery']

    def setContext(self):
        super(AbstractSearchView, self).setContext()
        self.context.update({
            'showRegisterSearch': True,
            'showRegisterIndex': True,
        })
        if self.startsWith or self.userQuery:
            searchResultList = self.searchManipulatedRegister()
            objectCount = len(searchResultList)
            self.context.update({
                'isResultsRequest': True,
                'domainObjectList': searchResultList,
                'objectCount': objectCount,
                'isCountZero': objectCount == 0,
                'isCountSingle': objectCount == 1,
                'userQuery': self.userQuery,
                'startsWith': self.startsWith,
                'showRegisterTable': bool(objectCount),
                # todo: Improve above HTML character substitution.
            })
        else:
            objectRegister = self.getManipulatedObjectRegister()
            objectCount = len(objectRegister)
            self.context.update({
                'objectCount': objectCount,
                'showRegisterTable': False,
            })

    def searchManipulatedRegister(self):
        if not self.domainClassName:
            raise Exception("No domainClassName on '%s' set." % self)
        commandName = self.domainClassName + 'List'
        commandKwds = {}
        commandKwds['userQuery'] = self.userQuery
        commandKwds['startsWith'] = self.startsWith.capitalize()
        if commandName in self.commands:
            commandClass = self.commands[commandName]
        else:
            commandClass = self.commands['DomainObjectList']
            commandKwds['typeName'] = self.domainClassName
        command = commandClass(**commandKwds)
        command.execute()
        return command.results
            

class AbstractFindView(AbstractClassView):

    def __init__(self, startsWith='', **kwds):
        super(AbstractFindView, self).__init__(**kwds)
        self.startsWith = startsWith
        if not self.startsWith and self.request.POST:
            self.requestParams = self.request.POST.copy()
            if self.requestParams.has_key('startsWith'):
                self.startsWith = self.requestParams['startsWith']

    def setContext(self):
        super(AbstractFindView, self).setContext()
        self.context.update({
            'showRegisterSearch': True,
            'showRegisterIndex': True,
        })
        if self.startsWith:
            resultList = self.findDomainObjects()
            objectCount = len(resultList)
            self.context.update({
                'isResultsRequest': True,
                'domainObjectList': resultList,
                'objectCount': objectCount,
                'isCountZero': objectCount == 0,
                'isCountSingle': objectCount == 1,
                'startsWith': self.startsWith,
                'showRegisterTable': bool(objectCount),
            })
        else:
            objectRegister = self.getManipulatedObjectRegister()
            objectCount = len(objectRegister)
            self.context.update({
                'objectCount': objectCount,
                'showRegisterTable': False,
            })
    
    def findDomainObjects(self):
        if not self.domainClassName:
            raise Exception("No domainClassName on '%s' set." % self)
        commandName = self.domainClassName + 'List'
        commandKwds = {}
        commandKwds['startsWith'] = self.startsWith.capitalize()
        if commandName in self.commands:
            commandClass = self.commands[commandName]
        else:
            commandClass = self.commands['DomainObjectList']
            commandKwds['typeName'] = self.domainClassName
        command = commandClass(**commandKwds)
        command.execute()
        return command.results
            

class AbstractCreateView(AbstractInputFormView):

    def getInitialParams(self):
        initialParams = MultiValueDict()
        objectRegister = self.getManipulatedObjectRegister()
        domainClass = self.getDomainClass(objectRegister.typeName)
        for metaAttr in domainClass.meta.attributes:
            if not (hasattr(metaAttr, 'default')):
                continue
            if metaAttr.isAssociateList:
                initialParams.setlist(metaAttr.name, metaAttr.default)
            else:
                if callable(metaAttr.default):
                    initialParams[metaAttr.name] = metaAttr.default()
                else:
                    initialParams[metaAttr.name] = metaAttr.default
        return initialParams

    def manipulateDomainObject(self):
        super(AbstractCreateView, self).manipulateDomainObject()
        if not self.getFormErrors():
            manipulator = self.getManipulator()
            requestParams = self.getCreateParams()
            manipulator.create(requestParams)
            if not manipulator.manipulationErrors:
                self.setCreatedObject(manipulator.domainObject)
            else:
                self.formErrors = manipulator.manipulationErrors 

    def getCreateParams(self):
        createParams = self.getRequestParams()
        return createParams

    def setCreatedObject(self, createdObject):
        self.domainObject = createdObject
    

class AbstractImageView(AbstractInstanceView):

    def getResponse(self):
        self.content = self.getImageContent()
        self.response = HttpResponse(self.content)
        self.response.headers['Content-Type'] = self.getImageContentType()
        return self.response

    def getImageContent(self):
        raise Exception("Method not implemented on %s" % self)
        
    def getImageContentType(self):
        raise Exception("Method not implemented on %s" % self)
        

class AbstractReadView(AbstractInstanceView):

    def setContext(self):
        super(AbstractReadView, self).setContext()
        (previousObject, nextObject) = self.getPreviousNextDomainObjects()
        self.context.update({
            'domainObjectPersonalLabel': self.getDomainObjectPersonalLabel(),
            'domainObjectNamedValues': self.getDomainObjectAsNamedValues(),
            'previousObject': previousObject,
            'nextObject': nextObject,
        })

    def getDomainObjectAsNamedValues(self):
        domainObject = self.getDomainObject()
        return domainObject.asNamedValues()
        
    def getDomainObjectPersonalLabel(self):
        domainObject = self.getDomainObject()
        if domainObject:
            return domainObject.getPersonalLabel()
        else:
            return ''

    def getNextDomainObject(self):
        domainObject = self.getManipulatedDomainObject()
        objectRegister = self.getManipulatedObjectRegister()
        objectList = objectRegister.getSortedList()
        nextObject = objectRegister.getNextObject(
            objectList, domainObject
        )
        return nextObject
    
    def getPreviousDomainObject(self):
        domainObject = self.getManipulatedDomainObject()
        objectRegister = self.getManipulatedObjectRegister()
        objectList = objectRegister.getSortedList()
        previousObject = objectRegister.getPreviousObject(
            objectList, domainObject
        )
        return previousObject

    def getPreviousNextDomainObjects(self):
        domainObject = self.getManipulatedDomainObject()
        objectRegister = self.getManipulatedObjectRegister()
        nextAscends = objectRegister.getDomainClass().nextAscends
        objectList = objectRegister.getSortedList()
        if nextAscends:
            nextObject = objectRegister.getNextObject(
                objectList, domainObject
            )
            previousObject = objectRegister.getPreviousObject(
                objectList, domainObject
            )
        else:
            nextObject = objectRegister.getPreviousObject(
                objectList, domainObject
            )
            previousObject = objectRegister.getNextObject(
                objectList, domainObject
            )
        return (previousObject, nextObject)


class AbstractUpdateView(AbstractInputFormView):

    def getInitialParams(self):
        manipulator = self.getManipulator()
        return manipulator.getUpdateParams()
        
    def manipulateDomainObject(self):
        super(AbstractUpdateView, self).manipulateDomainObject()
        formErrors = self.getFormErrors()
        if not formErrors:
            manipulator = self.getManipulator()
            requestParams = self.getUpdateParams()
            manipulator.update(requestParams)
            if manipulator.manipulationErrors:
                self.formErrors = manipulator.manipulationErrors 
        else:
            if self.debug:
                self.logger.debug('Manipulator update not possible with form errors: %s' % (formErrors))

    def getUpdateParams(self):
        return self.getRequestParams()


class AbstractApproveView(AbstractUpdateView):

    def __init__(self, **kwds):
        super(AbstractApproveView, self).__init__(**kwds)
        self.formErrors = {}

    def manipulateDomainObject(self):
        super(AbstractApproveView, self).manipulateDomainObject()
        domainObject = self.getManipulatedDomainObject()
        domainObject.approve()


class AbstractDeleteView(AbstractFormView):

    def __init__(self, **kwds):
        super(AbstractDeleteView, self).__init__(**kwds)
        self.formErrors = {}

    def getInitialParams(self):
        initialParams = MultiValueDict()
        domainObject = self.getManipulatedDomainObject()
        domainObjectValueDict = domainObject.asDictValues()
        initialParams.update(domainObjectValueDict)
        return initialParams

    def manipulateDomainObject(self):
        super(AbstractDeleteView, self).manipulateDomainObject()
        domainObject = self.getManipulatedDomainObject()
        domainObject.delete()


class AbstractHasManyView(AbstractInstanceView):

    def __init__(self, hasManyName=None, hasManyKey=None, **kwds):
        super(AbstractHasManyView, self).__init__(**kwds)
        self.hasManyName = hasManyName
        self.hasManyKey = hasManyKey
        self.hasManyMeta = None
        self.hasManyRegister = None
        self.hasManyValueLabels = None
        self.associationObject = None

    def __repr__(self):
        return "<%s domainClassName='%s' domainObjectKey='%s' hasManyName='%s' hasManyKey='%s' redirect='%s' redirectPath='%s'>" % (self.__class__.__name__, self.domainClassName, self.domainObjectKey, self.hasManyName, self.hasManyKey, self.redirect, self.redirectPath)

    def getManipulatedObjectRegister(self):
        return self.getHasManyRegister()

    def getManipulatedDomainObject(self):
        return self.getAssociationObject()

    def setContext(self):
        super(AbstractHasManyView, self).setContext()
        hasManyClassName = self.getHasManyMeta().typeName
        hasManyRegister = self.getHasManyRegister()
        hasManyValueLabels = self.getHasManyValueLabels()
        associationObject = self.getAssociationObject()
        if associationObject:
            associationObjectNamedValues = associationObject.asNamedValues(
                excludeName=self.getHasManyMeta().owner
            )
        else:
            associationObjectNamedValues = []
        self.context.update({
            'hasManyName'        : self.hasManyName,
            'hasManyClassName'   : hasManyClassName,
            'hasManyRegister'    : hasManyRegister,
            'hasManyKey'         : self.hasManyKey,
            'hasManyValueLabels' : hasManyValueLabels,
            'associationObject'  : associationObject,
            'associationObjectNamedValues' : associationObjectNamedValues,
        })

    def getHasManyMeta(self):
        if not self.hasManyMeta:
            domainObject = self.getDomainObject()
            if not domainObject:
                message = "No domain object when getting meta data: %s" % self
                raise Exception(message)
            if not self.hasManyName in domainObject.meta.attributeNames:
                message = "HasMany name '%s' not in attributes: %s" % (
                    self.hasManyName, domainObject.meta.attributeNames
                )
                raise Exception(message)
            hasManyMeta = domainObject.meta.attributeNames[self.hasManyName]
            self.hasManyMeta = hasManyMeta
        return self.hasManyMeta

    def getHasManyRegister(self):
        if not self.hasManyRegister:
            domainObject = self.getDomainObject()
            self.hasManyRegister = getattr(domainObject, self.hasManyName)
        return self.hasManyRegister

    def getHasManyValueLabels(self):
        if not self.hasManyValueLabels:
            domainObject = self.getDomainObject()
            hasManyMeta = self.getHasManyMeta()
            hasManyValueLabels = hasManyMeta.createValueLabelList(domainObject)
            self.hasManyValueLabels = hasManyValueLabels
        return self.hasManyValueLabels

    def getManipulatorClass(self):    
        return HasManyManipulator

    def getAssociationObject(self):
        if self.associationObject == None:
            if self.hasManyKey:
                domainObject = self.getDomainObject()
                hasManyMeta = self.getHasManyMeta()
                associationObject = hasManyMeta.getAssociationObject(
                    domainObject, self.hasManyKey
                )
                self.associationObject = associationObject
        return self.associationObject


class AbstractListHasManyView(AbstractHasManyView):
    pass

class AbstractCreateHasManyView(AbstractHasManyView, AbstractCreateView):

    def setCreatedObject(self, createdObject):
        self.associationObject = createdObject


class AbstractReadHasManyView(AbstractHasManyView):
    pass

class AbstractUpdateHasManyView(AbstractReadHasManyView, AbstractUpdateView):
    pass

class AbstractDeleteHasManyView(AbstractReadHasManyView, AbstractDeleteView):
    pass

