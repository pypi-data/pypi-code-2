import base64

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName


class SubjectsVocabulary(object):
    """Vocabulary factory for subjects.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        subjects = list(catalog.uniqueValuesFor('Subject'))
        subjects.sort()
        terms = [SimpleTerm(value=k, token=base64.b64encode(k), title=k)
                 for k in subjects]
        return SimpleVocabulary(terms)


SubjectsVocabularyFactory = SubjectsVocabulary()


class StatesVocabulary(object):
    """Vocabulary factory for states in the default workflow
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        wt = getToolByName(context, 'portal_workflow')
        id = wt.getDefaultChain()[0]
        defWf = wt.getWorkflowById(id)
        terms = [SimpleTerm(value=s.id,
            token=s.id,
            title=context.translate(s.title))
            for s in defWf.states.objectValues()]
        return SimpleVocabulary(terms)

StatesVocabularyFactory = StatesVocabulary()
