from Products.DCWorkflow.browser.workflow import DCWorkflowDefinitionAddView

from collective.subtractiveworkflow.workflow import SubtractiveWorkflowDefinition

class SubtractiveWorkflowDefinitionAddView(DCWorkflowDefinitionAddView):
    """Add view
    """
    
    klass = SubtractiveWorkflowDefinition
    description = u'Add a web-configurable subtractive workflow.'