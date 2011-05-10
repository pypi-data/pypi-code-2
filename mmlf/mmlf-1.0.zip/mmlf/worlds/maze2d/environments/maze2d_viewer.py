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


from collections import defaultdict

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mmlf.gui.viewers.viewer import Viewer
from mmlf.framework.observables import OBSERVABLES, TrajectoryObservable, \
                                 StateActionValuesObservable

class Maze2DDetailedViewer(Viewer):
    
    def __init__(self, maze, stateSpace, actions):        
        super(Maze2DDetailedViewer, self).__init__()
        
        self.maze = maze
        self.stateSpace = stateSpace
        self.actions = actions
        
        self.samples = defaultdict(lambda : 0)
        self.valueAccessFunction = None
                
        # Update frequency
        self.redrawFrequency = 1
        self.updateCounter = 0
               
        # Get required observables
        self.trajectoryObservable = \
                OBSERVABLES.getAllObservablesOfType(TrajectoryObservable)[0]
        self.stateActionValuesObservables = \
                OBSERVABLES.getAllObservablesOfType(StateActionValuesObservable)
    
        # Combo Box for selecting the observable
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(map(lambda x: "%s" % x.title, 
                                   self.stateActionValuesObservables))
        self.connect(self.comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), 
                     self._observableChanged)
        
        # Automatically update combobox when new float stream observables 
        #  are created during runtime
        def updateComboBox(observable, action):
            self.comboBox.clear()
            self.stateActionValuesObservables = \
                    OBSERVABLES.getAllObservablesOfType(StateActionValuesObservable)
            self.comboBox.addItems(map(lambda x: "%s" % x.title, 
                                       self.stateActionValuesObservables))
        OBSERVABLES.addObserver(updateComboBox)    
    
        # Create matplotlib widgets
        plotWidgetPolicy = QtGui.QWidget(self)
        plotWidgetPolicy.setMinimumSize(300, 400)
        plotWidgetPolicy.setWindowTitle ("Policy")
 
        self.figPolicy = Figure((3.0, 4.0), dpi=100)
        self.figPolicy.subplots_adjust(left=0.01, bottom=0.01, right=0.99, 
                                       top= 0.99, wspace=0.05, hspace=0.11)

        self.canvasPolicy = FigureCanvas(self.figPolicy)
        self.canvasPolicy.setParent(plotWidgetPolicy)
        
        ax = self.figPolicy.gca()
        ax.clear()
        self.maze.drawIntoAxis(ax)
        
        self.plotWidgetValueFunction = dict()
        self.figValueFunction = dict()
        self.canvasValueFunction = dict() 
        for index, action in enumerate(self.actions):
            self.plotWidgetValueFunction[action] = QtGui.QWidget(self)
            self.plotWidgetValueFunction[action].setMinimumSize(300, 400)
            self.plotWidgetValueFunction[action].setWindowTitle (str(action))
        
            self.figValueFunction[action] = Figure((3.0, 4.0), dpi=100)
            self.figValueFunction[action].subplots_adjust(left=0.01, bottom=0.01, 
                                                   right=0.99, top= 0.99,
                                                   wspace=0.05, hspace=0.11)
         
            self.canvasValueFunction[action] = FigureCanvas(self.figValueFunction[action])
            self.canvasValueFunction[action].setParent(self.plotWidgetValueFunction[action])
            
            ax = self.figValueFunction[action].gca()
            ax.clear()
            self.maze.drawIntoAxis(ax)
        
        self.textInstances = dict()
        self.arrowInstances = []
               
        self.canvasPolicy.draw()
        for index, action in enumerate(self.actions):
            self.canvasValueFunction[action].draw()
        
        self.mdiArea = QtGui.QMdiArea(self)
        self.mdiArea.addSubWindow(plotWidgetPolicy)
        for index, action in enumerate(self.actions):
            self.mdiArea.addSubWindow(self.plotWidgetValueFunction[action])
        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.mdiArea)
        self.vlayout.addWidget(self.comboBox)
        self.setLayout(self.vlayout)
        
        # Connect to observer (has to be the last thing!!)
        self.trajectoryObservableCallback = \
             lambda *transition: self.updateSamples(*transition)
        self.trajectoryObservable.addObserver(self.trajectoryObservableCallback)
        
        self.stateActionValuesObservableCallback = \
             lambda valueAccessFunction, actions: self.updateValues(valueAccessFunction, actions)
        if len(self.stateActionValuesObservables) > 0:
            # Show per default the first observable
            self.stateActionValuesObservable = self.stateActionValuesObservables[0] 
            
            self.stateActionValuesObservable.addObserver(self.stateActionValuesObservableCallback)
        else:
            self.stateActionValuesObservable = None
           
    
    def updateValues(self, valueAccessFunction, actions):
        self.valueAccessFunction = valueAccessFunction
        
        # Check if we have to redraw
        self.updateCounter += 1
        if self.updateCounter % self.redrawFrequency == 0: 
            self.redraw()
        
    def updateSamples(self, state, action, reward, succState, episodeTerminated):
        state = self.stateSpace.parseStateDict(state)
        self.samples[(state, action)] = self.samples[(state, action)] + 1
        
    def redraw(self):
        # Update policy visualization
        for arrow in self.arrowInstances:
            arrow.remove()
        self.arrowInstances = []
        states = set(state for state, action in self.samples.iterkeys())
        actions = set(action for state, action in self.samples.iterkeys())
        for state in states:
            maxValue, maxAction = max((self.valueAccessFunction(state, (action,)) 
                                            if self.valueAccessFunction is not None else 0.0,
                                       action) for action in actions)
            axis = self.figPolicy.gca()
            if isinstance(maxAction, tuple): # For TD-Agents that use crossproduct of action space
                self._plotArrow(axis, (state[0], -state[1]), maxAction[0])
            else:
                self._plotArrow(axis, (state[0], -state[1]), maxAction) 
        
        # Update Q-function visualization
        for (state, action) in self.samples.iterkeys():
            if (state, action) not in self.textInstances.keys():
                if isinstance(action, tuple): # For TD-Agents that use crossproduct of action space
                    axis = self.figValueFunction[action[0]].gca()
                else:
                    axis = self.figValueFunction[action].gca()
                textInstance = \
                    axis.text(state[0] - 0.3, -state[1],
                              "%.1f\n%s" % (self.valueAccessFunction(state, (action,)) 
                                                    if self.valueAccessFunction is not None else 0.0,
                                            self.samples[(state, action)]),
                              fontsize=8, fontweight = "bold")
                self.textInstances[(state, action)] = textInstance
            else:
                self.textInstances[(state, action)].set_text(
                             "%.1f\n%s" % (self.valueAccessFunction(state, (action,))
                                             if self.valueAccessFunction is not None else 0.0,
                             self.samples[(state, action)]))

        self.canvasPolicy.draw()
        for index, action in enumerate(self.actions):
            self.canvasValueFunction[action].draw()
            
    def _plotArrow(self, axis, center, direction):
        if isinstance(direction, tuple): # For TD agent with action crossproduct
            direction = direction[0]
        if direction == 'up':
            (dx, dy) = (0.0, 0.6)
        elif direction == 'down':
            (dx, dy) = (0.0, -0.6)
        elif direction == 'right':
            (dx, dy) = (0.6, 0.0)
        elif direction == 'left':
            (dx, dy) = (-0.6, 0.0)
            
        arr = axis.arrow(center[0] - dx/2, center[1] - dy/2, dx, dy,
                         width = 0.05, fc = 'k')
        self.arrowInstances.append(arr)   
        
    def _observableChanged(self, comboBoxIndex):
        if self.stateActionValuesObservable is not None:
            # Remove old observable
            self.stateActionValuesObservable.removeObserver(self.stateActionValuesObservableCallback)
        # Get new observable and add as listener
        self.stateActionValuesObservable = self.stateActionValuesObservables[comboBoxIndex]
        self.stateActionValuesObservable.addObserver(self.stateActionValuesObservableCallback)
