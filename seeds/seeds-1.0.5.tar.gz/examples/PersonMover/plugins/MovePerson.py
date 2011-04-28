# -*- coding: utf-8 -*-
"""
TODO: action description
TODO: make this work for all topologies
"""

__author__ = "TODO"
__credits__ = "TODO"

import csv
import random

from seeds.Action import *

class MovePerson(Action):
    """ TODO: description

        Config file settings:
        [MovePerson]
        epoch_start = 3    Epoch at which to start writing (default 0)
        epoch_end = 100    Epoch at which to stop writing (default end of experiment)
        prob_movement = 0.2 Probability of moving during a given epoch (default 0.5)
        resource = energy  Name of the resource the person deposits
        res_drop_amount = 1 Units of resource dropped per person per update

    """
    def __init__(self, world):
        """Initialize the MovePerson Action"""
        Action.__init__(self, world)

        self.epoch_start = self.world.config.getint('MovePerson', 'epoch_start', 0)
        self.epoch_end = self.world.config.getint('MovePerson', 'epoch_end',
                                                  default=self.world.config.getint('Experiment', 'epochs', default=-1))
        self.frequency = self.world.config.getint('MovePerson', 'frequency', 1)
        self.prob_movement = self.world.config.getfloat('MovePerson', 'prob_movement', 0.5)
        self.resource = self.world.config.get('MovePerson', 'resource')
        self.res_drop_amount = self.world.config.getfloat('MovePerson', 'res_drop_amount')
        self.name = "MovePerson"

        node = random.choice(self.world.topology_manager.topologies[0].graph.nodes())
        self.cell = self.world.topology_manager.topologies[0].graph.node[node]['cell']

    def update(self):
        """Execute the Action"""
        if self.skip_update():
	        return

        if random.random() < self.prob_movement:
            neighbor = random.choice(self.world.topology_manager.topologies[0].get_neighbors(self.cell.node))
            print "Person Moving from Cell %d to %d" % (self.cell.id, neighbor.id)
            self.cell = neighbor

        # TODO deposit resource in node's resource

