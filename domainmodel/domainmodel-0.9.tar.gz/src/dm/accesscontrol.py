from dm.ioc import RequiredFeature
from dm.strategy import MakeProtectedNames, FindProtectionObjects
from dm.dictionarywords import MEMOS_LIMIT, MEMOS_EXPIRE, MEMOS_ENABLED
from dm.dictionarywords import VISITOR_NAME
from dm.exceptions import *
import mx.DateTime
import traceback
moddebug = False

class BaseAccessController(object):
    """Template class for controlling access to protected objects.

    Client objects will call the isAccessAuthorised() method with keywords:
    
        canUpdateAccount = accessController.isAccessAuthorised(
            person=john,
            actionName='Update',
            protectedObject=account
        )
    
    This method effectively implements "bool(not bars and grants)" for the
    union of all pertaining bars and the union of all pertaining grants.

    It's critical to check all the ways access could be barred, before
    checking all the ways access could be authorised. It doesn't matter which
    bar triggers a denial or which grant causes an authorisation, but it does
    matter that bars trigger denials before grants trigger authorisations.

    Access is denied by raising the AccessIsForbidden exception in any of the
    methods called by isAccessAuthorised(). They are setPerson(), setAction(),
    setProtectedObject(), assertAccessNotBarred(), and 
    assertAccessNotAuthorised(). Likewise, access is authorised by raising the
    AccessIsAuthorised exception within those methods. By default, access is
    not authorised.

    Any access controller derived from this class can involve other domain
    objects having grants or bars in their access control scheme by extending
    the assertAccessNotBarred() or assertAccessNotAuthorised() methods, and 
    checking the involved object by calling the assertRoleNotBarred(object) or
    assertRoleNotAuthorised(object) methods.
    """
    
    dictionary = RequiredFeature('SystemDictionary')
    registry = RequiredFeature('DomainRegistry')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def __init__(self):
        self.action = None
        self.person = None
        self.protectedObject = None
        self.protectionObjects = None
        self.permissions = None
        self.visitor = None
        self.memosEnabled = bool(self.dictionary[self.dictionary.words.MEMOS_ENABLED])
        self.memosExpire = int(self.dictionary[self.dictionary.words.MEMOS_EXPIRE])
        self.memosLimit = int(self.dictionary[self.dictionary.words.MEMOS_LIMIT])
        self.memosCache = {}
        self.memosFifo = []
        self.memosAge = {}

    def isAuthorised(self, person=None, actionName=None, protectedObject=None, *args, **kwds):
        if moddebug:
            msg = "AccessController: Deciding access for %s to %s %s." % (
                self.summarizePerson(person), actionName.lower(),
                self.summarizeProtectedObject(protectedObject)
            )
            self.logger.info(msg)
        return self.isAccessAuthorised(person=person, actionName=actionName, protectedObject=protectedObject, *args, **kwds)

    def isAccessAuthorised(self, person, actionName, protectedObject, *args, **kwds):
        isAuthorised = False
        notMemoized = False
        try:
            if self.hasMemos():
                self.assertNotMemoized(person, actionName, protectedObject)
                notMemoized = True
            self.setPerson(person)
            self.setAction(actionName)
            self.setProtectedObject(protectedObject)
            self.assertAccessNotBarred()
            self.assertAccessNotAuthorised() 
            raise AccessIsForbidden("default")
        except AccessIsAuthorised, inst:
            msg = "AccessController: Allowing %s to %s %s: by %s." % (
                self.summarizePerson(person), actionName.lower(),
                self.summarizeProtectedObject(protectedObject), inst
            )
            self.logger.info(msg)
            isAuthorised = True
        except AccessIsForbidden, inst:
            msg = "AccessController: Denying %s to %s %s: by %s." % (
                self.summarizePerson(person), actionName.lower(),
                self.summarizeProtectedObject(protectedObject), inst
            )
            self.logger.info(msg)
        except Exception, inst:
            msg = "AccessController: Error whilst checking access for"
            msg += " %s to %s %s: %s" % (
                self.summarizePerson(person), actionName,
                self.summarizeProtectedObject(protectedObject), inst,
            )
            msg += "\n" + traceback.format_exc()
            self.logger.error(msg)
        if notMemoized:
            self.storeMemo(person, actionName, protectedObject, isAuthorised)
        return isAuthorised

    def hasMemos(self):
        return (self.memosEnabled) and (self.memosLimit > 0) and (self.memosExpire > 0)
        
    def assertNotMemoized(self, person, actionName, protectedObject):
        memoName = self.makeMemoName(person, actionName, protectedObject)
        if moddebug:
            self.logger.info("AccessController: Checking %s memos for '%s' result." % (len(self.memosFifo), memoName))
        if memoName not in self.memosCache:
            return
        isAuthorised = self.memosCache.get(memoName, None)
        isExpired = False
        if memoName in self.memosAge:
            isExpired = int(mx.DateTime.now() - self.memosAge[memoName]) >= self.memosExpire
        if isExpired:
            if memoName in self.memosFifo:
                self.memosFifo.remove(memoName)
            wasAuthorised = self.memosCache.pop(memoName, None)
            wasStored = self.memosAge.pop(memoName, None)
            if moddebug:
                self.logger.info("AccessController: Expired memo '%s' was %s at %s" % (memoName, wasAuthorised, wasStored))
        else:
            if isAuthorised == True:
                raise AccessIsAuthorised('memo of previous check')
            elif isAuthorised == False:
                raise AccessIsForbidden('memo of previous check')

    def makeMemoName(self, person, actionName, protectedObject):
        personTag = person and person.id or 'None'
        actionTag = actionName
        protectionTag = MakeProtectedNames(protectedObject).make()[0]
        return "Person.%s-%s-%s" % (personTag, actionTag, protectionTag)

    def storeMemo(self, person, actionName, protectedObject, isAuthorised):
        memoName = self.makeMemoName(person, actionName, protectedObject)
        if moddebug:
            self.logger.info("AccessController: Storing memo '%s': %s" % (memoName, isAuthorised))
        if memoName in self.memosFifo:
            self.memosFifo.remove(memoName)
        if len(self.memosFifo) >= self.memosLimit:
            # Drop the last one.
            retiredName = self.memosFifo.pop()
            wasAuthorised = self.memosCache.pop(retiredName, None)
            wasStored = self.memosAge.pop(retiredName, None)
            self.logger.info("AccessController: Retired oldest memo '%s' was %s at %s" % (retiredName, wasAuthorised, wasStored))
        self.memosFifo.insert(0, memoName)
        self.memosCache[memoName] = isAuthorised
        self.memosAge[memoName] = mx.DateTime.now()

    def setPerson(self, person):
        self.permissions = None
        if person:
            self.person = person
        else:
            self.person = self.getVisitor()
        if not self.person:
            raise AccessIsForbidden("missing person")

    def setAction(self, actionName):
        self.permissions = None
        if not actionName:
            raise AccessIsForbidden("missing action")
        if actionName not in self.registry.actions:
            raise AccessIsForbidden("invalid action")
        self.action = self.registry.actions[actionName]

    def setProtectedObject(self, protectedObject):
        self.permissions = None
        self.protectionObjects = None
        if not protectedObject:
            raise AccessIsForbidden("missing protected object")
        self.protectedObject = protectedObject
        
    def assertAccessNotBarred(self):
        pass

    def assertAccessNotAuthorised(self):
        pass

    def assertRoleNotBarred(self, role, msg=''):
        if self.isPermissionSet(role.bars, 'barred', msg):
            raise AccessIsForbidden(msg)

    def assertRoleNotAuthorised(self, role, msg=''):
        if self.isPermissionSet(role.grants, 'authorised', msg):
            raise AccessIsAuthorised(msg)

    # Todo: Memoize this method's results.
    def isPermissionSet(self, permissions, polarity, msg):
        isSet = False
        for permission in self.getPermissions():
            if permission in permissions:
                isSet = True
        if isSet:
            if moddebug:
                msg = "access %s by %s" % (polarity, msg)
                self.logger.info("AccessController: %s" % msg)
            return True
        else:
            if moddebug:
                msg = "access not %s by %s" % (polarity, msg)
                self.logger.info("AccessController: %s" % msg)
            return False

    # Todo: Memoize this method's results.
    def getPermissions(self):
        if self.permissions == None:
            self.permissions = []
            for protectionObject in self.getProtectionObjects():
                try:
                    permission = protectionObject.permissions[self.action]
                    self.permissions.append(permission)
                except KforgeRegistryKeyError:
                    msg = "No permission '%s' on protection object '%s'." % (
                        self.action.name, protectionObject.name)
                    self.logger.warn("AccessController: %s" % msg)
        return self.permissions

    # Todo: Memoize this method's results.
    def getProtectionObjects(self):
        if self.protectionObjects == None:
            findCmd = FindProtectionObjects(self.protectedObject)
            self.protectionObjects = findCmd.find()
        return self.protectionObjects

    def alsoCheckVisitor(self):
        return self.getVisitor() and self.person != self.getVisitor()

    def getVisitor(self):
        if self.visitor == None:
            visitorName = self.dictionary[VISITOR_NAME]
            try:
                self.visitor = self.registry.persons[visitorName]
            except KforgeRegistryKeyError:
                pass
        return self.visitor

    def summarizePerson(self, person):
        return person and person.name or 'None'

    def summarizeProtectedObject(self, protectedObject):
        if type(protectedObject) == type:
            return "%s objects" % protectedObject.__name__
        elif hasattr(protectedObject, 'getRegisterKeyValue'):
            return "%s %s" % (
                type(protectedObject).__name__,
                protectedObject.getRegisterKeyValue(),
            )
        else:
            return repr(protectedObject)
    

class SystemAccessController(BaseAccessController):
    "Introduces personal and system roles to base access controller."

    def assertAccessNotBarred(self):
        self.assertPersonNotBarred()
        super(SystemAccessController, self).assertAccessNotBarred()

    def assertPersonNotBarred(self):
        self.assertRoleNotBarred(self.person, 'personal role')

    def assertAccessNotAuthorised(self):
        self.assertSystemRoleNotAuthorised()
        self.assertPersonNotAuthorised()
        super(SystemAccessController, self).assertAccessNotAuthorised()
        
    def assertSystemRoleNotAuthorised(self):
        self.assertPersonSystemRoleNotAuthorised()
        if self.alsoCheckVisitor():
            self.assertVisitorSystemRoleNotAuthorised()

    def assertPersonSystemRoleNotAuthorised(self):
        role = self.person.role
        self.assertRoleNotAuthorised(role, "system %s role" % role.name.lower())

    def assertVisitorSystemRoleNotAuthorised(self):
        role = self.getVisitor().role
        self.assertRoleNotAuthorised(role, "visitor's system %s role" % role.name.lower())

    def assertPersonNotAuthorised(self):
        self.assertRoleNotAuthorised(self.person, 'personal role')

