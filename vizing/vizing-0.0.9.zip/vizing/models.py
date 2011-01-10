r"""
Python components for modelling list colourings of graphs.

This module provides several different models of list-colouring problems. 
Constraint models using the ``python-constraint`` and ``or-tools`` libraries
are the first to be implemented.

AUTHORS:

- Matthew Henderson (2010-12-23): initial version
"""

#********************************************************************************
#       Copyright (C) 2010 Matthew Henderson <matthew.james.henderson@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#********************************************************************************

import constraint
#from constraint_solver import pywrapcp

from utils import vtc_to_ctv

class _CP_model_:

    """ 
    Constraint model via python-constraint.

    REFERENCES: 

    [pyco] http://labix.org/python-constraint
    """

    def __init__(self, graph, list_assignment):
    
        """ 
        XXX doc XXX 
        """

        self.graph = graph
        self.list_assignment = list_assignment
        self.problem = constraint.Problem()
        for node in self.graph.nodes():
            self.problem.addVariable(node, self.list_assignment.get(node)) 
        for edge in self.graph.edges():
            self.problem.addConstraint(constraint.AllDifferentConstraint(), edge)

    def first_solution(self):

        """ 
        XXX doc XXX 
        """

        return vtc_to_ctv(self.problem.getSolution())

class _or_CP_model_:

    """ 
    Constraint model via Google or-tools.

    REFERENCES:

    [orto] http://code.google.com/p/or-tools/
    """

    def __init__(self, graph, list_assignment):

        """
        XXX doc XXX
        """

        self.graph = graph
        self.list_assignment = list_assignment
        self.solver = pywrapcp.Solver('xxxNAMExxx')
        self.var = {}
        self.solution = {}
        for node in self.graph.nodes():
            self.var[node] = self.solver.IntVar(self.list_assignment.get(node))
        for edge in self.graph.edges():
            self.solver.Add(self.solver.AllDifferent([self.var[node] for node in edge], False))

    def first_solution(self):

        """ 
        XXX doc XXX 
        """
    
        var_list = self.var.values()
        vars_phase = self.solver.Phase(var_list,
                                       self.solver.INT_VAR_SIMPLE, 
                                       self.solver.INT_VALUE_SIMPLE)
        solution = self.solver.Assignment()
        solution.Add(var_list)
        collector = self.solver.FirstSolutionCollector(solution)
        self.solver.Solve(vars_phase, [collector])
        current = collector.solution(0)
        if collector.solution_count() == 1:
            for var in self.var:  
                self.solution[var] = current.Value(self.var[var])
        return vtc_to_ctv(self.solution)

def list_colouring(graph, list_assignment, model = 'CP'):

    r"""
    This function returns a list-colouring of a list-colourable graph.

    INPUT:

    - ``graph`` -- A ``networkx`` graph.
    - ``list_assignment`` -- A mapping from nodes of ``graph`` to lists of colours.
    - ``model`` -- Choices are 'CP' for constraint programming via 
      ``python-constraint`` or ``or`` for constraint programming via Google 
      ``or-tools``.

    OUTPUT:

    ``dictionary`` -- the list colouring

    EXAMPLES:

    >>> import networkx
    >>> G = networkx.complete_graph(10)
    >>> L = dict([(node, range(10)) for node in G.nodes()])
    >>> from vizing.models import list_colouring
    >>> list_colouring(G, L, model = 'CP')
    {0: [9], 1: [8], 2: [7], 3: [6], 4: [5], 5: [4], 6: [3], 7: [2], 8: [1], 9: [0]}

    AUTHORS:
    - Matthew Henderson (2010-12-23)
    """

    if model == 'CP':
        return _CP_model_(graph, list_assignment).first_solution()
    if model == 'or':
        return _or_CP_model_(graph, list_assignment).first_solution()
    else:
        raise Exception('No such model')

