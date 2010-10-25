from zope.interface import implements
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from interfaces import INotificationRecipient, INotificationEnabled

class NotificationRecipient(object):
    implements(INotificationRecipient)
    
    def __init__(self, name, email):
        self.email = email
        self.name = safe_unicode(name)
        
    def __str__(self):
        return '<NotificationRecipient %s <%s>>' % (self.name, self.email)

def UserRecipientFactory(userid):
    context = getSite()
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getMemberById(userid)
    mdata = getToolByName(context, 'portal_memberdata')
    member = mdata.wrapUser(member)
    return NotificationRecipient(member.getProperty('fullname', member.getUserName()), member.getProperty('email', None))