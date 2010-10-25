from zope.interface import Interface, Attribute

class INotificationUtils(Interface):
    """ View providing utility methods concerning workflownotifications
    """
    
    def getEnabledTransitionsFor(objs):
        """ returns all transitions which have notifications enabled for the given objects
        """
    
    def getWorkflowFor(obj):
        """ returns the workflow_id for the given object
        """
    
    def getRecipientsFor(obj, action):
        """ returns a list of default recipients for the given object and action
        """
    
    def getTemplateFor(obj, action):
        """ returns the template for the given object and action
        """
        
class INotificationSender(Interface):
    """
    """
    
    def send(action, message, recipients):
        """ send the notifications
        """

class INotificationForm(Interface):
    """ Marker interface for notification form
    """

class INotificationEnabled(Interface):
    """
    """
    
    def transitions():
        """ returns a list of transition names for which notifications are sent (None for all)
        """

class INotificationRecipient(Interface):
    """ A recipient
    """
    name = Attribute('name')
    email = Attribute('email')

class INotificationRecipientProvider(Interface):
    """
    """
    
    def recipients(workflow, action):
        """ returns a list of recipients (objects implementing INotificationRecipient) to be notified
        """
        
class INotificationTemplateProvider(Interface):
    """
    """
    
    def template(workflow, action):
        """ returns a template to be used as the message
            
            the following keywords may be used in the form of %(keyword)s by the corresponding string:
            
            name:       the full name of the receiver
            url:        the url to the content object
            title:      the title of the content object
            old_state:  the old state of the content object
            new_state:  the new state of the content object
            transition: the transition made on the the content object
            issuer:     the full name of the issuer
        """
