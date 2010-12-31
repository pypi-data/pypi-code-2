from zope.interface import implements
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import registerType

from Products.ATContentTypes.criteria import _criterionRegistry

from Products.ATContentTypes.criteria import ALL_INDICES
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion

from zope.i18nmessageid import MessageFactory

from collective.membercriterion import PROJECTNAME

from collective.membercriterion.config import ZOPE2_VERSION

_ = MessageFactory('collective.membercriterion')

MemberDataCriterionSchema = ATBaseCriterionSchema + Schema((
    
    StringField('property',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default="",
                vocabulary_factory="collective.membercriterion.criteria",
                widget=SelectionWidget(
                    label=_(u'label_criteria_property', default=u'Property'),
                    description=_(u'help_criteria_property', default=u'Member property to match to content')
                    ),
                ),

    ))

class MemberDataCriterion(ATBaseCriterion):
    """Compares content to the value of a particular member property for 
    the current user
    """
    if ZOPE2_VERSION >= 2.12:
        implements(IATTopicSearchCriterion)
    else:
        __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )

    security       = ClassSecurityInfo()
    schema         = MemberDataCriterionSchema
    meta_type      = 'MemberDataCriterion'
    archetype_name = 'Member data criterion'
    shortDesc      = 'Member property'
    
    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        property_name = self.Value()
        
        if not property_name:
            return ()
            
        membership = getToolByName(self, 'portal_membership')
        
        if membership.isAnonymousUser():
            return ()
        
        member = membership.getAuthenticatedMember()
        user = member.getUser()
        
        value = None
        
        try:
            value = user.getProperty(property_name, None)
        except AttributeError:
            value = member.getProperty(property_name, None)
        
        if isinstance(value, (set, frozenset,)):
            value = tuple(value)
        
        return ((self.Field(), value,),)


def register(criterion, indices):
    if isinstance(indices, basestring):
        indices = (indices,)
    indices = tuple(indices)

    if indices == ():
        indices = ALL_INDICES

    registerType(criterion, PROJECTNAME)

    crit_id = criterion.meta_type
    _criterionRegistry[crit_id] = criterion
    _criterionRegistry.portaltypes[criterion.portal_type] = criterion

    _criterionRegistry.criterion2index[crit_id] = indices
    for index in indices:
        value = _criterionRegistry.index2criterion.get(index, ())
        _criterionRegistry.index2criterion[index] = value + (crit_id,)

register(MemberDataCriterion, ALL_INDICES)
