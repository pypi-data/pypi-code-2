#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Classes for Models NetworkX version.

See details in models.py
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
            new_node = network.next_node()
            network.add_edges_from([(network.nodes()[edge_target], new_node) for edge_target in edge_targets])

            running_condition = True
            return running_condition 
    else:
        def step(self, network):
            repeated_nodes = []
            for node in network:
                repeated_nodes.extend([node]*network.degree(node))
            new_node = network.next_node()
            edge_targets = []
            while len(edge_targets) < self.m:
                x = random.choice(repeated_nodes)
                if x not in edge_targets:
                    edge_targets.append(x)
            network.add_node(new_node)
            network.add_edges_from([(edge_target, new_node) for edge_target in edge_targets])

            running_condition = True
            return running_condition


class NodeFailureModel(Model):
    """It deletes a random node in a step."""

    def __init__(self):
        self.name = "NodeFailureModel"
        self.is_epidemic = False

    def step(self, network):
        nodes = network.nodes()
        if len(nodes) == 0:
            return False
        network.remove_node(random.choice(nodes))

        return ( len(nodes) > 1 )

    def minimum_nodes(self):
        return 2

class InfectiveFailureModel(Model):
    """It deletes a random node in a step."""

    def __init__(self):
        self.name = "InfectiveFailureModel"
        self.is_epidemic = True

    def step(self, network):
        infective_nodes = network.infective_nodes()
        if len(infective_nodes) == 0:
            return False
        network.remove_node(random.choice(infective_nodes))

        return (len(infective_nodes) > 1)

    def minimum_nodes(self):
        return 2

class SI_Model(Model):
    """Suscebtible -> Infective model"""

    def __init__(self, beta):
        self.name = "SI_Model, beta=%g" % beta
        self.is_epidemic = True
        self.beta = beta

    def step(self, network):
        infective_nodes = network.infective_nodes()
        if len(infective_nodes) == 0:
            return False
        for i in infective_nodes:
            nb = network.neighbors(i)
            network.random_disease(self.beta, nb)

        return True

    def minimum_nodes(self):
        return 1
