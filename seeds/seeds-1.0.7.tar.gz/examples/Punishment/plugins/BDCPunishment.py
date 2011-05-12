# -*- coding: utf-8 -*-
""" TODO: comments
"""

__author__ = "Brian Connelly <bdc@msu.edu>"
__credits__ = "Brian Connelly"

from seeds.cell.Cell import *
import random

class BDCPunishment(Cell):
    """
    TODO
    """

    types = ['Empty', 'Cooperator', 'Cooperator-Punisher', 'Noncooperator', 'Noncooperator-Punisher']

    EMPTY = 0
    COOPERATOR = 1
    COOPERATOR_PUNISHER= 2
    NONCOOPERATOR = 3
    NONCOOPERATOR_PUNISHER= 4

    def __init__(self, world, topology, node, id, type=-1):
        """Initialize a BDCPunishment object

        The type for the cell is selected at random.

        Parameters:

        *world*
            A reference to the World
        *topology*
            A reference to the topology in which the Cell will reside
        *node*
            A reference to the node on which the Cell exists
        *id*
            A unique ID for the cell
        *type*
            The type of cell to initialize (-1 for random)

        """

        Cell.__init__(self,world,topology,node,id)

        if type == -1:
            self.type = random.randint(0,len(self.types)-1)
        else:
            self.type = type
        
        self.topology.increment_type_count(self.type)

        self.death_base = self.world.config.getfloat('BDCPunishment', 'death_base')
        self.cost_coop = self.world.config.getfloat('BDCPunishment', 'cost_coop')
        self.benefit_coop = self.world.config.getfloat('BDCPunishment', 'benefit_coop')
        self.cost_punishment = self.world.config.getfloat('BDCPunishment', 'cost_punishment')
        self.punishment = self.world.config.getfloat('BDCPunishment', 'punishment')
        self.mutation = self.world.config.getfloat('BDCPunishment', 'mutation')

    def __str__(self):
        """Produce a string to be used when the object is printed"""
        return 'BDCPunishment Cell %d Type %d (%s)' % (self.id, self.type, self.types[self.type])

    def type(self):
        """Return the name of the type of this cell"""
        return self.types[self.type]

    def update(self, neighbors):
        """Update the cell based on its neighbors

        TODO: doc

        Parameters:

        *neighbors*
            A list of neighboring cells

        """

        neighbor = random.choice(neighbors)

        if self.type == self.EMPTY:
            newtype = neighbor.type

            # Loss/gain of cooperation through mutation during replication
            if newtype == self.COOPERATOR and random.random() < self.mutation:
                newtype = self.NONCOOPERATOR
            if newtype == self.COOPERATOR_PUNISHER and random.random() < self.mutation:
                newtype = self.NONCOOPERATOR_PUNISHER
            if newtype == self.NONCOOPERATOR and random.random() < self.mutation:
                newtype = self.COOPERATOR
            if newtype == self.NONCOOPERATOR_PUNISHER and random.random() < self.mutation:
                newtype = self.COOPERATOR_PUNISHER

            # Loss/gain of punishment through mutation during replication
            if newtype == self.COOPERATOR_PUNISHER and random.random() < self.mutation:
                newtype = self.COOPERATOR
            if newtype == self.NONCOOPERATOR_PUNISHER and random.random() < self.mutation:
                newtype = self.NONCOOPERATOR
            if newtype == self.COOPERATOR and random.random() < self.mutation:
                newtype = self.COOPERATOR_PUNISHER
            if newtype == self.NONCOOPERATOR and random.random() < self.mutation:
                newtype = self.NONCOOPERATOR_PUNISHER

            self.type = newtype
            self.topology.update_type_count(self.EMPTY, self.type)

        elif self.type == self.COOPERATOR:
            death = self.death_base + self.cost_coop

            if neighbor.type == self.COOPERATOR or neighbor.type == self.COOPERATOR_PUNISHER:
                death = death - self.benefit_coop

            if random.random() < death:
                self.topology.update_type_count(self.type, self.EMPTY)            
                self.type = self.EMPTY

        elif self.type == self.COOPERATOR_PUNISHER:
            death = self.death_base + self.cost_coop + self.cost_punishment

            if neighbor.type == self.COOPERATOR or neighbor.type == self.COOPERATOR_PUNISHER:
                death = death - self.benefit_coop

            if random.random() < death:
                self.topology.update_type_count(self.type, self.EMPTY)            
                self.type = self.EMPTY

        elif self.type == self.NONCOOPERATOR:
            death = self.death_base

            if neighbor.type == self.COOPERATOR_PUNISHER or neighbor.type == self.NONCOOPERATOR_PUNISHER:
                death = death + self.punishment

            if random.random() < death:
                self.topology.update_type_count(self.type, self.EMPTY)            
                self.type = self.EMPTY

        elif self.type == self.NONCOOPERATOR_PUNISHER:
            death = self.death_base + self.cost_punishment

            if neighbor.type == self.COOPERATOR_PUNISHER or neighbor.type == self.NONCOOPERATOR_PUNISHER:
                death = death + self.punishment

            if random.random() < death:
                self.topology.update_type_count(self.type, self.EMPTY)            
                self.type = self.EMPTY

