from zope.i18nmessageid import MessageFactory
workflownotificationtemplatesMessageFactory = MessageFactory('raptus.workflownotificationtemplates')
try:
    from Products.PlacelessTranslationService.utility import PTSTranslationDomain
    workflownotificationtemplatesdomain = PTSTranslationDomain('raptus.workflownotificationtemplates')
except ImportError: # Plone 4
    pass

STORAGE_KEY = 'raptus.workflownotificationtemplates'