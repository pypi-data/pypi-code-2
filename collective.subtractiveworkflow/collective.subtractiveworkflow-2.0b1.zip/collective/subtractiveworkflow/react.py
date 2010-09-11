from zope.component import adapter
from Products.DCWorkflow.interfaces import IAfterTransitionEvent

from Products.CMFCore.utils import getToolByName

from collective.subtractiveworkflow.interfaces import ISubtractiveWorkflowDefinition

@adapter(IAfterTransitionEvent)
def object_transitioned(event):
    """Subtractive workflows need to be able to modify the permissions of an
    object after other workflows may have done their work. This event handler
    will be called after a transition has been invoked and "re-play" the
    role mappings of all workflows in the chain, in order, so that the
    correct "subtraction" can take place.
    """
    
    obj = event.object
    wf_tool = getToolByName(obj, 'portal_workflow', None)
    
    if wf_tool is None:
        return
    
    wf = event.workflow
    
    # If there's only one workflow in the chain, there's no need to be too
    # clever.
    chain = wf_tool.getChainFor(obj)
    if not chain or not isinstance(chain, (list, tuple,)):
        return
    
    # If this is not a subtractive workflow and there's only one thing in the
    # chain, do nothing, assuming the chain has done its thing.
    if len(chain) == 1 and not ISubtractiveWorkflowDefinition.providedBy(wf):
        return
    
    wfs_in_chain = [wf_tool.getWorkflowById(wf_id) for wf_id in chain]
    
    found = False
    for wf in wfs_in_chain:
        if ISubtractiveWorkflowDefinition.providedBy(wf):
            found = True
            break
    
    # Do nothing if there are no subtractive workflows. The usual DCWorkflow
    # behaviour is to let the most recently entered state determine the full
    # permission mapping, regardless of the states of the other workflows in
    # the chain.
    if not found:
        return
    
    # Let each update permissions in turn, so that later workflows can
    # override earlier ones.
    for wf in wfs_in_chain:
        wf.updateRoleMappingsFor(obj)
