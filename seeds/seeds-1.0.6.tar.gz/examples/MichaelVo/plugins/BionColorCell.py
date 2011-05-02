# -*- coding: utf-8 -*-
""" Cell type representing the cells in Bion with RBG values
"""

__author__ = "Michael Vo <vomichae@msu.edu>"
__credits__ = "Brian Connelly"

from seeds.cell.Cell import *
import random

class BionColorCell(Cell):
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
        
        """ dummy cell type"""
        if type == -1:
        	self.type = 1
        else:
            self.type = 1
            
        """ random rgb value """
        self.red = random.randint(0,255)   
        self.green = random.randint(0,255)
        self.blue = random.randint(0,255)
        
        self.topology.increment_type_count(self.type)
        
        """ Read in parameters """
        self.mutation_rate = self.world.config.getfloat('Bion', 'mutation_rate', .05)
        self.visit_bonus = self.world.config.getfloat('Bion', 'visit_bonus', 4)
        self.update_energy = self.world.config.getfloat('Bion', 'update_energy', .0625)
        self.child_gift = self.world.config.getfloat('Bion', 'child_gift', 0)
        
        self.public_good_cost = self.world.config.getfloat('Bion', 'public_good_cost', .5)
        self.public_good_benefit = self.world.config.getfloat('Bion', 'public_good_benefit', 3)
        self.public_good_threshold = self.world.config.getfloat('Bion', 'public_good_threshold', 5)
        
        """ default public gene to false """
        self.public_good_gene=False
        	
    def __str__(self):
        """Produce a string to be used when the object is printed"""
        return 'RPCell %d Red %d Green %d Blue %d' % (self.id, self.red, self.green, self.blue)

    def type(self):
        """Return the name of the type of this cell"""
        return 'Red %d Green %d Blue %d' % (self.red, self.green, self.blue)

    def update(self, neighbors):
        """Update the cell by creating public good and reproducing

        Parameters:

        *neighbors*
            A list of neighboring cells

        """
        
        """ give cell update energy """
        self.energy_level+=self.update_energy
        
        """ if this cell is cooperator, produce public good at cost """
        if self.public_good_gene==True:
        	self.energy_level-=self.update_energy*self.public_good_cost
        	self.public_good_level+=1
        
        """ find total public good in vicinity, if greater than threshold give benefit """
        
        total_public_good = self.public_good_level
        for n in neighbors:
        	total_public_good+=n.public_good_level
        
        if(total_public_good>=self.public_good_threshold):
        	self.energy_level+=self.update_energy*self.public_good_benefit
        	
        # Pick a random neighbor to reproduce into if it comes down to it
        child = random.choice(neighbors)
        
        
        
        if self.energy_level>=1:
        	
        	# Possible modification of colors is mutation rate times 255
        	range = int(self.mutation_rate*255)
        	
        	# modify colors with mutation (not quite accurate for polygenic
        	# since it should be mut. rate for each of 255 genes. fix later)
        	child.blue = self.blue+random.randint(-range,range)
        	child.red = self.red+random.randint(-range,range)
        	child.green = self.green+random.randint(-range,range)
        	
        	# if there's a gift for new children, give it here
        	child.energy_level = self.energy_level*self.child_gift
        	
        	# public good level remains the same... still left in cell
        	child.public_good_level = child.public_good_level
        	
        	# see if we change the public good gene
        	if random.randrange(0,1000)>self.mutation_rate*1000:
        		child.public_good_gene = self.public_good_gene
        	else:
        		child.public_good_gene = not self.public_good_gene
        		
        	self.energy_level-=1
        
        # if public good level is greater than 0, subtract from it
        if self.public_good_level>0:
        	self.public_good_level-=.5
    
    def visit(self):
    	self.energy_level+=self.visit_bonus
