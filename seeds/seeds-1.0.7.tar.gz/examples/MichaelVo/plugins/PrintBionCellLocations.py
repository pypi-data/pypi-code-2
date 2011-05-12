# -*- coding: utf-8 -*-
"""
Print the coordinates of each bion cell
Note this uses the same configs as PrintCellLocations
"""

__author__ = "Michael Vo <vomichae@msu.edu>"
__credits__ = "Brian Connelly"

import csv

from seeds.Action import *

class PrintBionCellLocations(Action):
    """ Write the x,y coordinates of each cell and its color and cooperation status

    """
    def __init__(self, world):
        """Initialize the PrintBion CellLocations Action"""
        Action.__init__(self, world)

        self.epoch_start = self.world.config.getint('PrintCellLocations', 'epoch_start', 0)
        self.epoch_end = self.world.config.getint('PrintCellLocations', 'epoch_end',
                                                  default=self.world.config.getint('Experiment', 'epochs', default=-1))
        self.frequency = self.world.config.getint('PrintCellLocations', 'frequency', 1)
        self.filename = self.world.config.get('PrintCellLocations', 'filename', 'cell_locations')
        self.name = "PrintBionCellLocations"

    def update(self):
        """Execute the Action"""
        if self.skip_update():
	        return

        filename = "%s-%06d.csv" % (self.filename, self.world.epoch)
        data_file = self.datafile_path(filename)
        self.writer = csv.writer(open(data_file, 'w'))

        self.writer.writerow(['#epoch','population','cell id','x','y','type'])

        for top in self.world.topology_manager.topologies:
            for n in top.graph.nodes():
                cell = top.graph.node[n]['cell']
                row = [self.world.epoch, top.id, cell.id, cell.coords[0], cell.coords[1], cell.red, cell.green, cell.blue, cell.public_good_gene, cell.public_good_level]
                self.writer.writerow(row)

