from persistent.dict import PersistentDict

from zope.interface import implements, Interface
from zope.component import adapts
from zope.annotation import IAnnotations

from Products.CMFCore.utils import getToolByName

from raptus.workflownotification.interfaces import INotificationTemplateProvider
from raptus.workflownotificationtemplates import STORAGE_KEY

class NotificationTemplateProvider(object):
    """Mapper class to support templates stored in annotations
    """
    implements(INotificationTemplateProvider)
    adapts(Interface)
    
    def __init__(self, context):
        self.context = context
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        storage = IAnnotations(self.portal)
        if not storage.has_key(STORAGE_KEY):
            storage[STORAGE_KEY] = PersistentDict()
        self.storage = storage[STORAGE_KEY]
        
    def template(self, workflow, action):
        return self.storage.get('%s.%s' % (workflow, action), self.storage.get(workflow, u""))