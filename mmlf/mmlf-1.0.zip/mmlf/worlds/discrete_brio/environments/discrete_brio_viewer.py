# Maja Machine Learning Framework
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


__author__ = "Alexander Boettcher"
__copyright__ = "Copyright 2011, University Bremen, AG Robotics"
__credits__ = ["Jan Hendrik Metzen", 'Mark Edgington']
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Jan Hendrik Metzen"
__email__ = "jhm@informatik.uni-bremen.de"

from collections import defaultdict

import numpy
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import patches

from mmlf.gui.viewers.viewer import Viewer
from mmlf.framework.observables import OBSERVABLES, TrajectoryObservable

class DiscreteBrioViewer(Viewer):

    def __init__(self, mazeDescriptionString):
        super(DiscreteBrioViewer, self).__init__()
        
        self.actions = None
        
        # Update frequency
        self.redrawFrequency = 100
        self.updateCounter = 0
        
        # Parse maze structure      
        self.mazeStructure = []
        for row in map(lambda s: s.strip(), mazeDescriptionString.split('\n')):
            if row == '': continue
            self.mazeStructure.append(list(row))
        self.mazeDimensions=(len(self.mazeStructure),len(self.mazeStructure[0]))
        
        self.gridCells = {}
        self.gridCellVisits = defaultdict(int)
        self.currentPositionPatch = None
        
        # Get required observables
        self.trajectoryObservable = OBSERVABLES.getAllObservablesOfType(TrajectoryObservable)[0]
        
        # Create matplotlib widgets
        self.mazeSubplot = None
        plotWidgetVisitedCells = QtGui.QWidget(self)
        plotWidgetVisitedCells.setMinimumSize(300, 400)
        plotWidgetVisitedCells.setWindowTitle ("Visited Cells")
 
        self.figVisitedCells = Figure((3.0, 4.0), dpi=100, facecolor='white')
        self.figVisitedCells.subplots_adjust(left=0.01, bottom=0.01, right=0.99, 
                                             top= 0.99, wspace=0.05, hspace=0.11)
        self.axisVisitedCells = self.figVisitedCells.gca()
        self.canvasVisitedCells = FigureCanvas(self.figVisitedCells)
        self.canvasVisitedCells.setParent(plotWidgetVisitedCells)
        
        self.canvasVisitedCells.draw()
        
        # Connect to observer (has to be the last thing!!)
        self.trajectoryObservableCallback = \
             lambda *transition: self.updateCurrentState(*transition)
        self.trajectoryObservable.addObserver(self.trajectoryObservableCallback)


    def updateCurrentState(self, state, action, reward, succState, 
                           episodeTerminated):
        self.currentCoordinates = (succState['column'], succState['row'])
        self.gridCellVisits[self.currentCoordinates] += 1
        
        self.updateCounter += 1
        if self.updateCounter % self.redrawFrequency == 0: 
            self.redraw()
        

    def redraw(self):
        self._drawMaze(len(self.mazeStructure[0]),len(self.mazeStructure))
            
        # normalizing to the range [0,1] to draw grey values in the respective color
        maxVisits = max(self.gridCellVisits.values())
        normalized=[(el, visits / float(maxVisits)) 
                            for el, visits in self.gridCellVisits.iteritems()]
                
        for element in normalized:
            if self.gridCells.has_key(element[0]) == True:
                cellSquare=self.gridCells[element[0]]
                cellSquare.set_facecolor(str(1-element[1]))
            else:
                cellSquare = patches.Rectangle((element[0][0],
                                                abs(element[0][1]-self.mazeDimensions[1])-1),
                                                1,1,fill=True,facecolor=str(1-element[1]))
                self.gridCells[element[0]]=cellSquare
        
        self.canvasVisitedCells.draw()
        
    def _drawMaze(self, xd, yd):
        if self.mazeSubplot == None:
            # Crate base maze
            self.mazeSubplot = self.figVisitedCells.add_subplot(111)
            
            pp=self._getGridPatch(xd, yd)
            self.mazeSubplot.add_patch(pp)
            objects=self._getMazeObjectPatches(self.mazeStructure)
            for object in objects:
                self.mazeSubplot.add_patch(object)
                
            self.mazeSubplot.set_axis_off()
            self.mazeSubplot.set_xlim((1.0, xd-1))
            self.mazeSubplot.set_ylim((1.0, yd-1))
        
        # add patches for visit numbers
        for cellSquare in self.gridCells.values():
            self.mazeSubplot.add_patch(cellSquare)
        
        # Add current position patch and remove old one
        if self.currentPositionPatch is not None:
            self.mazeSubplot.patches.remove(self.currentPositionPatch)
            
        self.currentPositionPatch = \
                patches.Circle((self.currentCoordinates[0] + 0.5,
                                abs(self.currentCoordinates[1] - self.mazeDimensions[1]) - 1 + 0.5),
                                0.5, fill=True, facecolor="black")
        self.mazeSubplot.add_patch(self.currentPositionPatch)        
        

    def _getGridPatch(self, xd,yd):
        vertices=[]
        code=[]
        
        for x in range(xd+1):
            vertices.append((x,0))
            code.append(patches.Path.MOVETO)
            vertices.append((x,yd))
            code.append(patches.Path.LINETO)

        for y in range(yd+1):
            vertices.append((0,y))
            code.append(patches.Path.MOVETO)
            vertices.append((xd,y))
            code.append(patches.Path.LINETO)

        p=patches.Path(vertices,code)
        pp=patches.PathPatch(p)
        pp.set_edgecolor("red")
        return(pp)

    def _getMazeObjectPatches(self, structure):
        objects=[]
        x = 0
        y = 0
        for row in structure:
            x=0
            for col in row:
                if col=="*":
                    wall=patches.Rectangle((x,abs(y-self.mazeDimensions[1])-1),
                                           1,1,fill=True,facecolor="cyan")
                    objects.append(wall)
                if col=="S":
                    start=patches.Rectangle((x,abs(y-self.mazeDimensions[1])-1),
                                                       1,
                                                       1,
                                                       fill=False,
                                                       linewidth=3.0,
                                                       edgecolor="green")
                    objects.append(start)
                if col=="G":
                    goal=patches.Rectangle((x,abs(y-self.mazeDimensions[1])-1),
                                                      1,
                                                      1,
                                                      fill=False,
                                                      linewidth=3.0,
                                                      edgecolor="blue")
                    objects.append(goal)
                if ord(col) <= ord('z') and ord(col) >= ord('a'):
                    hole=patches.Circle((x+0.5,abs(y-self.mazeDimensions[1])-1+0.5),
                                        0.5,fill=True,facecolor="grey")
                    objects.append(hole)
                x+=1
            y+=1
            
        return objects
