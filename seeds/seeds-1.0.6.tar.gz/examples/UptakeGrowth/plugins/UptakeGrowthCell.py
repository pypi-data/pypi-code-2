# -*- coding: utf-8 -*-
""" TODO
"""

__author__ = "Brian Connelly <bdc@msu.edu>"
__credits__ = "Brian Connelly"

from seeds.cell.Cell import *
import random

class UptakeGrowthCell(Cell):
    """ TODO
    """

    types = ['Empty', 'Living']

    EMPTY = 0
    LIVING = 1

    def __init__(self, world, topology, node, id, type=-1):
        """Initialize a UptakeGrowthCell object

        The type for the cell is selected at random.

        Parameters:

        *world*
            A reference to the World
        *topology*
            A reference to the topology in which the Cell will reside
        *node*
            A reference to the node on which the Cell resides
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

        self.death = self.world.config.getfloat('UptakeGrowthCell', 'death', default=0.0)
        self.mutation = self.world.config.getfloat('UptakeGrowthCell', 'mutation', default=0.005)
        self.mutation_sigma = self.world.config.getfloat('UptakeGrowthCell', 'mutation_sigma', default=0.05)
        self.energy_uptake = self.world.config.getfloat('UptakeGrowthCell', 'energy_uptake', default=0.05)
        self.energy_cost = self.world.config.getfloat('UptakeGrowthCell', 'energy_cost', default=0.05)
        self.daughter_frac_energy = self.world.config.getfloat('UptakeGrowthCell', 'daughter_frac_energy', default=0.5)

        self.resource = self.world.config.get('UptakeGrowthCell', 'resource', default='res')

        self.uptake_rate = random.normalvariate(0.5, 0.2)
        self.energy = 1.0

    def __str__(self):
        """Produce a string to be used when the object is printed"""
        return 'UptakeGrowthCell %d Type %d (%s)' % (self.id, self.type, self.types[self.type])

    def type(self):
        """Return the name of the type of this cell"""
        return self.types[self.type]

    def update(self, neighbors):
        """Update the cell based on a competition with a randomly-selected
        neighbor

        TODO: details

        Parameters:

        *neighbors*
            A list of neighboring cells

        """

        if self.type == self.EMPTY:
            pass

        elif self.type == self.LIVING:
            self.energy -= self.energy_cost

            if random.random() < self.death or self.energy <= 0:
                self.type = self.EMPTY
                self.topology.update_type_count(self.LIVING, self.EMPTY)
            elif random.random() < self.uptake_rate:
                # Get level of resource
                # Subtract max(level, uptake_amount) from resource
                # Add this amount of energy to org
                # TODO: uptake
                print "Node is",self.node
                reslevel = self.node['resource_manager'].get_level(self.resource)
                print "Level is",reslevel
            else:
                neighbor = None
                random.shuffle(neighbors)
                for n in neighbors:
                    if n.type == self.EMPTY:
                        neighbor = n

                if n == None:
                    neighbor = random.choice(neighbors)

                neighbor.type = self.type
                
                if random.random() < self.mutation:
                    neighbor.uptake_rate = random.normalvariate(self.update_rate, self.mutation_sigma)
                else:
                    neighbor.uptake_rate = self.uptake_rate

                donated_energy = self.energy * self.daughter_frac_energy
                self.energy -= donated_energy
                neighbor.energy = donated_energy

