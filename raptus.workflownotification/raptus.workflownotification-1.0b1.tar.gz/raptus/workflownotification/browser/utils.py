from zope.component import queryAdapter
from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from raptus.workflownotification.interfaces import INotificationEnabled, INotificationRecipientProvider, INotificationTemplateProvider, INotificationUtils

class WorkflownotificationView(BrowserView):
    """ View providing utility methods concerning workflownotifications
    """
    implements(INotificationUtils)
    
    def getEnabledTransitionsFor(self, objs):
        """ returns all transitions which have notifications enabled for the given objects
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if not type(objs) is type([]):
            objs = [objs,]
        transitions = []
        for obj in objs:
            if type(obj) is type(''):
                obj = portal.restrictedTraverse(obj)
            enabler = INotificationEnabled(obj, None)
            
            if enabler:
                transitions.extend(enabler.transitions())
        return transitions
    
    def getWorkflowFor(self, obj):
        """ returns the workflow_id for the given object
        """
        wftool = getToolByName(obj, 'portal_workflow')
        chain = wftool.getChainFor(obj)
        return chain[0]
    
    def getRecipientsFor(self, obj, action):
        """ returns a list of default recipients for the given object and action
        """
        recipients = []
        workflow = self.getWorkflowFor(obj)
        provider_global = queryAdapter(obj, INotificationRecipientProvider)
        if provider_global is not None:
            recipients.extend(provider_global.recipients(workflow, action))
        
        provider_workflow = queryAdapter(obj, INotificationRecipientProvider, name=workflow)
        if provider_workflow is not None:
            recipients.extend(provider_workflow.recipients(workflow, action))
        
        provider_transition = queryAdapter(obj, INotificationRecipientProvider, name='%s.%s' % (workflow, action))
        if provider_transition is not None:
            recipients.extend(provider_transition.recipients(workflow, action))
            
        return recipients
    
    def getTemplateFor(self, obj, action):
        """ returns the template for the given object and action
        """
        workflow = self.getWorkflowFor(obj)
        provider_transition = queryAdapter(obj, INotificationTemplateProvider, name='%s.%s' % (workflow, action))
        if provider_transition is not None:
            return provider_transition.template(workflow, action)
        
        provider_workflow = queryAdapter(obj, INotificationTemplateProvider, name=workflow)
        if provider_workflow is not None:
            return provider_workflow.template(workflow, action)
            
        provider_global = queryAdapter(obj, INotificationTemplateProvider)
        if provider_global is not None:
            return provider_global.template(workflow, action)
            
        return u""
