from zope.interface import Interface
from zope import schema

from borg.project import ProjectMessageFactory as _

from plone.app.vocabularies.users import UsersSource
from plone.app.vocabularies.groups import GroupsSource

class IProject(Interface):
    """A project workspace, where special local roles may apply
    """
                         
    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"Name of the project"),
                            required=True)
                            
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short summary of the project"),
                              required=True)
    
    managers = schema.List(title=_(u"Managers"),
                           description=_(u"The following users should be managers of this project"),
                           value_type=schema.Choice(title=_(u"User id"),
                                                   source=UsersSource,),
                           default=[],
                           required=False)
    
    members = schema.List(title=_(u"Members"),
                          description=_(u"The following users should be members of this project"),
                          value_type=schema.Choice(title=_(u"User id"),
                                                   source=UsersSource,),
                          default=[],
                          required=False)
                                                   
    groups = schema.List(title=_(u"Member groups"),
                         description=_(u"Members of the following groups should be members of this project"),
                         value_type=schema.Choice(title=_(u"Group id"),
                                                   source=GroupsSource,),
                         default=[],
                         required=False)

    workflow_policy = schema.Choice(title=_(u"Workflow policy"),
                                    description=_(u"Choose a workflow policy for this project"),
                                    vocabulary="borg.project.WorkflowPolicies")
                                    
    addable_types = schema.Set(title=_(u"Addable types"),
                               description=_(u"These types will be addable by project members"),
                               value_type=schema.Choice(title=_(u"Type id"),
                                                        vocabulary="borg.project.AddableTypes"))
