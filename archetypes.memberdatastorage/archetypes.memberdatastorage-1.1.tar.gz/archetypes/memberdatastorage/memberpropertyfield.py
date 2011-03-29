import logging
logger = logging.getLogger('archetypes.memberdatastorage')
logger.setLevel(logging.DEBUG)

try:
    from Products.PlonePAS.utils import decleanId
except ImportError:    # prior to Plone 4
    def decleanId(id):
        return id

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.Archetypes.Registry import registerField
from archetypes.memberdatastorage.memberdatastorage import MemberdataStorage


class MemberPropertyField(atapi.StringField):
    """Making string-valued member properties managed by the memberdata 
       tool available in content space.

       Uses the Memberdata storage layer.

       Overrides the getDefault method to look up existing
       member properties first.

       Per default the field is mapped to a member property
       with the same id as the field's name. To connect to
       a differently named member property, this needs to be 
       specified twice: (i) by setting the 'member_property_id'
       on the field and (ii) when setting the storage. 
    """

    _properties = atapi.StringField._properties.copy()
    _properties.update({
        'member_property_id' : None,
        'storage' : MemberdataStorage(),   # pass in the member property id
                                           # here if mapping to a property
                                           # named differently than the field
        })

    security  = ClassSecurityInfo()

    security.declarePublic('getDefault')
    def getDefault(self, instance):
        """Return the default value to be used for initializing this
        field. First hunts for a matching member property before
        doing the regular stuff."""
        property = self._huntProperty(instance)
        return property or atapi.StringField.getDefault(self, instance)

    def _huntProperty(self, instance):
        logger.debug("hunting for property %s" % self.member_property_id)
        property_id = self.member_property_id or self.getName()
        content_id = instance.getId()
        membership_tool = getToolByName(instance, 'portal_membership')
        member = membership_tool.getMemberById(decleanId(content_id))
        if member is None:
            return None
        return member.getProperty(property_id)


registerField(MemberPropertyField,
              title = 'Member property field',
              description = 'Used to manage a member property '
                            'from a content object.')
