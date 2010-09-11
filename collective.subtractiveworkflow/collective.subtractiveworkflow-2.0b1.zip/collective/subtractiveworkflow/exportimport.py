from rwproperty import getproperty, setproperty

from zope.component import adapts

from Products.GenericSetup.interfaces import ISetupEnviron

from Products.DCWorkflow.exportimport import DCWorkflowDefinitionBodyAdapter
from Products.DCWorkflow.exportimport import WorkflowDefinitionConfigurator
from Products.DCWorkflow.exportimport import _initDCWorkflow

from collective.subtractiveworkflow.interfaces import ISubtractiveWorkflowDefinition

class SubtractiveWorkflowDefinitionBodyAdapter(DCWorkflowDefinitionBodyAdapter):
    """Body adapter for the subtractive workflow
    """

    adapts(ISubtractiveWorkflowDefinition, ISetupEnviron)

    @getproperty
    def body(self):
        wfdc = SubtractiveWorkflowDefinitionConfigurator(self.context)
        return wfdc.__of__(self.context).generateWorkflowXML()
    
    @setproperty
    def body(self, body):
        wfdc = SubtractiveWorkflowDefinitionConfigurator(self.context)

        (workflow_id, title, state_variable, initial_state, states, 
         transitions, variables, worklists, permissions, 
         scripts, description, manager_bypass,
         creation_guard) = wfdc.parseWorkflowXML(body, 'utf-8')

        _initDCWorkflow(self.context, title, description, manager_bypass,
                        creation_guard, state_variable,
                        initial_state, states, transitions, variables,
                        worklists, permissions, scripts, self.environ)

class SubtractiveWorkflowDefinitionConfigurator(WorkflowDefinitionConfigurator):
    """We need a custom configurator because the original does and explicit
    meta_type check.
    """
    
    def __init__(self, obj):
        self._obj = obj

    def getWorkflowInfo(self, workflow_id):
        workflow = self._obj
        workflow_info = {'id'          : workflow_id, 
                         'meta_type'   : workflow.meta_type,
                         'title'       : workflow.title_or_id(),
                         'description' : workflow.description}

        if ISubtractiveWorkflowDefinition.providedBy(workflow):
            self._extractDCWorkflowInfo(workflow, workflow_info)

        return workflow_info
