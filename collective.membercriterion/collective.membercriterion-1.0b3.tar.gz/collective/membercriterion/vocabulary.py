from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.interfaces.propertysheets import IPropertySheet
from Products.CMFCore.utils import getToolByName

class PropertiesVocabulary(object):

    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        acl_users = getToolByName(context, 'acl_users')
        
        all_properties = set()
        
        # XXX: Assumes properties for current user equals properties for
        # other any user

        membership = getToolByName(context, 'portal_membership')
        member = membership.getAuthenticatedMember()
        user = member.getUser()
        
        properties_plugins = acl_users.plugins.listPlugins(IPropertiesPlugin)
        for plugin_id, plugin in properties_plugins:
            sheet = plugin.getPropertiesForUser(user)
            if IPropertySheet.providedBy(sheet):
                all_properties.update(sheet.propertyIds())
        
        return SimpleVocabulary.fromValues(sorted(all_properties))

PropertiesVocabularyFactory = PropertiesVocabulary()