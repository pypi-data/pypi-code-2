from zope.i18nmessageid import MessageFactory
workflownotificationMessageFactory = MessageFactory('raptus.workflownotification')
try:
    from Products.PlacelessTranslationService.utility import PTSTranslationDomain
    workflownotificationdomain = PTSTranslationDomain('raptus.workflownotification')
except ImportError: # Plone 4
    pass