# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

class WorkflowEdge(object):
    """
    Workflow graph edge (transition)
    """
    def __init__(self, name, target):
        """
        Constructor
        """
        self.name = name
        self.target = target

class WorkflowNode(object):
    """
    A workflow graph node (state)
    """
    def __init__(self, name):
        """
        Constructor
        """
        self.name = name
        self.edges = {}

    def add_edge(self, edge):
        """
        Add a transition
        """
        self.edges[edge.name] = edge.target


class WorkflowGraph(object):
    """
    A workflow graph
    """
    def __init__(self, name, pwtool):
        """
        Constructor
        """
        self.name = name
        self.pwtool = pwtool
        self.nodes = {}
        self.edges = {}

    def load(self):
        """
        Load the workflow graph from Plone
        """
        workflow = getattr(self.pwtool, self.name)
        
        # Load transitions
        trns = workflow.transitions.objectValues()
        for trn in trns:
            name = trn.getId()
            target = trn.new_state_id
            self.edges[name] = WorkflowEdge(name, target)

        # Load states
        states = workflow.states.objectValues()
        for state in states:
            name = state.getId()
            node = WorkflowNode(name)
            trns = state.getTransitions()
            for trn in trns:
                node.add_edge(self.edges[trn])
            self.nodes[name] = node

    def find_path(self, start, end):
        """
        Return a list of transition names to go from start to end
        """
        if start == end:
            return []
        
        reachable = { start: [] }
        new = [ start ]
        while new:
            old = new
            new = []

            # For every node found on the previous iteration
            for src in old:
                edges = reachable[src]
                for edge, trgt in self.nodes[src].edges.items():
                    if not trgt in reachable:
                        # New node found, yeah !                        
                        reachable[trgt] = edges + [ edge ]
                        if trgt == end:
                            return reachable[trgt]
                        new.append(trgt)
            
        raise RuntimeError, "Cannot reach %r from %r on workflow %r" % (start, end, self.name)

class MultiWorkflowGraph(object):
    """
    All the workflows of a site
    """
    def __init__(self, plone):
        """
        Constructor (needs a Plone site instance as parameter)
        """
        self.plone = plone
        self.pwtool = getToolByName(self.plone, "portal_workflow")
        self.workflows = {}
        self.load()

    def load(self):
        """
        Load the workflows from the Plone site
        """
        workflows = self.pwtool.objectIds()
        for wfid in workflows:
            workflow = WorkflowGraph(wfid, self.pwtool)
            workflow.load()
            self.workflows[wfid] = workflow

    def set_to(self, obj, end_state):
        """
        Set given obj to given state
        """
        start = self.pwtool.getInfoFor(obj, "review_state")
        wf_ids = self.pwtool.getChainFor(obj)
        wf_id = wf_ids[0]   
        workflow = self.workflows[wf_id]
        path = workflow.find_path(start, end_state)
        for edge in path:
            self.pwtool.doActionFor(obj, edge)
        return path
        
def set_to(self, obj, end_state):
    """
    External method wrapper
    """
    graph = MultiWorkflowGraph(self)
    return graph.set_to(obj, end_state)
    
