from plone.app.contentmenu.menu import WorkflowMenu as BaseWorkflowMenu

from raptus.workflownotification.interfaces import INotificationEnabled

class WorkflowMenu(BaseWorkflowMenu):
    
    def getMenuItems(self, context, request):
        items = super(WorkflowMenu, self).getMenuItems(context, request)
        notification = INotificationEnabled(context, None)
        if notification is None:
            return items
        transitions = notification.transitions()
        
        for item in items:
            if item['extra']['id'][20:] in transitions:
                item['extra']['class'] = '%s workflownotification' % item['extra']['class']
                item['action'] = item['action'].replace('content_status_modify', '@@workflownotification_form')
                
        return items
