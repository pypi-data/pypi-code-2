from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import getAllUtilitiesRegisteredFor

from raptus.workflownotificationtemplates.interfaces import IPossibleNotificationTemplates

def availableWorkflows(context):
    utilities = getAllUtilitiesRegisteredFor(IPossibleNotificationTemplates)
    terms = []
    
    for utility in utilities:
        terms.extend([SimpleTerm(value, value, title) for value, title in utility.names(context)])
    return SimpleVocabulary(terms)