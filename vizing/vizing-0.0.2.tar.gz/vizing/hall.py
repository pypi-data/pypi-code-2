r"""
Python components for calculating Hall inequalities.

AUTHORS:

- Matthew Henderson (2010-12-30): initial version
"""

#********************************************************************************
#       Copyright (C) 2010 Matthew Henderson <matthew.james.henderson@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#********************************************************************************

from utils import support_subgraph, independence_number 

def hall_number(graph, list_assignment, colour):
    """
    Compute the independence number of the subgraph induced by those 
    vertices in 'graph' having 'colour' in their list.
    """
    return independence_number(support_subgraph(graph, colour, list_assignment))

def hall_sum(graph, list_assignment, colours):
    """
    Sum Hall numbers over all monochromatic subgraphs.
    """
    return sum([hall_number(graph, list_assignment, colour) for colour in colours])

def hall_inequality(graph, list_assignment, colours):
    """
    Decide whether the Hall inequality for graph is satisfied
    """
    return hall_sum(graph, list_assignment, colours) >= len(graph.nodes())

def hall_inequality_induced_by(graph, list_assignment, colours, vertices):
    """
    Check Hall's inequality for a subgraph of 'graph' induced by 'vertices'.
    """
    return hall_inequality(graph.subgraph(vertices), list_assignment, colours)

