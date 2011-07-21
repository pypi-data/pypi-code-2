from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import SelectionWidget
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from collective.arboreal.public import MultiArborealField
from collective.arboreal.public import MultiTreeSelectionWidget


ATArborealSelectionCriterionSchema = ATBaseCriterionSchema + Schema((

    StringField('tree',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                vocabulary='getArborealTreeVocabulary',
                widget=SelectionWidget(
                    label="tree name",
                    label_msgid="label_list_criteria_arboreal_list",
                    description="Choose a tree and save",
                    description_msgid="help_list_criteria_arboreal_list",
                    i18n_domain="atcontenttypes"),
                ),
    MultiArborealField('value',
                       required=True,
                       tree='getCurrentTree',
                       write_permission=ChangeTopics,
                       accessor="Value",
                       mutator="setValue",
                       default=[],
                       widget=MultiTreeSelectionWidget(
                           format='select',
                           label="Value",
                           label_msgid="label_selection_criteria_value",
                           description="Existing values.",
                           description_msgid="help_selection_criteria_value",
                           i18n_domain="plone"),
                       ),
#    LinesField('value',
#                required=1,
#                mode="rw",
#                write_permission=ChangeTopics,
#                accessor="Value",
#                mutator="setValue",
#                default=[],
#                vocabulary="getCurrentValues",
#                widget=MultiSelectionWidget(
#                    label="Value",
#                    label_msgid="label_selection_criteria_value",
#                    description="Existing values.",
#                    description_msgid="help_selection_criteria_value",
#                    i18n_domain="plone"),
#                ),
    ))

class ATArborealSelectionCriterion(ATBaseCriterion):
    """A selection criterion"""

    implements(IATTopicSearchCriterion)

    security = ClassSecurityInfo()
    schema = ATArborealSelectionCriterionSchema
    meta_type = 'ATArborealSelectionCriterion'
    archetype_name = 'ArborealSelection Criterion'
    shortDesc      = 'Select values from list'
    typeDescription= ''

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple( result )

    def getArborealTrees(self):
        " Get all trees from the tool "
        portal_arboreal = getToolByName(self, 'portal_arboreal')
        return portal_arboreal.getTopLevelTreeNames()
        
    def getArborealTreeVocabulary(self):
        " Get vocab for all trees from the tool "
        return DisplayList([(tree, tree) for tree in self.getArborealTrees()])

    def getCurrentTree(self):
        " fetches the correct tree "
        return self.getTree()


registerCriterion(ATArborealSelectionCriterion, ('MultiPathIndex',))
