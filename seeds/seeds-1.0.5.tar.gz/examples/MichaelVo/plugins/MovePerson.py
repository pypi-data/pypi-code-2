# -*- coding: utf-8 -*-
"""
Moves museum visitors to new locations and prints them, and chooses what cell gets an energy boost
"""

__author__ = "Michael Vo <vomichae@msu.edu>"
__credits__ = "Brian Connelly"

import csv
import random

from seeds.Action import *

class Visitor(object):
    def __init__(self, world, location):
        self.world = world
        self.location = location

        self.pref_red = self.world.config.getint('Bion', 'red', 0)
        self.pref_green = self.world.config.getint('Bion', 'green', 0)
        self.pref_blue = self.world.config.getint('Bion', 'blue', 0)

        self.time_at_location = 0
        self.current_score = 9999999

        self.visited_sites = []

class MovePerson(Action):
    """ Write the x,y coordinates of each visitor and moves them
    Also gives fitness benefits to cells with high similarity to the color they seek
    Config file settings are in Bion
    """
    def __init__(self, world):
        """Initialize the MovePerson Action"""
        Action.__init__(self, world)
        self.top = self.world.topology_manager.topologies[0]
       	self.name = "MovePerson"

       	self.red = self.world.config.getint('Bion', 'red', 0)
       	self.green=self.world.config.getint('Bion', 'green', 0)
       	self.blue=self.world.config.getint('Bion', 'blue', 1)
       	self.num_people = self.world.config.getint('Bion', 'people', 1)
       	self.neighbor_visit_frac = self.world.config.getfloat('Bion', 'neighbor_visit_frac', 0.25)

        self.visitors = []
        for i in xrange(self.num_people):
            node = random.choice(self.top.graph.nodes())
            cell = self.top.graph.node[node]['cell']
            v = Visitor(world, cell)
            self.visitors.append(v)

    def update(self):
        filename = "%s-%06d.csv" % ("person", self.world.epoch)
        data_file = self.datafile_path(filename)
        self.writer = csv.writer(open(data_file, 'w'))
        self.writer.writerow(['#epoch', 'population', 'cell id','x','y','type'])
    	
    	"""
    	The code below finds the neighbor with the highest similarity to the target color, and gives it an energy boost.
    		
    	It also moves to a random neighbor, and writes to file
    	"""
    	for visitor in self.visitors:
            moved = False
            visitor.time_at_location += 1

            # Visit the current cell.
            visitor.location.visit(frac=1)

            neighbors = self.top.get_neighbors(visitor.location.node)
            for n in neighbors:
                visitor.location.visit(frac=self.neighbor_visit_frac)
                score = (visitor.pref_red - n.red)**2 + (visitor.pref_blue - n.blue)**2 + (visitor.pref_green - n.green)**2
                
                # Move to cell with closest color
                if score < visitor.current_score and n.id not in visitor.visited_sites:
                    current_score = score
                    visitor.location = n
                    visitor.current_score = score
                    visitor.visited_sites.append(n.id)
                    visitor.time_at_location = 0

            # If no movement has been made in N epochs, move to a random neighbor
            if not moved and visitor.time_at_location > 3:
                visitor.location = random.choice(neighbors)
                visitor.visited_sites.append(visitor.location.id)
                visitor.time_at_location = 0
                visitor.current_score = (visitor.pref_red - visitor.location.red)**2 + (visitor.pref_blue - visitor.location.blue)**2 + (visitor.pref_green - visitor.location.green)**2

            self.writer.writerow([self.world.epoch, self.top.id, visitor.location.id, visitor.location.coords[0], visitor.location.coords[1]])

