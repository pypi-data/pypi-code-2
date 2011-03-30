from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from betahaus.memberprofile import MemberProfileMessageFactory as _


class IsUniqueEmailValidatorBase(object):

    def __init__( self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        field = kwargs.get('field', None)
        if field is None:
            raise KeyError("Can't validate email address if field doesn't exist as a kwarg.")
        current_email = field.get(instance)
        
        #Don't validate if we're setting the same email address as already exists.
        if value == current_email:
            return None
        
        #Add all users from Plone acl
        #Check if anyone else is using that email address.
        plone_acl = getToolByName(instance, 'acl_users')
        found_emails = set()
        [found_emails.add(x.get('email')) for x in plone_acl.searchUsers(email=value)]
        
        #Add the Zope root users too. We can't search for them, and we have to do a lookup
        #based on their userids. They won't be returned by searchUsers.
        pm = getToolByName(instance, 'portal_membership')
        zope = getToolByName(instance, 'portal_url').getPortalObject().aq_parent
        for userid in zope.acl_users.users.listUserIds():
            member = pm.getMemberById(userid)
            found_emails.add(member.getProperty('email'))
        
        if value in found_emails:
            return _(u"The email address you entered wasn't unique in this site.")
        
        #All is well
        return True

#This weirdness is due to that Plone 3 and Plone 4 register validators in different ways
#well, it will all be over soon. (Riiight...:)

try:
    import plone.app.upgrade #Only exists in Plone 4
    #Plone 4
    from Products.validation.interfaces.IValidator import IValidator

    class IsUniqueEmail(IsUniqueEmailValidatorBase):
        """ Plone 4 version of validator. """
        implements(IValidator)

except ImportError:
    #Plone 3
    from Products.validation.interfaces import ivalidator

    class IsUniqueEmail(IsUniqueEmailValidatorBase):
        """ Plone 3 version of validator. """
        __implements__ = (ivalidator,)

