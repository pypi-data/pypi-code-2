# -*- coding: utf-8 -*-
""" Cell type representing the cells in Bion with RBG values
"""

__author__ = "Michael Vo <vomichae@msu.edu>"
__credits__ = "Brian Connelly"

from seeds.cell.Cell import *
import random

class BionColorCellBC(Cell):
    """
    This is a simple Cell type with RBG values and simple cooperation.

    Configuration: There are no parameters configurable for this Cell type.


	red, green, and blue are rbg values from 0 to 255
	energy is needed to reproduce
	public good is produced each update if the cell has gene for it turned on
	"""
	
    red = 0
    green = 0
    blue = 0
    
    energy_level = 0
    public_good_level = 0
    public_good_gene = False

    def __init__(self, world, topology, node, id, type=-1):
        """Initialize a RPSCell object

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
        self.type = 1
            
        """ random rgb value """
        self.red = random.randint(0,255)   
        self.green = random.randint(0,255)
        self.blue = random.randint(0,255)
        
        self.topology.increment_type_count(self.type)
        
        """ Read in parameters """
        self.mutation_rate = self.world.config.getfloat('Bion', 'mutation_rate', .005)
        self.mutation_sigma = self.world.config.getfloat('Bion', 'mutation_sigma', 0.05)

        self.visit_bonus = self.world.config.getfloat('Bion', 'visit_bonus', 4)
        self.update_energy = self.world.config.getfloat('Bion', 'update_energy', .0625)
        self.child_gift = self.world.config.getfloat('Bion', 'child_gift', 0)
        
        self.public_good_cost = self.world.config.getfloat('Bion', 'public_good_cost', .5)
        self.public_good_benefit = self.world.config.getfloat('Bion', 'public_good_benefit', 3)
        self.public_good_threshold = self.world.config.getfloat('Bion', 'public_good_threshold', 5)
        self.public_good_loss = self.world.config.getfloat('Bion', 'public_good_loss', 0.01)
        
        """ default public gene to false """
        self.public_good_gene=False
        	
    def __str__(self):
        """Produce a string to be used when the object is printed"""
        return 'BionColorCellBC %d Red %d Green %d Blue %d' % (self.id, self.red, self.green, self.blue)

    def type(self):
        """Return the name of the type of this cell"""
        return self.type
        return 'Red %d Green %d Blue %d' % (self.red, self.green, self.blue)

    def update(self, neighbors):
        """Update the cell by creating public good and reproducing

        Parameters:

        *neighbors*
            A list of neighboring cells

        """

        """ find total public good in vicinity, if greater than threshold give benefit """
        total_public_good = self.public_good_level
        for n in neighbors:
        	total_public_good += n.public_good_level
        
        """ give cell update energy """
        if total_public_good >= self.public_good_threshold:
        	self.energy_level += self.update_energy*self.public_good_benefit
        else:
            self.energy_level += self.update_energy
        
        """ if this cell is cooperator, produce public good at cost """
        if self.public_good_gene:
        	self.energy_level -= self.update_energy*self.public_good_cost
        	self.public_good_level += 1
        
        # Reproduce if energy is sufficient
        if self.energy_level >= 1:
            child = random.choice(neighbors)

            # Mutate red, green, and blue alleles independently
            if random.random() < self.mutation_rate:
                child.red = int(round(random.normalvariate(self.red, self.mutation_sigma)))
            if random.random() < self.mutation_rate:
                child.green = int(round(random.normalvariate(self.green, self.mutation_sigma)))
            if random.random() < self.mutation_rate:
                child.blue = int(round(random.normalvariate(self.blue, self.mutation_sigma)))

            # Mutate the public good gene
            if random.random() < self.mutation_rate:
                child.public_good_gene = not self.public_good_gene

            # Donate some energy to the child.  remove from self.
            donation = self.energy_level * self.child_gift
            child.energy_level = donation
            self.energy_level -= donation
        	
            # Deduct energy used to reproduce
            self.energy_level-=1
        
        # Remove some of the public good
        self.public_good_level -= self.public_good_loss
    
    def visit(self, frac=1):
    	self.energy_level += (self.visit_bonus * frac)

