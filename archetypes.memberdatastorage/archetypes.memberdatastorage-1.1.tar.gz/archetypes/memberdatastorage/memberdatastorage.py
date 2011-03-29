import logging
logger = logging.getLogger('archetypes.memberdatastorage')
logger.setLevel(logging.DEBUG)

try:
    from Products.PlonePAS.utils import decleanId
except ImportError:     # prior to Plone 4
    def decleanId(id):
        return id
    
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Storage import StorageLayer
from Products.Archetypes.Storage.annotation import AnnotationStorage
from Products.Archetypes.interfaces.storage import IStorage
from Products.Archetypes.interfaces.layer import ILayer
from Products.Archetypes.Field import encode

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerStorage

class MemberdataStorage(AnnotationStorage, StorageLayer):
    """A facade storage which delegates to
    the site's Memberdata Tool for actually
    storing content item field values as
    memberdata values. 

    This heavily relies on name magic.
    It is assumed that the correponding member
    and content instances have corresponding ids
    where the correspondance is established through
    Products.PlonePAS.utils.[de]cleanId.
    Furthermore the field names have
    to match corresponding memberdata properties
    unless the memberproperty id is specified when
    instanciating the storage.

    For safety reasons values are always stored in
    AnnotationStorage (as well) and it automatically
    falls back to this if no associated member can be
    found.
    """

    security = ClassSecurityInfo()

    __implements__ = (IStorage, ILayer)

    
    def __init__(self, property_id='', migrate=False):
        self._member_property_id = property_id
        self._migrate = migrate
        AnnotationStorage.__init__(self, migrate)

    
    security.declarePrivate('getMembershipTool')
    def getMembershipTool(self, instance):
        return getToolByName(instance, 'portal_membership')

    security.declarePrivate('initializeInstance')
    def initializeInstance(self, instance, item=None, container=None):
        pass

    security.declarePrivate('initializeField')
    def initializeField(self, instance, field):
        name = self._member_property_id or field.getName()
        logger.debug("Initializing memberproperty field '%s' to look for %s" % \
            (field.getName(), name))
        membership_tool = self.getMembershipTool(instance)
        member = membership_tool.getMemberById(decleanId(instance.getId()))
        memberdata_tool = getToolByName(instance, 'portal_memberdata')
        if not memberdata_tool.hasProperty(name):
            logger.debug("Adding %s property to the memberdata tool" % name)
            memberdata_tool.manage_addProperty(name, field.default, field.type)
        if member is not None:
            value = member.getProperty(name)
            self.set(name, instance, value)

    security.declarePrivate('get')
    def get(self, name, instance, **kwargs):
        membership_tool = self.getMembershipTool(instance)
        member = membership_tool.getMemberById(decleanId(instance.getId()))
        if member is not None:
            id = self._member_property_id or name
            value = member.getProperty(id)
            return value
        else:
            return AnnotationStorage.get(self, name, instance, **kwargs)

    security.declarePrivate('set')
    def set(self, name, instance, value, **kwargs):
        membership_tool = self.getMembershipTool(instance)
        member = membership_tool.getMemberById(decleanId(instance.getId()))
        if type(value) == type(u''):
            value = encode(value, instance)
        if member is not None:
            id = self._member_property_id or name
            member.setMemberProperties({id:value})
        # yes, set it in two places so we can fall back to it
        AnnotationStorage.set(self, name, instance, value, **kwargs)


    security.declarePrivate('unset')
    def unset(self, name, instance, **kwargs):
        pass

    security.declarePrivate('cleanupField')
    def cleanupField(self, instance, field, **kwargs):
        pass

    security.declarePrivate('cleanupInstance')
    def cleanupInstance(self, instance, item=None, container=None):
        pass

registerStorage(MemberdataStorage)
