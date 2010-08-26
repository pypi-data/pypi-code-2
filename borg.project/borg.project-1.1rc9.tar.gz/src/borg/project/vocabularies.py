from zope.interface import implementer

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

from borg.project.config import PLACEFUL_WORKFLOW_POLICY
from borg.project import ProjectMessageFactory as _

@implementer(IVocabularyFactory)
def workflow_policies(context):
    context = getattr(context, 'context', context)
    placeful_workflow = getToolByName(context, 'portal_placeful_workflow', None)
    items = []
    if placeful_workflow is not None:
        if PLACEFUL_WORKFLOW_POLICY in placeful_workflow.objectIds():
            items.append((_(u"Default project workflow"), PLACEFUL_WORKFLOW_POLICY))
    items.sort()
    return SimpleVocabulary.fromItems(items)

@implementer(IVocabularyFactory)
def globally_allowed_types(context):
    context = getattr(context, 'context', context)
    portal_types = getToolByName(context, 'portal_types')
    items = []
    for fti in portal_types.listTypeInfo():
        if getattr(fti, 'globalAllow', lambda: False)() == True and fti.title:
            items.append((fti.title, fti.getId(),))
    return SimpleVocabulary.fromItems(items)
