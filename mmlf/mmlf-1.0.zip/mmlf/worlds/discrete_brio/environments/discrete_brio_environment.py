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

""" The discrete BRIO labyrinth.

This module contains an implementation of the discrete BRIO labyrinth dynamics
which can be used in a world of the MMLF.
"""

__author__ = "Alexander Boettcher"
__copyright__ = "Copyright 2011, University Bremen, AG Robotics"
__credits__ = ["Jan Hendrik Metzen", 'Mark Edgington']
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Jan Hendrik Metzen"
__email__ = "jhm@informatik.uni-bremen.de"

import numpy
import random
from copy import deepcopy

from mmlf.framework.protocol import EnvironmentInfo
from mmlf.framework.spaces import StateSpace, ActionSpace
from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.observables import FloatStreamObservable

class DiscreteBrioEnvironment(SingleAgentEnvironment):
    """ The discrete BRIO labyrinth.
    
    .. versionadded:: 0.9.9
    
    **CONFIG DICT**
        :maxDeflection: : Maximal value for the board's deflection (and also for the velocities) in each direction
        :holePenalty: : The reward an agent obtains when falling into a hole
        :goalReward: : The reward an agent obtains for reaching the goal
        :transitionProbability: : With probability 1-transitionProbability, the transition does not go to the "deterministic" successor state but to a randomly selected neighbor state
        :mazeIdentifier: : A string identifying the maze to be used. Currently available: "testSmall", "testMedium", "brio", "multipleWays", "emptyMaze", "cliff", "cliffLike" 
    
    """          
    DEFAULT_CONFIG_DICT = {"maxDeflection" : 1,
                           "holePenalty" : -10,
                           "goalReward" : 50.0,
                           "transitionProbability" : 1.0,
                           "mazeIdentifier": "'testSmall'",}
    
    def __init__(self, useGUI, *args, **kwargs):
        
        self.environmentInfo = EnvironmentInfo(versionNumber="0.3",
                                               environmentName="DiscreteBrio",
                                               discreteActionSpace=True,
                                               episodic=True,
                                               continuousStateSpace=False,
                                               continuousActionSpace=False,
                                               stochastic=False)

        super(DiscreteBrioEnvironment, self).__init__(useGUI=useGUI, *args, **kwargs)
        
        # A string which describes the structure of the maze.
        # A * indicates a wall, a lower case letter is a hole,
        # an S the start position of the agent and a G the
        # goal position. A blank indicates a free cell.
        mazeDescriptionString = {}
        mazeDescriptionString['testSmall'] =  """*****
                                                 *S b*
                                                 ** **
                                                 *a G*
                                                 *****
        """
        mazeDescriptionString['testMedium'] =  """*********
                                                  *S c*   *
                                                  ** *  *G*
                                                  *b   a  *
                                                  *********
        """

        mazeDescriptionString['brio'] =  """************
                                            *n  S*  f  *
                                            ** m*      *
                                            *   * **e  *
                                            *l* * d    *
                                            *k  *  * *c*
                                            *  j*e *   *
                                            *i  *f *b  *
                                            *  ***  *a *
                                            * h   g  * *
                                            *   *   *G *
                                            ************
        """
        mazeDescriptionString['multipleWays'] =  """************
                                                    *S *   *   *
                                                    *    *   * *
                                                    * ******** *
                                                    *  *   *   *
                                                    *    *   * *
                                                    * ******** *
                                                    *  *   *   *
                                                    *    *   * *
                                                    *  ******* *
                                                    *         G*
                                                    ************
        """
        mazeDescriptionString['emptyMaze'] =  """************
                                                 *S         *
                                                 *          *
                                                 *          *
                                                 *          *
                                                 *          *
                                                 *          *
                                                 *          *
                                                 *          *
                                                 *          *
                                                 *         G*
                                                 ************
        """
        mazeDescriptionString['cliffLike'] =  """************
                                                 *S  nmlkjih*
                                                 * *       g*
                                                 * *onmlkf f*
                                                 * ******e e*
                                                 *      *d d*
                                                 ****** *c c*
                                                 *      *b b*
                                                 * ******a a*
                                                 * *   ***  *
                                                 *   *     G*
                                                 ************
        """
        mazeDescriptionString['cliff'] =  """************
                                             *S         *
                                             *h         *
                                             *g         *
                                             *f         *
                                             *e         *
                                             *d         *
                                             *c         *
                                             *b         *
                                             *a         *
                                             *G         *
                                             ************
        """

        # Check the maze description identifier
        if(self.configDict.has_key('mazeIdentifier') == False or
           mazeDescriptionString.has_key(self.configDict['mazeIdentifier']) == False):
            print "error: spezify an existing maze"
            exit(1)

        #The maze object is created from the description
        self.maze = Maze.createMazeFromString(
            mazeDescriptionString[self.configDict['mazeIdentifier']])

        #The state space of the Discrete Brio Simulation
        oldStyleStateSpace =   {
            "column": ("discrete", range(self.maze.getColumns())),
            "row": ("discrete", range(self.maze.getRows())),
            "velocityX": ("discrete", range(
                    -self.configDict["maxDeflection"],
                    self.configDict["maxDeflection"]+1)),
            "velocityY": ("discrete", range(
                    -self.configDict["maxDeflection"],
                    self.configDict["maxDeflection"]+1)),
            "angleX": ("discrete", range(-self.configDict["maxDeflection"],
                                          self.configDict["maxDeflection"]+1)),
            "angleY": ("discrete", range(-self.configDict["maxDeflection"],
                                          self.configDict["maxDeflection"]+1))
            }
        
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace, limitType="soft")
        
        #The action space of the Discrete Brio Simulation
        oldStyleActionSpace =  {
            "angleXChange" : ("discrete", [-1,0,1]),
            "angleYChange" : ("discrete", [-1,0,1])
            }
        
        self.actionSpace = ActionSpace()
        self.actionSpace.addOldStyleSpace(oldStyleActionSpace, limitType="soft")
        
        #The current state of the simulation
        self.initialState =  { 
            "column": self.maze.getStartPosition()[0],
            "row": self.maze.getStartPosition()[1],
            "angleX": 0,
            "angleY": 0,
            "velocityX": 0,
            "velocityY": 0
            }
        #The current state is initially set to the initial state
        self.currentState = deepcopy(self.initialState)
        
        # A counter which stores the number of steps which
        # have been perfomed in this episode
        self.episodeStepCounter = 0

        # A counter which stores the number of steps which
        # have been perfomed in this run
        self.runStepCounter = 0

        # A counter which stores the number of episodes which
        # have been perfomed in this run
        self.episodeCounter = 0
        
        # The reward obtained in during the episode
        self.episodeReward = 0

        # The accumulated Reward is needed for logging. Accumulated reward
        # is a logging alternative to episode length which is not apropriate
        # since the ball can end up in a hole.
        self.accumulatedReward = 0

        # A boolean attribute, which is set when the ball fell
        # into a hole to give bad reward and to end the episode
        self.ballInHole = False
        
        # This variable logs the grid cell visits of the agent to visualize them
        self.gridCellVisits = {}

        # Create an observable for the episodes' return and one for the episode 
        # length
        self.maxHoleObservable = \
            FloatStreamObservable(title='%s Max Hole' % self.__class__.__name__,
                                  time_dimension_name='Episode',
                                  value_name='Episode Max Hole')
        self.accumulatedRewardObservable = \
            FloatStreamObservable(title='%s Accumulated Reward' % self.__class__.__name__,
                                  time_dimension_name='Step',
                                  value_name='Episode Accumulated Reward')
        
        if useGUI:
            # Add a viewer for the maze world
            from mmlf.gui.viewers import VIEWERS
            from mmlf.gui.viewers.trajectory_viewer import TrajectoryViewer
            from mmlf.worlds.discrete_brio.environments.discrete_brio_viewer import DiscreteBrioViewer
            VIEWERS.addViewer(lambda : DiscreteBrioViewer(mazeDescriptionString[self.configDict['mazeIdentifier']]),
                              'DiscreteBrioViewer')
            
            # Add general trajectory viewer
            VIEWERS.addViewer(lambda : TrajectoryViewer(self.stateSpace), 
                              'TrajectoryViewer')
        
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
        # The state before executing the action
        previousState = self.currentState
        
        angleXChange = actionObject['angleXChange']
        angleYChange = actionObject['angleYChange']

        # Update the gridCellVisits
        currentCoordinates=(self.currentState['column'],self.currentState['row'])
        if self.gridCellVisits.has_key(currentCoordinates)==False:
            self.gridCellVisits[currentCoordinates]=1
        else:
            self.gridCellVisits[currentCoordinates]+=1

        # Execute the action which was chosen by the agent
        self._stateTransition(angleXChange, angleYChange)
        
        # Check if the episode is finished (i.e. the goal is reached)
        episodeFinished = self._checkEpisodeFinished()

        terminalState = self.currentState if episodeFinished else None

        # Calculate Reward:
        if self.ballInHole == True:
            if self.configDict["holePenalty"] == "automatic":
                reward = -1* self.maze.getRows()*self.maze.getColumns()
            else:
                reward = self.configDict["holePenalty"]
        else:
            reward = -1
        if episodeFinished and self.ballInHole == False:
            reward = self.configDict["goalReward"]
        self.accumulatedReward += reward
        self.episodeReward += reward

        if episodeFinished:
            self.episodeLengthObservable.addValue(self.episodeCounter,
                                                  (self.episodeStepCounter+1))
            self.returnObservable.addValue(self.episodeCounter,
                                           self.episodeReward)
            
            holeNumber = -self.maze.structure[self.currentState['column']][self.currentState['row']]
            self.maxHoleObservable.addValue(self.episodeCounter, holeNumber)
            self.environmentLog.debug("Discrete Brio: run: %3d steps: %6d "
                                      "step in episode: %4d hole: %2d acc.reward: %7d" 
                                        % (self.episodeCounter + 1,
                                           self.runStepCounter + 1, 
                                           self.episodeStepCounter + 1,
                                           holeNumber,
                                           self.accumulatedReward))
            #Reset the simulation to the initial state (always the same)
            self.episodeStepCounter = 0
            self.currentState = deepcopy(self.initialState)
            self.ballInHole = False
            self.episodeReward = 0
            self.episodeCounter += 1
        else:
            self.episodeStepCounter += 1
        self.runStepCounter += 1
        if self.runStepCounter%100 == 0:
            self.accumulatedRewardObservable.addValue(self.runStepCounter,
                                                      self.accumulatedReward)

        self.trajectoryObservable.addTransition(previousState, actionObject, 
                                                reward, self.currentState, 
                                                episodeTerminated=episodeFinished)
        
        resultsDict = {"reward" : reward,
                       "terminalState" : terminalState,                       
                       "nextState" : self._createStateForAgent(self.currentState),
                       "startNewEpisode" : episodeFinished
                       }
        return resultsDict


    def _stateTransition(self, angleXChange, angleYChange):
        "Execute the specified action and store the resulting state"
        # get the current position
        currentPos = (self.currentState['column'],self.currentState['row'])
        currentVel = (self.currentState['velocityX'],self.currentState['velocityY'])
        # set the new angle postitions
        self.currentState['angleX'] = self.currentState['angleX'] + angleXChange
        if abs(self.currentState['angleX']) > self.configDict["maxDeflection"]: 
            # if the inclination is greater than maxDeflection set to maxDeflection
            self.currentState['angleX'] = (
                numpy.sign(self.currentState['angleX'])*
                self.configDict["maxDeflection"])
        self.currentState['angleY'] = self.currentState['angleY'] + angleYChange
        if abs(self.currentState['angleY']) > self.configDict["maxDeflection"]: 
            # if the inclination is greater than maxDeflection set to maxDeflection
            self.currentState['angleY'] = (
                numpy.sign(self.currentState['angleY'])*
                self.configDict["maxDeflection"])
        # change the postition of the ball
        nextPos, nextVel, self.ballInHole = \
            self.maze.executeMovement(currentPos, currentVel, 
                                      (self.currentState['angleX'],
                                       self.currentState['angleY']),
                                      self.configDict['transitionProbability'])
        self.currentState['column'] = nextPos[0]
        self.currentState['row'] = nextPos[1]
        self.currentState['velocityX']= nextVel[0]
        self.currentState['velocityY']= nextVel[1]
        if abs(self.currentState['velocityX']) > self.configDict["maxDeflection"]:
            # if the inclination is greater than maxDeflection set to maxDeflection
            self.currentState['velocityX'] = (
                numpy.sign(self.currentState['velocityX'])*
                self.configDict["maxDeflection"])
        if abs(self.currentState['velocityY']) > self.configDict["maxDeflection"]: 
            # if the inclination is greater than maxDeflection set to maxDeflection
            self.currentState['velocityY'] = (
                numpy.sign(self.currentState['velocityY'])*
                self.configDict["maxDeflection"])

    def _checkEpisodeFinished(self):
        "Checks whether the episode is finished, i. e. the goal is reached"        
        currentPos = (self.currentState['column'],self.currentState['row'])
        return self.maze.isGoalReached(currentPos) or self.ballInHole
    
    def _createStateForAgent(self, state):
        "Create a state description for the agent"
        return state
    
class Maze(object):
    """
    A class which represents the two-dimensional maze.
    """
    def __init__(self, rows, columns):
        "Create an empty maze with the specified number of rows and columns"
        self.structure = [[[] for i in range(columns)] for j in range(rows)]
        self.startPos = None
        self.goalPos = None
    
    @staticmethod
    def createMazeFromString(string):
        """
        Factory method which creates a maze based on the string which is passed.
        """
        structure = []
        for row in map(lambda s: s.strip(),string.split('\n')):
            if row == '': continue
            structure.append(list(row))
            
        maze = Maze(len(structure[0]), len(structure))
        for row_index, row in enumerate(structure):
            for col_index, col in enumerate(row):
                maze.structure[col_index][row_index] = 1 if col == '*' else 0
                if col == 'S':
                    maze.startPos = (col_index,row_index)
                if col == 'G':
                    maze.goalPos = (col_index,row_index)
                if col <= 'z' and col >= 'a':
                    maze.structure[col_index][row_index] = -(ord(col)-ord('a'))-1
        return maze

    def getColumns(self):
        "Returns the number of columns of the maze"
        return len(self.structure)
        
    def getRows(self):
        "Returns the number of rows of the maze"
        return len(self.structure[0])
    
    def getStartPosition(self):
        "Returns the start position of the maze"
        return self.startPos
        
    def isGoalReached(self, pos):
        "Checks if the given position is the goal position"
        return pos == self.goalPos

    def argmax(self, delta):
        """Returns the index with the biggest absolut value
        if the absolut values are equal -1 will be returned
        """
        if delta[0] > delta[1]:
            return 0
        if delta[0] < delta[1]:
            return 1
        return -1

    def getGridCellType(self, pos):
        gridCellValue = self.structure[pos[0]][pos[1]]
        if gridCellValue == 0:
            return "free"
        elif gridCellValue ==  1:
            return "wall"
        else:
            return "hole"

    def getSteps(self, move):
        absoluteMove = abs(move)
        if max(absoluteMove) == 0:
            return []
        steps= numpy.array(range(max(absoluteMove)+1))
        steps=steps*(float(min(absoluteMove))/float(max(absoluteMove)))
        steps=numpy.round(steps)
        steps=numpy.diff(steps)
        return steps

    def _updateVelocity(self, movedirection, velocity):
        currentVelocity = velocity[movedirection]
        velocity[movedirection]=currentVelocity/2.0*(-1)
        return velocity

    def _getRandomNeighborOffset(self):
        a = [-1,0,1]
        setOfTuples = [ (b1,b2) for b1 in a for b2 in a]
        setOfTuples.remove( (0,0) )
        return( setOfTuples[random.randint(0,len(setOfTuples)-1)] )

    def executeMovement(self, posFrom, curVel, inclination, transitionProbability):
        "Returns a list of positions which lead from one position to the other"
#        print "getPath posFrom:",posFrom,"inclination:",inclination, "curVel:",curVel
        # reduce the curVel by one on each dimension to have a very basic
        # friction
        velX = curVel[0]-numpy.sign(curVel[0])
        velY = curVel[1]-numpy.sign(curVel[1])
        # ball in the hole flag
        ballInHole=False
        # ball passed the goal flag
        ballpassedGoal=False
        # the position during moving relative to the posFrom position
        relativePosition = numpy.array([0,0])
        # the new velocity equals the inclination + current velocity
        newVelocity = numpy.array(inclination) + numpy.array([velX,velY])
        # delta is the moving vector for this step
        delta = numpy.array(newVelocity)
        # if transistion probability is smaller than 1 in the config
        # do sometimes change the delta to a adjacent grid cell.
        if random.random() > transitionProbability:
            delta += self._getRandomNeighborOffset()
        # the number of steps
        stepCount = max(abs(delta[0]),abs(delta[1]))
        # variable to check for loops in the processing
        lastAction = '' # no bounce
        beforeLastAction = ''
        # try to move to the desired location
        steps=self.getSteps(delta)
        step = 0
        while step < len(steps):
            # check for a loop
            if beforeLastAction != '' and beforeLastAction == lastAction:
                break
            beforeLastAction = lastAction
            lastAction = ''
            # check if there is no move to do any more (can happen when hitting a wall)
            if numpy.array_equal(delta, (0,0)):
                break
            # get argmax as moving direction, if equal set to -1
            movedirection = self.argmax(abs(delta))
            if steps[step] == 0.:
                # stright move
                # single step moving vector
                singleStepVector = numpy.array([0,0])
                singleStepVector[movedirection]=numpy.sign(delta[movedirection])
                # reduce delta
                delta-=singleStepVector
                # get coordinates of the next relative position
                newRelativePosition=relativePosition+singleStepVector
                # check the next position type 
                type = self.getGridCellType(newRelativePosition+posFrom)
                # 
                if type == "hole":
                    # rise ball in hole flag and exit the step loop
                    relativePosition=newRelativePosition
                    ballInHole=True
                    break
                if type == "goal":
                    # rise the goal passed flag
                    ballPassedGoal=True
                if type == "goal" or type == "free":
                    # move to the new position
                    relativePosition=newRelativePosition
                    pass
                if type == "wall":
                    # reset step, as steps will get reset a few lines down
                    step = -1
                    # update velocity
                    newVelocity = self._updateVelocity(movedirection, 
                                                       newVelocity)+inclination
                    # update delta
                    delta[movedirection] = newVelocity[movedirection]
                    # update step kinds
                    stepCount = len(steps)
                    steps = self.getSteps(delta)
                    lastAction="straight move bounce"
            else:
                # diagonally 
                # single step moving vector
                singleStepVector = numpy.array(
                    [numpy.sign(delta[0]),
                     numpy.sign(delta[1])])
                # reduce delta
                delta-=singleStepVector
                # get grid cells of the neighbors and the destination
                horizontalNeighbor = numpy.array(
                    [singleStepVector[0],0])
                verticalNeighbor = numpy.array(
                    [0,singleStepVector[1]])
                destination = numpy.array(
                    [singleStepVector[0],singleStepVector[1]])
                # check the grid cells
                horizontalNeighborType = self.getGridCellType(horizontalNeighbor+relativePosition+posFrom)
                verticalNeighborType = self.getGridCellType(verticalNeighbor+relativePosition+posFrom)
                destinationType = self.getGridCellType(destination+relativePosition+posFrom)
                if destinationType == "free" and (
                    horizontalNeighborType == "free" or
                    verticalNeighborType == "free"):
                    # move to destination
                    relativePosition=relativePosition+singleStepVector
                    pass
                elif ( (destinationType == "wall" and horizontalNeighborType != "wall" and
                        verticalNeighborType != "wall") or
                       (horizontalNeighborType == "wall" and verticalNeighborType == "wall") ):
                    # bounce in both directions
                    # reset step, as steps will get reset a few lines down
                    step = -1
                    # update velocity for both directions
                    newVelocity = self._updateVelocity(0,newVelocity)
                    newVelocity = self._updateVelocity(1,newVelocity)#+inclination
                    # update delta
                    delta = newVelocity
                    # update step kinds
                    stepCount = len(steps)
                    steps = self.getSteps(delta)
                    lastAction="diagonal move bounce both"
                    pass
                elif ( destinationType == "wall" and horizontalNeighborType == "wall" and
                       verticalNeighborType == "free"):
                    # move vertically + bounce horizontally
                    # relativePosition=relativePosition+numpy.array([0,singleStepVector[1]])
                    # reset step, as steps will get reset a few lines down
                    step = -1
                    # update velocity
                    newVelocity = self._updateVelocity(0, 
                                                       newVelocity)#+inclination
                    # update delta
                    delta[0] = newVelocity[0]
                    delta[1] += singleStepVector[1]
                    # update step kinds
                    stepCount = len(steps)
                    steps = self.getSteps(delta)
                    lastAction="diagonal move bounce horizontal"
                elif ( destinationType == "wall" and horizontalNeighborType == "free" and
                       verticalNeighborType == "wall"):
                    # move horizontally + bounce vertically
                    # relativePosition=relativePosition+numpy.array([singleStepVector[0],0])
                    # reset step, as steps will get reset a few lines down
                    step = -1
                    # update velocity
                    newVelocity = self._updateVelocity(1, newVelocity)#+inclination
                    # update delta
                    delta[1] = newVelocity[1]
                    delta[0] += singleStepVector[0]
                    # update step kinds
                    steps = self.getSteps(delta)
                    lastAction="diagonal move bounce vertical"
                    pass
                else:
                    # fall in a hole
                    # check in which hole to fall
                    if horizontalNeighborType=="hole":
                        relativePosition=relativePosition+numpy.array([singleStepVector[0],0])
                    elif verticalNeighborType=="hole":
                        relativePosition=relativePosition+numpy.array([0,singleStepVector[1]])
                    elif destinationType=="hole":
                        relativePosition=relativePosition+singleStepVector
                    else:
                        # we should never end up here...
                        print "ERROR"
                        exit(1)
                    ballInHole=True
                    break
                
                #singleStepVector[movedirection]=singleStepVector[movedirection]
            step=step+1
        return (posFrom+relativePosition,newVelocity, ballInHole)
   
EnvironmentClass = DiscreteBrioEnvironment
EnvironmentName = "Discrete BRIO Labyrinth"
