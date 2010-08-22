#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module handling network evolution.

It handles evolution models and measurements.

"""

from __future__ import division

import sys
sys.path.insert(0, "..")
import networkx
#print "NetworkX version %s is used." % networkx.__version__
import random
import numpy
import models

graphmodule_version = "NetworkX %s" % networkx.__version__

# Epidemic states. 
STATE_SUBSCEPTIBLE = 0
STATE_INFECTIVE = 1
STATE_RECOVERED = 2

class EpidemicNode:
    """Nodes for epidemic processes on complex networks.

    state is a character, it can be:
    - s : susceptible
    - i : infective
    - r : recovered

    birth is an integer, it is the step in which the node was created

    name should be an integer or string

    """

    def __init__(self, birth, name):
        self.birth = birth
        self.state = STATE_SUBSCEPTIBLE
        self.name = name

    def get_disease(self, period):
        if self.state != STATE_INFECTIVE:
            self.state = STATE_INFECTIVE
            self.state_started = period

    def recover(self, period):
        self.state = STATE_RECOVERED
        self.state_started = period

    def is_infective(self):
        return self.state == STATE_INFECTIVE

    def __str__(self):
        return str(self.name)


class Network(networkx.Graph):
    """Some addition to the nx.Graph() class.
    """

    def __init__(self, data=None, name="", is_epidemic = False):
        networkx.Graph.__init__(self, data, name)
        self.next_node_name = 0
        self.is_epidemic = is_epidemic
        self.period = 0

    def next_node(self):
        if self.is_epidemic:
            node = EpidemicNode(birth=self.period, name=self.next_node_name)
        else:
            node = self.next_node_name
        self.next_node_name += 1
        return node

    def add_new_cycle(self, num):
        """Add a cycle of 'num' new nodes."""
        nodes = [self.next_node() for i in xrange(num)]
        self.add_cycle(nodes)

    def random_disease(self, beta, nodes=None):
        """Each node get disease with beta probability."""
        if nodes is None:
            nodes = self.nodes()
        for n in nodes:
            if random.random() < beta:
                n.get_disease(self.period)

    def infective_nodes(self):
        return [ node for node in self if node.is_infective() ]

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

    def m_clustering(self, params):
        return {"average_clustering": networkx.average_clustering(network)}

    def m_component_properties(self, params):
        """It returns with the properties of the components.

        Input:

        - network (Graph or Network object): the network on which it works
        - params (dict): the parameters.
          All parameter is optional.

        other_components means components without the largest one
        """

        properties = {}
        components = networkx.component.connected_components(self)
        properties["number_of_nodes"] = number_of_nodes = len(self)
        properties["number_of_edges"] = number_of_edges = self.number_of_edges()
        properties["number_of_components"] = number_of_components = len(components)
        properties["order_of_biggest_component"] = order_of_biggest_component = len(components[0])
        if number_of_components == 1:
            properties["average_order_of_other_components"] = 0
        else:
            properties["average_order_of_other_components"] = (number_of_nodes - order_of_biggest_component)/(number_of_components - 1)

        return properties

    def m_diameter(self, params):
        properties = {}
        components = networkx.component.connected_components(self)
        return {"diameter_of_biggest_component": networkx.diameter(self.subgraph(components[0]))}

    def m_write_dot(self, params):
        """Write the actual network into a dot file."""
        networkx.write_dot(self, params["file"] +".dot")
        return {}

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
        for n in self:
            state = n.state
            if state in states.keys():
                number_of_states[states[state]] += 1 
            else:
                raise ValueError, "State '%s' is not known" % state

        components = networkx.component.connected_components(self)
        number_of_states["number_of_infective_components"] = 0
        for c in components:
            for node in c:
                if node.state == STATE_INFECTIVE:
                    number_of_states["number_of_infective_components"] += 1
                    break

        return number_of_states


def epidemic_BA_network(n=100, p_i = 0.09):
    """Builds a Barabasi-Albert graph for epidemic models."""

    network = Network(name="epidemic_network", is_epidemic=True)
    model = models.BarabasiAlbertModel(3)
    model.initial(network)
    for i in xrange(n):
        model.step(network)
    network.random_disease(p_i)
    return network
