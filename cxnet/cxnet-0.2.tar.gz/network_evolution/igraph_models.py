#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Classes for Models. IGraph version.

Classes for Models
Main model types: growth, random remove, attack, spread of infection

Both have:
- step() method.
- name parameter including the important parameters.
- minimum_nodes method returning with the minimum nodes required the model.
- is_epidemic parameter which is True if the model needs states of nodes.

The step() method returns with the model level running condition.
If it is False, running will be discarded.

"""

from __future__ import division

import random

mycython_module = False
try:
    import mycython
except ImportError:
    mycython_module = False
else:
    mycython_module = True


class Model:
    def __str__(self):
        return self.name


class BarabasiAlbertModel(Model):
    """See in networkx/generators/random_graphs.py .
    """
    def __init__(self, m):
        self.m = m
        self.name = "BarabasiAlbertModel, m=%d" % m
        self.is_epidemic = False

    def minimum_nodes(self):
        return self.m + 1

    def initial(self, network):
        network.add_new_cycle(self.m)

    if mycython_module:
        def step(self, network):
            edge_targets = mycython.choice(network.degree(), self.m)
            new_node = network.add_node()
            network.add_edges_from([(edge_target, new_node) for edge_target in edge_targets])

            running_condition = True
            return running_condition 
    else:
#TODO else part is not checked for igraph
        def step(self, network):
            repeated_nodes = []
            for node in xrange(network.vcount()):
                repeated_nodes.extend([node]*network.degree(node))
            edge_targets = []
            while len(edge_targets) < self.m:
                x = random.choice(repeated_nodes)
                if x not in edge_targets:
                    edge_targets.append(x)
            new_node = network.add_node()
            network.add_edges_from([(edge_target, new_node) for edge_target in edge_targets])

            running_condition = True
            return running_condition


class NodeFailureModel(Model):
    """It deletes a random node in a step."""

    def __init__(self):
        self.name = "NodeFailureModel"
        self.is_epidemic = False

    def step(self, network):
        if network.vcount() == 0:
            return False
        network.delete_vertices(random.choice(xrange(network.vcount())))

        return ( network.vcount() > 1 )

    def minimum_nodes(self):
        return 2


class InfectiveFailureModel(Model):
    """It deletes a random node in a step."""

    def __init__(self):
        self.name = "InfectiveFailureModel"
        self.is_epidemic = True

    def step(self, network):
        infective_vertices = network.infective_vertices()
        if not infective_vertices:
            return False
        network.delete_vertices(random.choice(infective_vertices))

        return (len(infective_vertices) > 1)

    def minimum_nodes(self):
        return 2


class SI_Model(Model):
    """Suscebtible -> Infective model"""

    def __init__(self, beta):
        self.name = "SI_Model, beta=%g" % beta
        self.is_epidemic = True
        self.beta = beta

    def step(self, network):
        infective_vertices = network.infective_vertices()
        if not infective_vertices:
            return False
        for vertex in infective_vertices:
            nb = network.neighbors(vertex)
            network.random_disease(self.beta, nb)

        return True

    def minimum_nodes(self):
        return 1
