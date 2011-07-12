from dm.view.base import SessionView
from dm.view.base import DomainObjectManipulator
from dm.view.base import HasManyManipulator
from dm.dom.base import DomainObjectRegister
from dm.dom.base import DomainObject
from dm.dictionarywords import SYSTEM_VERSION
from dm.dictionarywords import URI_PREFIX
from dm.util.datastructure import MultiValueDict
from dm.on import json
import traceback

class ApiView(SessionView):

    apiKeyHeaderName = None

    def getAuthenticatedPerson(self):
        person = None
        if self.apiKeyHeaderName == None:
            raise Exception, "Api key header name not set on %s." % self.__class__
        headerName = self.apiKeyHeaderName
        headerName = 'HTTP_%s' % headerName.upper().replace('-', '_')
        if headerName in self.request.META:
            headerValue = self.request.META[headerName]
            apiKeys = self.registry.apiKeys.findDomainObjects(key=headerValue)
            if len(apiKeys) == 1:
                person = apiKeys[0].person
        return person

    def canAccess(self):
        return self.canReadSystem()

    def getResponse(self):
        responseLocationHeader = ''
        self.content = ''
        try:
            self.setPathFromRequest()
            path = self.path.replace('/api', '', 1)
            try:
                dereferencedObject = self.registry.path.open(path)
            # Todo: Define exception class for this case.
            except Exception, inst:
                self.responseStatusCode = 404
            else:
                methodName = self.getMethodName()
                isRegistry = False
                isRegister = False
                isEntity = False
                if dereferencedObject == self.registry:
                    self.setResponseData({'version': self.dictionary[SYSTEM_VERSION]})
                elif isinstance(dereferencedObject, DomainObjectRegister):
                    objectRegister = dereferencedObject
                    domainClass = objectRegister.getDomainClass()
                    if methodName in ['GET']:
                        # Register-Get.
                        if not self.authoriseActionObject('Read', domainClass):
                            self.responseStatusCode = 403
                        else:
                            self.setResponseData(objectRegister.keys())
                    elif methodName in ['POST']:
                        # Register-Post.
                        if not self.authoriseActionObject('Create', domainClass):
                            self.responseStatusCode = 403
                        else:
                            data = MultiValueDict()
                            data.update(self.getRequestData())
                            manipulator = DomainObjectManipulator(objectRegister)
                            validationErrors = {}
                            for k,v in manipulator.getValidationErrors(data).items():
                               validationErrors[k] = v.as_text().strip('* ')
                            if validationErrors:
                                self.setResponseData(validationErrors)
                                self.responseStatusCode = 400
                            else:
                                manipulator.create(data)
                                if manipulator.manipulationErrors:
                                    self.setResponseData(manipulator.manipulationErrors)
                                    self.responseStatusCode = 400
                                else:
                                    self.responseStatusCode = 201
                                    responseLocationHeader = self.dictionary[URI_PREFIX]
                                    responseLocationHeader += self.path + '/'
                                    responseLocationHeader += str(manipulator.domainObject.getRegisterKeyValue())
                elif isinstance(dereferencedObject, DomainObject):
                    domainObject = dereferencedObject
                    objectRegister = domainObject.createRegister()
                    if methodName in ['GET']:
                        # Entity-Get.
                        if not self.authoriseActionObject('Read', domainObject):
                            self.responseStatusCode = 403
                        else:
                            manipulator = DomainObjectManipulator(objectRegister, domainObject)
                            self.setResponseData(manipulator.getReadableDictValues())
                    elif methodName in ['PUT', 'POST']:
                        # Entity-Put.
                        if not self.authoriseActionObject('Update', domainObject):
                            self.responseStatusCode = 403
                        else:
                            data = self.getRequestData()
                            manipulator = DomainObjectManipulator(objectRegister, domainObject)
                            validationErrors = {}
                            for k,v in manipulator.getValidationErrors(data).items():
                               validationErrors[k] = v.as_text().strip('* ')
                            if validationErrors:
                                self.setResponseData(validationErrors)
                                self.responseStatusCode = 400
                            else:
                                manipulator.update(data)
                                if manipulator.manipulationErrors:
                                    self.setResponseData(manipulator.manipulationErrors)
                                    self.responseStatusCode = 400
                                else:
                                    self.responseStatusCode = 200
                else:
                    raise Exception, "Path '%s' resolves to neither the registry, a register or a domain object: %s" % registryObject
        except Exception, inst:
            self.responseStatusCode = 500
            self.content = ''
            msg = "API View Error: %s: %s" % (inst, traceback.format_exc())
            self.logger.error(msg)
        self.createResponse()
        self.response['Content-Type'] = 'application/json'
        if responseLocationHeader:
            self.response['Location'] = responseLocationHeader
        return self.response

    def getRequestData(self):
        message = self.request.POST.keys()[0]
        try:
            data = json.loads(message)
        except Exception, inst:
            raise Exception, "Couldn't load JSON from request '%s': %s" % (message, inst)
        return data

    def setResponseData(self, data):
        self.content = json.dumps(data)

