"""Package of domain model object classes."""

from dm.ioc import RequiredFeature
from dm.ioc import *
from dm.dom.meta import *
from dm.exceptions import *
import dm.times
from dm.util.datastructure import MultiValueDict
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
import traceback

debug = RequiredFeature('Debug')
moddebug = False
 
class DomainBase(object):
    """
    'Layer Supertype (475)'  [Fowler, 2003]
    """

    log              = RequiredFeature('Logger')
    dictionary       = RequiredFeature('SystemDictionary')
    registry         = RequiredFeature('DomainRegistry')
    pluginController = RequiredFeature('PluginController')

    def resolvePathPart(self, pathPart):
        return getattr(self, pathPart)


class AbstractRegister(DomainBase): 
    """
    Supertype for domain model registers.
    Follows 'AbstractList' in 'Iterator (257)' [GoF].
    """ 

    database = RequiredFeature('DatabaseFacade')

    def __init__(self, owner=None, ownerName=None, owner2=None,
            ownerName2=None, filter={}, isCached=False, **kwds):
        self.owner = owner
        self.ownerName = ownerName
        self.owner2 = owner2
        self.ownerName2 = ownerName2
        self.filter = filter
        self.isCached = isCached
        if self.isCached:
            self.cache = dict()
        else:
            self.cache = None

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default
                
    def __getitem__(self, key):
        item = self.find(key)
        return item

    # NB: Use item's key to test containment of item in register.
    def __contains__(self, key):
        return self.has_key(key)

    def has_key(self, key):
        if self.isCached:
            if key in self.cache:
                return True
        try:
            item = self.find(key)
        except:
            return False
        else:
            return True
       
    def find(self, key):
        "Returns keyed object."
        if self.isCached:
            if key in self.cache:
                if moddebug:
                    msg = "Model: Cache hit for key: '%s'" % key
                    self.log.info(msg)
                return self.readCache(key)
            else:
                if moddebug:
                    msg = "Model: Cache miss for key: '%s'" % key
                    self.log.info(msg)
        if moddebug:
            msg = "Model: Retrieving from %s record for key: '%s'" % (self, key)
            self.log.info(msg)
        return self.retrieveItem(key)

    def retrieveItem(self, *args, **kwds):
        "Abstract method to retrieve register entity."
        return None

    def beginTransaction(self):
        "Begins a transaction."
        # Commit, commit, commit, rollback, begin, commit, commit.
        return self.database.beginTransaction()
        

class RegisterIterator(object):
    "Iterator for domain object registers."

    def __init__(self, **kwds):
        self.results  = iter(kwds['results'])
        self.register = kwds['register']

    def next(self):
        nextRecord = self.results.next()
        return nextRecord.getDomainObject()

    def __getitem__(self, key):
        itemRecord = self.results[key]
        return itemRecord.getDomainObject()

    def __iter__(self):
        return self


class DomainObjectRegister(AbstractRegister):
    "Supertype for concrete domain object registers."

    isStateful = False

    def __init__(self, typeName='', keyName='id', metaAttr=None, **kwds):
        super(DomainObjectRegister, self).__init__(**kwds)
        # Recorded domain class name.
        self.typeName = typeName  
        # Attribute used to key register.
        self.keyName = keyName
        # Meta object for supported model attribute.
        self.metaAttr = metaAttr
        # Attributes used in basic search.
        if 'searchAttributeNames' in kwds:
            self.searchAttributeNames = kwds['searchAttributeNames']
        else:
            self.searchAttributeNames = ''
        if 'startsWithAttributeName' in kwds:
            self.startsWithAttributeName = kwds['startsWithAttributeName']
        else:
            self.startsWithAttributeName = ''
        
    def __repr__(self):
        className = self.__class__.__name__
        typeName = self.typeName
        keyName = self.keyName
        return "<%s typeName='%s' keyName='%s'>" % (
            className, typeName, keyName
        )

    def resolvePathPart(self, pathPart):
        # Make register key from path part.
        keyMeta = self.getKeyMeta()
        if keyMeta == None:
            keyValue = pathPart
        elif keyMeta.isDomainObjectRef:
            keyValue = keyMeta.getObjectByKey(pathPart)
        else:
            keyValue = pathPart
        return self[keyValue]

    def retrieveItem(self, key):
        "Attempts to retrieve existing domain object from database."
        item = None
        try:
            item = self.findDomainObject(key)
            if item and self.isCached:
                self.cacheItem(item)
            if not item:
                message = "findDomainObject() returned: %s" % unicode(item)
                raise StandardError(message)
        except StandardError, inst:
            #trace = traceback.format_exc()
            #self.log.error("Model: Error calling findDomainObject() method: %s" % trace)
            msg = "No %s called '%s' found: %s" \
                % (self.typeName, key, inst)
            raise KforgeRegistryKeyError(msg)
        return item

    def create(self, *args, **kwds):
        "Returns new registered domain object."
        item = self.createDomainObject(*args, **kwds)
        if item:
            if self.isCached:
                self.cacheItem(item)
            item.raiseCreate()
        return item

    def __len__(self):
        "Supports: len(registry)"
        return self.count()

    def __iter__(self, **kwds):
        "Returns iterator for registered items (not keys!)."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        results = self.database.listRecords(self.typeName, **kwds)
        iterator = RegisterIterator(results=results, register=self)
        objectList = [i for i in iterator]
        self.sortDomainObjects(objectList)
        return iter(objectList)
 
    def __delitem__(self, key):
        "Supports: del registry[key]"
        self.pop(key)
 
    def pop(self, key):
        item = self[key]
        item.delete()
        return item
        
    def count(self, **kwds):
        "Returns count of matching records."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        return self.database.countRecords(self.typeName, **kwds)
    
    def keys(self, **kwds):
        "Returns list of keys for register."
        values = self.values(**kwds)
        keyName = self.getKeyName()
        return [self.getRegisterKey(v) for v in values]

    def values(self, **kwds):
        "Returns list of records of register."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        values = []
        results = self.database.listRecords(self.typeName, **kwds)
        return [r.getDomainObject() for r in results]

    def startsWith(self, value, attributeName=''):
        kwds = {}
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        if not attributeName:
            attributeName = self.getStartsWithAttributeName()
        results = self.database.startsWith(
            self.typeName, value, attributeName, **kwds
        )
        #return RegisterIterator(results=results, register=self)
        iterator = RegisterIterator(results=results, register=self)
        objectList = [i for i in iterator]
        self.sortDomainObjects(objectList)
        return objectList
    
    def search(self, userQuery, attributeNames=None, spaceSplit=True):
        kwds = {'spaceSplit':spaceSplit}
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        if not attributeNames:
            attributeNames = self.getSearchAttributeNames()
        results = self.database.search(
            self.typeName, userQuery, attributeNames, **kwds
        )
        iterator = RegisterIterator(results=results, register=self)
        objectList = [i for i in iterator]
        self.sortDomainObjects(objectList)
        return objectList
    
    def createDomainObject(self, *args, **kwds):
        try:
            temporalKwds = {}
            for metaAttr in self.getDomainClassMetaAttributes():
                if metaAttr.isTemporal and metaAttr.name in kwds:
                    temporalKwds[metaAttr.name] = kwds.pop(metaAttr.name)
            self.coerceArgs(args, kwds)
            self.initialiseKwds(kwds)
            self.initialiseWithDefaults(kwds)
            self.coerceKwds(kwds)
            self.switchToRecords(kwds)
            domainObject = self.database.createDomainObject(self.typeName, **kwds)
            for (attrName, attrValue) in temporalKwds.items():
                setattr(domainObject, attrName, attrValue)
                domainObject.isChanged = True
            self.initialiseObject(domainObject)
            if domainObject.isChanged:
                domainObject.save()
        except KforgeDbError, inst:
            raise KforgeDomError(inst)
        else:
            return domainObject

    def findDomainObject(self, key):
        "Finds existing object."
        kwds = dict()
        keyName = self.getKeyName()
        if keyName:
            kwds[keyName] = key
            self.coerceKwds(kwds)
            record = self.findRecord(**kwds)
            loadedList = set(kwds.values())
            return record.getDomainObject(loadedList=loadedList)
        else:
            raise Exception, "No keyName set on %s" % self

    def read(self, *args, **kwds):  # todo: rename to something better
        self.coerceArgs(args, kwds)
        record = self.findRecord(**kwds)
        return record.getDomainObject()
            
    def findSingleDomainObject(self, **kwds):
        return self.findFirstDomainObject(**kwds)

    def findFirstDomainObject(self, **kwds):
        domainObjects = self.findDomainObjects(**kwds)
        if len(domainObjects) >= 1:
            return domainObjects[0]
        else:
            return None
    
    def findLastDomainObject(self, **kwds):
        domainObjects = self.findDomainObjects(**kwds)
        if len(domainObjects) >= 1:
            return domainObjects[-1]
        else:
            return None
    
    def findDomainObjects(self, __loadedList__=None, **kwds):
        objectList = []
        if __loadedList__ == None:
            __loadedList__ = set()
        self.coerceKwds(kwds)
        for value in kwds.values():
            __loadedList__.add(value)
        for record in self.findRecords(**kwds):
            domainObject = record.getDomainObject(__loadedList__)
            objectList.append(domainObject)
        self.sortDomainObjects(objectList)
        return objectList
    
    def findRecord(self, **kwds):
        "Finds existing object record."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        return self.database.findRecord(self.typeName, **kwds)

    def findRecords(self, **kwds):
        "Finds existing object records."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        return self.database.findRecords(self.typeName, **kwds)

    def coerceArgs(self, args, kwds):
        "Sets registryKey from args if not registryKey in kwds."
        keyName = self.getKeyName()
        if not kwds.has_key(keyName):
            if len(args):
                kwds[keyName] = args[0]

    def getDomainClass(self):
        return self.registry.getDomainClass(self.typeName)

    def getDomainClassMeta(self):
        domainClass = self.getDomainClass()
        return domainClass.meta
    
    def getDomainClassMetaAttributes(self):
        domainClassMeta = self.getDomainClassMeta()
        return domainClassMeta.attributes
    
    def getDomainClassMetaAttributeNames(self):
        domainClassMeta = self.getDomainClassMeta()
        return domainClassMeta.attributeNames
    
    def initialiseKwds(self, kwds):
        pass
        
    def initialiseWithDefaults(self, kwds):
        for metaAttr in self.getDomainClassMetaAttributes():
            attrName = metaAttr.name
            if attrName in kwds:
                continue
            if metaAttr.isDomainObjectRef:
                if not (hasattr(metaAttr, 'default') and metaAttr.default):
                    continue
                attrClassName = metaAttr.typeName
                attrClass = self.registry.getDomainClass(attrClassName)
                attrDomainRegister = attrClass.createRegister()
                attrValue = attrDomainRegister[metaAttr.default]
                kwds[attrName] = attrValue

    def coerceKwds(self, kwds):
        if self.owner and self.ownerName:
            kwds[self.ownerName] = self.owner
        if self.owner2 and self.ownerName2:
            kwds[self.ownerName2] = self.owner2
        for (k, v) in self.filter.items():
            if k not in kwds:
                kwds[k] = v

    def switchToRecords(self, kwds):
        metaAttributeNames = self.getDomainClassMetaAttributeNames()
        for attrName in kwds.keys():
            if attrName in metaAttributeNames:
                metaAttr = metaAttributeNames[attrName]
                if metaAttr.isDomainObjectRef:
                    domainObject = kwds[attrName]
                    if domainObject:
                        if hasattr(domainObject, 'record'):
                            kwds[attrName] = domainObject.record
                        else:
                            msg = "No record for '%s' domainObjectRef: %s" % (
                                attrName, kwds
                            )
                            raise KforgeRegistryKeyError, msg
                
    def initialiseObject(self, object):
        object.initialise(self)

    def cacheItem(self, item):
        "Adds item to in-memory cache."
        key = self.getRegisterKey(item)
        self.cache[key] = item
        item.cacheRegister(self)
    
    def readCache(self, item):
        "Reads item from in-memory cache."
        return self.cache[item]
    
    def decacheItem(self, item):
        "Removes item from in-memory cache."
        item.decacheRegister(self)
        key = self.getRegisterKey(item)
        self.decacheKey(key)
    
    def decacheKey(self, key):
        "Removes key from in-memory cache."
        try:
            del self.cache[key]
        except:
            pass
    
    def getRegisterKey(self, domainObject):
        "Returns key for domain object in register."
        attrName = self.getKeyName()
        return getattr(domainObject, attrName)
   
    def getKeyName(self):
        "Returns name of domain object attribute used for register key."
        if hasattr(self, 'keyName') and self.keyName:
            keyName = self.keyName
        else:
            keyName = 'id'
        return keyName

    def getKeyMeta(self):
        "Returns meta attr for register key."
        keyName = self.getKeyName()
        metaAttrs = self.getDomainClassMetaAttributeNames()
        if keyName in metaAttrs:
            return metaAttrs[keyName]
        else:
            return None

    def getStartsWithAttributeName(self):
        "Returns name of domain object attribute used in alphabetical index."
        attrName = self.startsWithAttributeName or self.getKeyName()
        if attrName == 'id':
            msg = "Can't match start of 'id' attribute. Try setting the " 
            msg += "'startsWithAttributeName' on class %s." % (
                self.getDomainClassMeta().name
            )
            raise Exception(msg)
        return attrName

    def getSearchAttributeNames(self):
        "Returns name of attributes used for searching domain objects'."
        return self.searchAttributeNames or [self.getStartsWithAttributeName()]

    def getObjectList(self):
        objectList = [domainObject for domainObject in self]
        return objectList
    
    def getSortedList(self):
        objectList = self.getObjectList()
        #self.sortDomainObjects(objectList)
        return objectList

    def getReverseSortedList(self):
        objectList = self.getSortedList()
        objectList.reverse()
        return objectList

    def sortDomainObjects(self, domainObjects):
        if debug:
            count = len(domainObjects)
            if count:
                className = domainObjects[0].__class__.__name__
                msg = "Model: Sorting %s %s domain objects." % (count, className)
                self.log.debug(msg)
        domainObjects.sort(self.cmpDomainObjects)

    def cmpDomainObjects(self, x, y):
        xValue = x.getSortOnValue()
        yValue = y.getSortOnValue()
        sortAscending = x.sortAscending
        if xValue < yValue:
            if sortAscending:
                return -1
            else:
                return 1
        if xValue == yValue:
            return 0
        if xValue > yValue:
            if sortAscending:
                return 1
            else:
                return -1

    def getNextObject(self, objectList, domainObject):
        if domainObject not in objectList:
            return None
            #msg = "Object not in list: %s %s" % (domainObject, objectList)
            #raise Exception(msg)
        index = objectList.index(domainObject)
        index += 1
        if (index < len(objectList)):
            return objectList[index]
        else:
            return None

    def getPreviousObject(self, objectList, domainObject):
        if domainObject not in objectList:
            return None
            #msg = "Object not in list: %s %s" % (domainObject, objectList)
            #raise Exception(msg)
        index = objectList.index(domainObject)
        index -= 1
        if (index >= 0):
            return objectList[index]
        else:
            return None

    def getOptionsRegister(self):
        keyName = self.getKeyName()
        classMeta = self.getDomainClassMeta()
        if keyName != 'id':
            keyAttrMeta = classMeta.attributeNames[keyName]
            if keyAttrMeta.isDomainObjectRef:
                return keyAttrMeta.getAssociatedObjectRegister(None)
        return self.clone()

    def clone(self):
        c = self.getDomainClass().createRegister()
        return c


class Register(DomainObjectRegister):
    pass


class DomainObject(DomainBase):
    """
    Domain object supertype. Follows 'Domain Model (116)'. 
    """

    registerKeyName = 'id'
    registerClass = Register
    principalRegister = None
    meta = None
    metaClass = MetaDomainObject
    paths = RequiredFeature('FileSystem') 
    isConstant = False
    isUnique = True
    isTemporal = False
    searchAttributeNames = []
    startsWithAttributeName = ''
    isRegistered = False
    dbName = ''
    registryAttrName = None
    sortOnName = None 
    sortAscending = True
    nextAscends = True

    def __init__(self, **kwds):
        "Initialise base attributes."
        #self.objectAttrValues = {}    # experimental
        self.assertIsClassRegistered()
        self.isChanged = False
        self.registerCache = {}
        self.record = None
        self.id = None
        if self.meta:
            for metaAttr in self.meta.attributes:
                metaAttr.setInitialValue(self)
                
    ## experimental
    #def __setattr__(self, attrName, attrVal):
    #    if self.meta and self.meta.attributeNames.has_key(attrName) and hasattr(self, 'objectAttrValues'):
    #        self.objectAttrValues[attrName] = attrVal
    #    else:
    #        super(DomainObject, self).__setattr__(attrName, attrVal)
    #    #super(DomainObject, self).__setattr__(attrName, attrVal)
   
    ## experimental
    #def __getattr__(self, attrName):
    #    raise AttributeError(attrName)
    #    if self.meta and self.meta.attributeNames.has_key(attrName) and hasattr(self, 'objectAttrValues'):
    #        return self.objectAttrValues.get(attrName, None)
    #    else:
    #        raise AttributeError(attrName)

    def __repr__(self):
        className = self.__class__.__name__
        reprAttrs = self.reprAttrs()
        return "<%s%s>" % (className, reprAttrs)

    def reprAttrs(self):
        reprAttrs = " id='%d'" % self.id
        if self.meta:
            for attr in self.meta.attributes:
                if attr.isValueRef and not attr.isBLOB:
                    reprAttrs += ' ' + attr.createObjectRepr(self)
                elif attr.isDomainObjectRef:
                    reprAttrs += ' ' + attr.createObjectRepr(self)
        return reprAttrs

    def getSortOnValue(self):
        if self.sortOnName:
            sortOnValue = getattr(self, self.sortOnName)
        else:
            sortOnValue = self.getPersonalLabel()
        if type(sortOnValue) in [str, unicode]:
            sortOnValue = sortOnValue.lower()
        return sortOnValue

    def asNamedValues(self, excludeName=''):  # todo: excludeNames
        namedValues = [] 
        if self.meta:
            for attr in self.meta.attributes:
                if not excludeName == attr.name:
                    namedValue = {}
                    namedValue['name'] = attr.name
                    namedValue['title'] = attr.calcTitle()
                    namedValue['value'] = attr.createValueRepr(self)
                    namedValue['label'] = attr.createLabelRepr(self)
                    namedValue['domainKeyValue'] = self.getRegisterKeyValue()
                    namedValue['isDomainObjectRef'] = attr.isDomainObjectRef
                    if attr.isDomainObjectRef:
                        namedValue['isSimpleOption'] = attr.isSimpleOption
                    else:
                        namedValue['isSimpleOption'] = False
                    namedValue['registryAttrName'] = attr.getRegistryAttrName(self)
                    namedValue['typeName'] = attr.typeName
                    namedValue['isAssociateList'] = attr.isAssociateList
                    if attr.isAssociateList:
                        namedValue['associatedNamedValues'] = attr.createAssociatedNamedValues(self)
                    namedValues.append(namedValue)
        return namedValues

    def asSortableValues(self):
        values = {} 
        if self.meta:
            for attr in self.meta.attributes:
                values[attr.name] = attr.createSortableRepr(self)
        return values

    def asDictValues(self):
        dictValues = {} 
        if self.meta:
            for attr in self.meta.attributes:
                dictValues[attr.name] = attr.createValueRepr(self)
        return dictValues

    def asDictLabels(self):
        labels = {} 
        if self.meta:
            for attr in self.meta.attributes:
                labels[attr.name] = attr.createLabelRepr(self)
        return labels

    def present(self):
        return self.asDictLabels()

    def asRequestParams(self, attrNames=None):
        requestParams = MultiValueDict()
        for attr in self.meta.attributes:
            attrName = attr.name
            if (attrNames != None) and (attrName not in attrNames):
                continue
            attrValueRepr = attr.createValueRepr(self)
            if attr.isList():
                requestParams.setlist(attrName, attrValueRepr)
            else:
                if attrValueRepr != None:
                    requestParams[attrName] = attrValueRepr
                else:
                    requestParams[attrName] = ''
        return requestParams

    def assertIsClassRegistered(self):
        className = self.__class__.__name__
        if not self.isClassRegistered(self.__class__):
            message = "Class '%s' is not registered." % className
            raise DomainClassRegistrationError(message)
        if not self.meta:
            message = "Class '%s' has no meta object." % className
            raise DomainClassRegistrationError(message)
        if len(self.meta.attributesDeferred):
            message = "Class '%s' has mismatched (deferred) attributes: %s" % (
                className, unicode(self.meta.attributesDeferred))
            raise DomainClassRegistrationError(message)

    def isClassRegistered(self, domainClass):
        return domainClass.isRegistered

    def initialise(self, register=None):
        pass 
    
    def isActionActionable(self, actionName):
        return True

    def save(self):
        "Update record of object in the database."
        self.saveSilently()
        self.raiseUpdate()

    def saveSilently(self):
        "Update record without raising update event."
        if not self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            self.updateLastModifiedTime()
        self.record.saveDomainObject()

    def updateLastModifiedTime(self):
        if 'lastModified' in self.meta.attributeNames:
            self.lastModified = dm.times.getUniversalNow()
        
    def delete(self):
        self.deleteAggregates()
        # Todo: Set 'HasA' on normal collection to 'None'?
        self.raiseDelete()
        self.destroySelf()

    def deleteAggregates(self):
        for metaAttr in self.meta.attributes:
            if metaAttr.isAggregation():
                if metaAttr.isList():
                    self.deleteAggregateList(metaAttr.name)

    def deleteAggregateList(self, attrName):
        aggregateRegister = getattr(self, attrName)
        for aggregateObject in aggregateRegister:
            aggregateObject.delete()

    def destroySelf(self):
        "Destroy record of object in the database."
        self.decacheItem()
        if self.record:
            self.deleteTemporalObjects()
            self.record.domainObject = None
            self.record.destroySelf()
            self.record = None

    def deleteTemporalObjects(self):
        if self.meta.isTemporal:
            register = self.meta.createTemporalCollection(self)
            [i.delete() for i in register]
        else:
            for metaAttr in self.meta.attributes:
                if metaAttr.isTemporal:
                    register = metaAttr.createTemporalCollection(self)
                    [i.delete() for i in register]

    def purgeAggregates(self):
        for metaAttr in self.meta.attributes:
            if metaAttr.isAggregation():
                if metaAttr.isList():
                    self.purgeAggregateList(metaAttr.name)

    def purgeAggregateList(self, attrName):
        aggregateRegister = getattr(self, attrName)
        if aggregateRegister.isStateful:
            aggregateRegister = aggregateRegister.getDeleted()
        for aggregateObject in aggregateRegister:
            aggregateObject.purge()

    def decacheItem(self):
        for register in self.registerCache.keys():
            register.decacheItem(self)

    def notifyPlugins(self, *args):
        if self.pluginController:
            self.pluginController.notify(*args)

    def raiseCreate(self):
        "Raises onCreate event."
        message = "Model: Created %s '%s': %s" % (
            self.__class__.__name__,
            self.getRegisterKeyValue(),
            repr(self)
        )
        self.log.info(message)
        try:
            self.onCreate()
        except Exception, inst:
            trace = traceback.format_exc()
            self.log.error("Model: Error raising create event: %s" % trace)
            try:
                self.uncreate()
            except Exception, inst:
                trace = traceback.format_exc()
                self.log.error("Model: Couldn't undo create: %s" % trace)
            raise

    def uncreate(self):
        self.delete()
        # Todo: Move this down to Stateful class.
        if hasattr(self, 'purge'):
            self.purge()

    def raiseUpdate(self):
        "Raises onUpdate event."
        if debug:
            message = "Model: Updated %s: '%s'" % (
                self.__class__.__name__,
                self
            )
            self.log.debug(message)
        try:
            self.onUpdate()
        except Exception, inst:
            trace = traceback.format_exc()
            self.log.error("Model: Error raising update event: %s" % trace)
            raise

    def raiseDelete(self):
        "Raises onDelete event."
        message = "Model: Deleted %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)
        try:
            self.onDelete()
        except Exception, inst:
            trace = traceback.format_exc()
            self.log.error("Model: Error raising delete event: %s" % trace)
        # Don't re-raise event, because it trips up undoing create.

    def raiseApprove(self):
        "Raises onApprove event."
        message = "Model: Approved %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)
        try:
            self.onApprove()
        except Exception, inst:
            trace = traceback.format_exc()
            self.log.error("Model: Error raising approve event: %s" % trace)
            raise

    def raiseUndelete(self):
        "Raises onUndelete event."
        message = "Model: Undeleted %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)
        try:
            self.onUndelete()
        except Exception, inst:
            trace = traceback.format_exc()
            self.log.error("Model: Error raising undelete event: %s" % trace)
            raise

    def raisePurge(self):
        "Raises onPurge event."
        message = "Model: Purged %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)
        try:
            self.onPurge()
        except Exception, inst:
            trace = traceback.format_exc()
            self.log.error("Model: Error raising purge event: %s" % trace)
        # Don't re-raise event, because it trips up undoing create.


    def onCreate(self):
        "Abstract handler for Create object event."
        self.notifyPlugins(self.__class__.__name__ + 'Create', self)

    def onUpdate(self):
        "Abstract handler for Update event."
        self.notifyPlugins(self.__class__.__name__ + 'Update', self)

    def onDelete(self):
        "Abstract handler for Delete object event."
        self.notifyPlugins(self.__class__.__name__ + 'Delete', self)
    
    def onApprove(self):
        "Abstract handler for Approve object event."
        self.notifyPlugins(self.__class__.__name__ + 'Approve', self)
    
    def onUndelete(self):
        "Abstract handler for Undelete object event."
        self.notifyPlugins(self.__class__.__name__ + 'Undelete', self)
    
    def onPurge(self):
        "Abstract handler for Purge object event."
        self.notifyPlugins(self.__class__.__name__ + 'Purge', self)

    def cacheRegister(self, register):
        "Remember a register."
        self.registerCache[register] = register

    def decacheRegister(self, register):
        "Forget a register."
        if register in self.registerCache:
            del(self.registerCache[register])

    def createRegister(self, **kwds):
        if not ('typeName' in kwds and kwds['typeName']):
            kwds['typeName'] = self.__name__
        if not ('keyName' in kwds and kwds['keyName']):
            kwds['keyName']  = self.registerKeyName
        if not ('isCached' in kwds and kwds['isCached']):
            kwds['isCached'] = self.isConstant
        if not('searchAttributeNames' in kwds and kwds['searchAttributeNames']):
            kwds['searchAttributeNames'] = self.searchAttributeNames
        if not('startsWithAttributeName' in kwds and kwds['startsWithAttributeName']):
            kwds['startsWithAttributeName'] = self.startsWithAttributeName
        if moddebug and debug:
            className = self.registerClass.__name__
            message = "Model: Creating '%s' register with kwds: %s" % (className, kwds)
            self.log.debug(message)
        register = self.registerClass(**kwds)
        return register
        
    createRegister = classmethod(createRegister)
    
    def getRegisterKeyValue(self):
        "Returns register key for domain object."
        return getattr(self, self.registerKeyName)
  
    def getRegistryAttrName(self):
        if not self.registryAttrName:
            self.registryAttrName = self.createCollectiveNoun()
        return self.registryAttrName

    getRegistryAttrName = classmethod(getRegistryAttrName)
    
    def getRegistryId(self):
        return "%s.%s" % (
            self.getRegistryAttrName(),
            self.getRegisterKeyValue(),
        )
    
    def getLabelRepr(self):
        return self.getLabelValue().encode('utf-8')

    def getLabelValue(self):
        return unicode(self.getRegisterKeyValue())

    def getPersonalLabel(self):
        # default to basic label
        return self.getLabelValue()

    def createCollectiveNoun(self):
        noun = self.createNoun()
        # caution: naive pluralisation ahead!
        if noun[-1] == 'y':
            noun = noun[:-1] + 'ies'
        elif noun[-1] == 's':
            noun = noun[:-1] + 'ses'
        else:
            noun = noun + 's'
        return noun

    createCollectiveNoun = classmethod(createCollectiveNoun)
    
    def createNoun(self):
        name = self.__name__
        return name[0].lower() + name[1:]
        
    createNoun = classmethod(createNoun)

    def getOptionsRegister(self, attrName):
        attrValue = getattr(self, attrName)
        metaAttr = self.meta.attributeNames[attrName]
        register = metaAttr.getAssociatedObjectRegister(attrValue)
        return register


class SimpleObject(DomainObject):
    pass
    
    
class SimpleNamedObject(DomainObject):

    registerKeyName = 'name'
    name = String(isIndexed=True, isRequired=True)

