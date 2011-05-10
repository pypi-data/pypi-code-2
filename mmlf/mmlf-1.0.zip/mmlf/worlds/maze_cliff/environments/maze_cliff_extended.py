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

"""
module that implements a maze-environment with cliff support and a lot of optional configuration settings. 
"""

__author__ = "Fabian Maas genannt Bermpohl"
__copyright__ = "Copyright 2011, University Bremen, AG Robotics"
__credits__ = ['Jan Hendrik Metzen']
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Fabian Maas genannt Bermpohl"
__email__ = "fabian.maas@informatik.uni-bremen.de"

import random

from copy import deepcopy
import os

from mmlf.framework.spaces import StateSpace, ActionSpace
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.environments.single_agent_environment import SingleAgentEnvironment

class MazeCliffExtendedEnvironment(SingleAgentEnvironment):
    """ The extended two-dimensional maze cliff environment.

    This is an extended version of the two-dimensional maze cliff environment.
    The environment offers a wide range of configurability.
    Example Maze:
    **************
    *            *
    *            *
    *            *
    *SCCCCCCCCCCG*
    **************

    In this environment the agent has to find its way from the start position 'S'
    to the goal position 'G'. Thereby the agent must avoid the cliff regions 'C'.
    It should avoid collisions with walls '*'. The rewards the agent should receive
    on any time step and on running into the cliff region are configurable.
    The shape of the maze is also freely configurable via a configuration file. 
    The minimum configuration contains only a single line with a 'S' and a 'G'. You 
    may put '*' and 'C' as you like. All other characters will be ignored. Make sure
    that a path exists between start and goal position. Else the first episode will last
    infinitly long.
    The size of the maze will be determined by the longest row/column. If the actual size
    of the maze is not bounded by walls, this 'outer boundary' will also behave like walls. 

    **CONFIG DICT**
        :stepPenalty: : The reward the agent obtains on any time step, except when on a cliff
        :wallDeflection: : If set 'True', movement against a wall will no longer block but cause movement in the opposite direction
        :cliffPenalty: : The reward an agent obtains when stepping into the cliff area
        :cliffRestart: : If set 'True', the state of the environment will be reset to initialState when the agent steps into the cliff. The cliffPenalty will be given independently of this.
        :extendedActionSpace: : If set 'True', the agent may move to each of the 8-connected grid fields. The action space gets extended by 4 additional actions to perform diagonal moves.
        :stochasticity: : The stochasticity of the state transition matrix. With probability *stochasticity* the desired transition is made, otherwise a random transition 
        :mazeDescriptionString: : Name of the config file where the maze is defined. These files are located in folder 'worlds/maze_cliff'. 
    """
    
    DEFAULT_CONFIG_DICT = {"stepPenalty" : -1,
                           "wallDeflection" : False,
                           "cliffPenalty" : -100,
                           "cliffRestart" : True,
                           "extendedActionSpace" : False,
                           "stochasticity" : 0.0,
                           "mazeDescriptionString" : "'maze_default.cfg'"
                           }
    
    def __init__(self, *args, **kwargs):
        self.environmentInfo = EnvironmentInfo(versionNumber="0.3",
                                               environmentName="Maze Cliff Extended",
                                               discreteActionSpace=True,
                                               episodic=True,
                                               continuousStateSpace=False,
                                               continuousActionSpace=False,
                                               stochastic=False)
        super(MazeCliffExtendedEnvironment, self).__init__(*args, **kwargs)

        # initialize episode counter
        self.episodeCounter = 0
        
        # create the maze
        self.maze = Maze(self)
        
        # define state space
        oldStyleStateSpace = {
            "row": ("discrete", range(self.maze.Rows())),
            "col": ("discrete", range(self.maze.Cols()))
            }
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace, limitType="soft")

        # set initial state
        self.initialState = {
            "row": self.maze.getStartPosition()[0],
            "col": self.maze.getStartPosition()[1],
            }
        
        # define action space
        if self.configDict["extendedActionSpace"]:
            oldStyleActionSpace =  { "action": ("discrete", ["n", "nw", "w", "sw", "s", "se", "e", "ne"]) }
        else:
            oldStyleActionSpace =  { "action": ("discrete", ["north", "west", "south", "east"]) }
        self.actionSpace = ActionSpace()
        self.actionSpace.addOldStyleSpace(oldStyleActionSpace, limitType="soft")
        self.actions = [action[0] for action in self.actionSpace.getActionList()]
        
        # prepare episode
        self.stochasticity = self.configDict["stochasticity"]
        self._reinitialize()

    ########################## Interface Functions #####################################
    def getInitialState(self):
        """
        Returns the initial state of the simulation
        """
        return self._createStateForAgent(self.initialState)
    
    def getStateSpace(self):
        """
        Returns the state space of this simulation.
        """
        return self.stateSpace
    
    def getActionSpace(self):
        """
        Return the action space of this simulation.
        """
        return self.actionSpace
    
    def evaluateAction(self, actionObject):
        """ Execute an agent's action in the environment.
        
        Take an actionObject containing the action of an agent, and evaluate 
        this action, calculating the next state, and the reward the agent 
        should receive for having taken this action.
        
        Additionally, decide whether the episode should continue,
        or end after the reward has been  issued to the agent.
        
        This method returns a dictionary with the following keys:
           :rewardValue: : An integer or float representing the agent's reward.
                           If rewardValue == None, then no reward is given to the agent.
           :startNewEpisode: : True if the agent's action has caused an episode
                               to get finished.
           :nextState: : A State object which contains the state the environment
                         takes on after executing the action. This might be the
                         initial state of the next episode if a new episode
                         has just started (startNewEpisode == True)
           :terminalState: : A State object which contains the terminal state 
                             of the environment in the last episode if a new 
                             episode has just started (startNewEpisode == True). 
                             Otherwise None.        
        """
        # increment step count
        self.stepCounter += 1

        # append action to action trace
        action = actionObject['action']
        self.actionTrace.append(action)

        # evaluate action
        newState, reward = self._evaluateAction(action)
        self.currentState = newState
        self.totalReward += reward
     
        # check if episode ends with this transition
        if not self._checkTermination():
            terminalState = None
        else: 
            terminalState = self.currentState

            # prepare next episode
            self._terminateEpisode()
            self._reinitialize()

            # increment episode counter
            self.episodeCounter += 1
            
        resultsDict = {"reward" : reward,
                       "terminalState" : terminalState,
                       "nextState" : self._createStateForAgent(self.currentState),
                       "startNewEpisode" : terminalState != None}
        return resultsDict

    def _terminateEpisode(self):
        # some logging
        self.environmentLog.info("Episode %s lasted for %s steps; acc. reward: %s."
                                 % (self.episodeCounter, self.stepCounter, self.totalReward))
        if len(self.actionTrace) < 20: 
            actionTrace = self.actionTrace
        else:
            actionTrace = ["..."] + self.actionTrace[-20:]
        self.environmentLog.info("Action Trace is %s" % actionTrace)
        
        # update observables
        self.episodeLengthObservable.addValue(self.episodeCounter, self.stepCounter)
        self.returnObservable.addValue(self.episodeCounter, self.totalReward)

    def _reinitialize(self):
        self.stepCounter = 0
        self.totalReward = 0.0
        self.actionTrace = []
        self.currentState = deepcopy(self.initialState)
    
    def _evaluateAction(self, action):
        """Execute the action and see what's happening

        In stochastic environments, the chosen action is only executed
        with probability 1 - self.stochasticity. 
        Otherwise a random action will be executed"""

        if random.random() < self.stochasticity:
            action = random.choice(self.actions)

        currentPos = (self.currentState['row'], self.currentState['col'])
        nextPos, reward = self.maze.evaluateAction(currentPos, action)
        nextState = dict()
        nextState['row'] = nextPos[0]
        nextState['col'] = nextPos[1]
                
        return (nextState, reward)
        
    def _checkTermination(self):
        """Checks if the agent has reached the goal state"""
        currentPos = (self.currentState['row'], self.currentState['col'])

        return self.maze.isGoalState(currentPos)
    
    def _createStateForAgent(self, state):
        """eventually implement noisy observations"""
        return state

class Maze(object):
    """ A class which represents a two-dimensional maze with a cliff """
    def __init__(self, parent):

        self.parent = parent
        self.stepPenalty = self.parent.configDict["stepPenalty"]
        self.wallDeflection = self.parent.configDict["wallDeflection"]
        self.cliffPenalty = self.parent.configDict["cliffPenalty"]
        self.cliffRestart = self.parent.configDict["cliffRestart"]

        mazeString = self.parent.configDict['mazeDescriptionString']

        maze = self._loadMaze(mazeString)
        if maze == []:
            raise ValueError("Invalid maze string filename or empty config file")

        self._analyzeMaze(maze)

    def _loadMaze(self, mazeString):
        # build up absolute filename
        filename = os.path.dirname(os.path.abspath(__file__)) + os.sep + os.pardir + os.sep + mazeString

        maze = []
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                maze = [line for line in f]

        return maze

    def _analyzeMaze(self, maze):

        # determine occupied fields
        walls = []
        cliff = []
        self.start = None
        self.goal = None
        for row,line in enumerate(maze):
            for col,val in enumerate(line):
                if val == '*':
                    walls.append((row,col))
                elif val == 'C':
                    cliff.append((row,col))
                elif val == 'G':
                    self.goal = (row,col)
                elif val == 'S':
                    self.start = (row,col)
                # all other characters will be ignored
        # make sure we have at least a start and a goal
        assert self.start != None and "invalid maze description!"
        assert self.goal != None and "invalid maze description!"

        # determine height and width, by finding the max occupied field along the axes
        # thus allowing open walls, without enabling the agent to escape
        rows = []
        cols = []
        rows.append( self.start[0] )
        rows.append( self.goal[0] )
        if cliff != []:
            rows.append( max(cliff, key=lambda tuple: tuple[0])[0] )
        if walls != []:
            rows.append( max(walls, key=lambda tuple: tuple[0])[0] )
        self.rows = max( rows ) + 1

        cols.append( self.start[1] )
        cols.append( self.goal[1] )
        if cliff != []:
            cols.append( max(cliff, key=lambda tuple: tuple[1])[1] )
        if walls != []:
            cols.append( max(walls, key=lambda tuple: tuple[1])[1] )
        self.cols = max( cols ) + 1
        
        self.walls = set(walls)
        self.cliff = set(cliff)

    def evaluateAction(self, pos, action):
        """
        The method executes a forward movement starting from the given pos
        in the given direction. If no wall is blocking the movement, the new position
        is returned, otherwise the old position.
        """

        if self.wallDeflection:
            print "warning! wall deflection is currently not implemented!"
   
        # determine position update along row axis
        newPos = pos
        if action == 'n' or action == 'nw' or action == 'ne' or action == 'north':
            newPos = (newPos[0]-1, newPos[1])
        elif action == 's' or action == 'sw' or action == 'se' or action == 'south':
            newPos = (newPos[0]+1, newPos[1])
        # test wall collision and world border collision
        if newPos in self.walls or newPos[0] not in range(self.rows):
            newPos = pos

        # determine position update along col axis
        tmp = newPos
        if action == 'e' or action == 'ne' or action == 'se' or action == 'east':
            newPos = (newPos[0], newPos[1]+1)
        elif action == 'w' or action == 'nw' or action == 'sw' or action == 'west':
            newPos = (newPos[0], newPos[1]-1)
        # test wall collision and world border collision
        if newPos in self.walls or newPos[1] not in range(self.cols):
            newPos = tmp

        # test cliff collision
        if newPos in self.cliff:
            if self.cliffRestart:
                return self.start, self.cliffPenalty
            else:
                return newPos, self.cliffPenalty
        else:
            return newPos, self.stepPenalty

    
    def Cols(self):
        "Returns the number of columns of the maze"
        return self.cols
        
    def Rows(self):
        "Returns the number of rows of the maze"
        return self.rows
    
    def getStartPosition(self):
        "Returns the start position of the maze"
        return self.start
        
    def isGoalState(self, pos):
        "Checks if the given position is the goal position"
        return pos == self.goal
        
   
EnvironmentClass = MazeCliffExtendedEnvironment
EnvironmentName = "Maze Cliff Extended"
