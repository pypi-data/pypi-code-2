#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module handling network evolution.

It handles evolution models and measurements.

"""

from __future__ import division

#from networkx_network import *
from random import random
import igraph
from models import BarabasiAlbertModel
import numpy

graphmodule_version = "IGraph %s" % igraph.__version__

# Epidemic states. 
STATE_SUBSCEPTIBLE = 0
STATE_INFECTIVE = 1
STATE_RECOVERED = 2

class Network(igraph.Graph):
    """Calculate useful functions in addition to the igraph.Graph() class.

    """

    def __init__(self, data=None, name="", is_epidemic = False):
        igraph.Graph.__init__(self, 0)
        self.is_epidemic = is_epidemic
        self.name = name
        self.period = 0
        self.add_edges_from = self.add_edges

    def __len__(self):
        return self.vcount()

    def number_of_nodes(self):
        return self.vcount()

    def number_of_edges(self):
        return self.ecount()

#    def remove_vertices(self, vs):
#        """Delete vertices, and remove them from the
#        infective_vertices set, if necessary.
#
#        vs: a single vertex ID or the list of vertex IDs
#              to be deleted.
#        """
#        if isinstance(vs, int):
#            vs = [vs]
#        self.delete_vertices(vs)

    def add_node(self, **kwords):
        """Add a new node to the graph.

        kwords is for compatibility with NetworkX.
        there is an obligatory 'node' argument not used in igraph.
        """
        self.add_vertices(1)
        self.vs[self.vcount()-1]["state"] = STATE_SUBSCEPTIBLE
        return self.vcount() - 1

    def add_new_cycle(self, num):
        """Add a cycle of 'num' new nodes."""
        n = self.number_of_nodes()
        self.add_vertices(num)
        self.add_edges([(i, i+1) for i in xrange(n, n+num-1)])
        self.add_edges((n, n+num-1))


    def random_disease(self, beta, vertices=None, other_subsceptible=False):
        """Each node get disease with beta probability.
        
        vertices (default False): if it is a list of vertices, it will use just
            these vertices, otherwise all vertices.
        other_subceptible (default False): if True the vertices other then
           have been infective will be set to STATE_SUBSCEPTIBLE
        """
        if vertices is None:
            vertices = self.vs
        else:
            vertices = [self.vs[i] for i in vertices]
        for vertex in vertices:
            if random() < beta:
                vertex["state"] = STATE_INFECTIVE
            elif other_subsceptible:
                vertex["state"] = STATE_SUBSCEPTIBLE

    def infective_vertices(self):
        return [vertex.index for vertex in self.vs(state=STATE_INFECTIVE)]

    """Measurement methods
    
    The functions below are the  measurement methods of the Network.
    These methods are called in the NetworkEvoluion class.
    All of measurement method have some common property.

    parameters:
        - params: dictionary
            to store parameters, usually empty

    returns:
        with a dictionary of the measured values
        (one method can measure mode values)

    """

    def m_degree_distribution(self, params):
        """Values calculated from degree distribution.

    The exponent end error are caculated with the equations written in [1] page 4.

    [1]
    @article{newman-2005-46,
      url = {http://arxiv.org/abs/cond-mat/0412004},
      author = {M.~E.~J. Newman},
      title = {Power laws, Pareto distributions and Zipf's law},
      journal = {Contemporary Physics},
      volume = {46},
      pages = {323},
      year = {2005},
    }

    [2]
    @misc{clauset-2007,
      url = {http://arxiv.org/abs/0706.1062},
      author = {Aaron Clauset and Cosma Rohilla Shalizi and M.~E.~J. Newman},
      title = {Power-law distributions in empirical data},
      year = {2007}
    }

        """

        min_deg = 5.5
        deg = numpy.array([d for d in self.degree() if d > min_deg])
        summa = sum(numpy.log(deg/min_deg))
        n = len(deg)
        gamma = 1 + n/summa
        sigma = numpy.sqrt(n+1) / summa

        return {"exponent": gamma, "exponent_sigma": sigma}

    def m_component_properties(self, params):
        """It returns with the properties of the components.

        Input:

        - network (Graph or Network object): the network on which it works
        - params (dict): the parameters.

        other_components means components without the largest one
        """

        properties = {}
        components = self.components()
        properties["number_of_nodes"] = number_of_nodes = self.vcount()
        properties["number_of_edges"] = number_of_edges = self.number_of_edges()
        properties["number_of_components"] = number_of_components = len(components)
        properties["order_of_biggest_component"] = \
                order_of_biggest_component = max(components.sizes())
        if number_of_components == 1:
            properties["average_order_of_other_components"] = 0
        else:
            properties["average_order_of_other_components"] = \
                (number_of_nodes - order_of_biggest_component)/(number_of_components - 1)

        return properties

    def m_diameter(self, params):
        return {"diameter": self.diameter()}

    def m_write_dot(self, params):
        """Write the actual network into a gml file."""
#TODO It writes to gml instead of dot, because igraph can not read from dot.
        self.write_gml(params["file"] + ".gml")
        return {}

    def m_states(self, params):
        """States of nodes.

        Return a dictionary with the number of nodes
        with the given state.

        Example:
        {"state_susceptible": 1020, "state_infective": 254, "state_recovered": 531}

        """

        states = {0: "state_susceptible", 1: "state_infective", 2: "state_recovered"}
        number_of_states = {}
        for state in states.values():
            number_of_states[state] = 0
        for key in states.keys():
            number_of_states[states[key]] = self.vs["state"].count(key)

        components = self.components()
        number_of_states["number_of_infective_components"] = 0
        for i in xrange(len(components)):
            if STATE_INFECTIVE in components.subgraph(i).vs["state"]: 
                number_of_states["number_of_infective_components"] += 1

        return number_of_states


def epidemic_BA_network(n=100, p_i = 0.09):
    """Builds a Barabasi-Albert graph for epidemic models."""

    network = Network(name="epidemic_network", is_epidemic=True)
    model = BarabasiAlbertModel(3)
    model.initial(network)
    for i in xrange(n):
        model.step(network)
    network.random_disease(p_i, other_subsceptible=True)
    return network
