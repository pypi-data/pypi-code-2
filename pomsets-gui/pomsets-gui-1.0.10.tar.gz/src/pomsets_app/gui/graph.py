import logging
import os

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule


import pomsets.definition as DefinitionModule
import pomsets.task as TaskModule
import pomsets.parameter as ParameterModule
import pomsets.resource as ResourceModule


from PyQt4.QtCore import *


import pomsets_app.gui.policy as PolicyModule

IMAGE_SELECTED_TRUE = 'image selected'
IMAGE_SELECTED_FALSE = 'image not selected'
IMAGE_PARAMETER_SWEEP = 'image parameter sweep'


class LocalGraphObject(ResourceModule.Struct):

    ATTRIBUTES = [
        'visible', 'isSelected', 'isSelectable', 'isClickable',
        'contextManager'
        ]

    # This is a hack,
    # until we move the common graph object code 
    def __init__(self):
        ResourceModule.Struct.__init__(self)
        self.isSelected(False)
        self.visible(True)
        return

    def overlaps(self, point):
        return False

    pass


class Point(object):
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
        return

class Rect(LocalGraphObject):

    ATTRIBUTES = LocalGraphObject.ATTRIBUTES + [
        'filled'
        ]

    def __init__(self, x, y, width, height):
        LocalGraphObject.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        return

    def containsPoint(self, point):
        # TODO:
        # need to handle negative widths and heights

        return self.x < point.x and \
            self.x + self.width > point.x and \
            self.y < point.y and \
            self.y + self.height > point.y


    def intersectsLine(self, line):
        points = [Point(self.x, self.y),
                  Point(self.x+self.width, self.y),
                  Point(self.x+self.width, self.y+self.height),
                  Point(self.x, self.y+self.height)]
        for points in zip(points[:-1],points[1:]):
            rectEdge = Line()
            rectEdge.points = points
            if line.intersectsLine(rectEdge):
                return True
        return False

    # END class Rect
    pass



class Line(LocalGraphObject):

    ATTRIBUTES = LocalGraphObject.ATTRIBUTES + []

    @staticmethod
    def ccw(A,B,C):
        """
        from http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
        """
	return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

    def __init__(self):
        LocalGraphObject.__init__(self)
        return
    
    def intersectsLine(self, other):
        A = self.points[0]
        B = self.points[1]
        C = other.points[0]
        D = other.points[1]
        return Line.ccw(A,C,D) != Line.ccw(B,C,D) and \
            Line.ccw(A,B,C) != Line.ccw(A,B,D)
        
    # END class Line
    pass


class Triangle(object):
    # END class Triangle
    pass


class Circle(object):

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        return

    # END class Circle
    pass


class Text(LocalGraphObject):
    ALIGN_LEFT = 'left'
    ALIGN_RIGHT = 'right'
    ALIGN_CENTER = 'center'

    ALIGN_TOP = 'top'
    ALIGN_MIDDLE = 'middle'
    ALIGN_BOTTOM = 'bottom'

    def __init__(self):
        LocalGraphObject.__init__(self)
        return

    """
    def getDrawingOffset(self, textBoundingRect, zoomFactor):

        # TODO:
        # use QFontMetrics.boundingRect


        # fontSize = self.font.getSize(self.text)

        selfWidth = self.size[0]
        selfHeight = self.size[1]

        xx = 0
        if self.horizontal_align is Text.ALIGN_CENTER:		# CENTER ALIGN
            print "in center halign"
            xx = (selfWidth-textBoundingRect.width())/2
        elif self.horizontal_align is Text.ALIGN_RIGHT:	# RIGHT ALIGN
            print "in right halign"
            xx = (selfWidth-textBoundingRect.width())
        else:
            print "in left halign"
    
        #yy = zoomFactor * textBoundingRect.height()/4.0
        # yy = 0
        yy = textBoundingRect.height() / 4.0
        if self.vertical_align is Text.ALIGN_MIDDLE:		# MIDDLE ALIGN
            print "in middle valign"
            yy = yy+ (selfHeight-textBoundingRect.height())/2
        elif self.vertical_align is Text.ALIGN_BOTTOM:		# BOTTOM ALIGN
            print "in bottom valign"
            yy = yy+ (selfHeight-textBoundingRect.height())
        else:
            print "in top valign"

        xx = xx*1.0/zoomFactor
        yy = yy*1.0/zoomFactor

        #print "returning %s,%s drawing offset" % (xx,yy)
        return 0, yy
        # return 0, 0
    """

    # END class Text
    pass


class Node(LocalGraphObject):

    ATTRIBUTES = LocalGraphObject.ATTRIBUTES + [
        'task',
        'statusUpdater',
        'shouldDisplayExecutionStatus',
        'shouldUpdateDisplay',
        'shouldUpdateImage',
        'shouldUpdateColors'
    ]

    PART_EXECUTE_STATUS = 'execute status'
    PART_DISPLAY_IMAGES = 'display images'

    PART_BORDER = "node border"
    PART_BACKGROUND = "node background"
    PART_LABEL = "node label"

    
    def __init__(self, nodeData, *args, **kwds):
        LocalGraphObject.__init__(self)

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.inputPorts = {}
        self.outputPorts = {}
        self.parts = {
            "inputPorts":self.inputPorts,
            "outputPorts":self.outputPorts
            }

        
        self.nodeData = nodeData
        
        self.shouldUpdateDisplay(True)
        self.shouldUpdateImage(False)
        self.shouldUpdateColors(True)

        self.isClickable(True)
        self.isSelectable(True)
        return


    def _buildChildren(self):
        """
        returns the parts that are to be drawn
        """

        parts = []

        imageMap = self.parts.get(Node.PART_DISPLAY_IMAGES, {})
        if IMAGE_PARAMETER_SWEEP in imageMap:
            parts.append(imageMap[IMAGE_PARAMETER_SWEEP])
        if IMAGE_SELECTED_TRUE in imageMap:
            parts.append(imageMap[IMAGE_SELECTED_TRUE])
        if IMAGE_SELECTED_FALSE in imageMap:
            parts.append(imageMap[IMAGE_SELECTED_FALSE])

            
        parts.append(self.parts[Node.PART_BACKGROUND])
        parts.append(self.parts[Node.PART_LABEL])
        parts.extend(self.inputPorts.values())
        parts.extend(self.outputPorts.values())

        if self.shouldDrawExecuteStatus():
            parts.append(self.parts[Node.PART_EXECUTE_STATUS])

        return parts


    def partPrimitives(self):
        return self.children()

    def children(self):
        """
        A subclass can override this
        """
        if not hasattr(self, '_children'):
            # cache this so that we dont have to recompute 
            # for every redraw
            self._children = self._buildChildren()
            pass
        return self._children

    
    def configurePerformers(self, task):

        self.task(task)

        parentTask = task.parentTask()
        taskInfo = parentTask.getTaskInformation(task)
        values = taskInfo._values
        guiNode = self

        import mext.reaction.component as trellis
        
        class StatusUpdater(trellis.Component):
            @trellis.maintain
            def update(self):

                logging.debug("performer.update")
                
                if not hasattr(values, 'changed'):
                    return

                changes = getattr(values, 'changed')
                if not 'status' in changes:
                    return

                guiNode.updateExecuteStatus(changes['status'])
                task.automaton().contextManager().mainWindow().emit(
                    SIGNAL("OnTaskExecutionStatusChanged()"))

                        
                return
            # END class StatusUpdater
            pass

        statusUpdater = StatusUpdater()
        self.statusUpdater(statusUpdater)

        return


    def updateDisplay(self):
        if self.shouldUpdateColors():
            self.updateColors()

        if self.shouldUpdateImage():
            self.updateImage()
        return


    def shouldDrawExecuteStatus(self):
        dataNode = self.nodeData
        guiOptions = dataNode.guiOptions()
        return guiOptions.get('should draw execute status', True)

    def shouldDrawTemporalParameters(self):
        dataNode = self.nodeData
        guiOptions = dataNode.guiOptions()
        return guiOptions.get('should draw temporal parameters', True)
        

    def retrieveInputPortNamesFromDataObject(self):
        # getParametersByFilter

        filter = FilterModule.constructAndFilter()

        filter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_DIRECTION_INPUT),
                keyFunction=lambda x: x.portDirection()
            )
        )

        if not self.shouldDrawTemporalParameters():
            notTemporalFilter = FilterModule.constructNotFilter()
            notTemporalFilter.addFilter(
                FilterModule.ObjectKeyMatchesFilter(
                    filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL),
                    keyFunction=lambda x: x.portType()
                )
            )
            filter.addFilter(notTemporalFilter)
            pass

        """
        notSideEffectFilter = FilterModule.constructNotFilter()
        notSideEffectFilter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter=FilterModule.IdentityFilter(True),
                keyFunction=lambda x: x.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT)
            )
        )
        filter.addFilter(notSideEffectFilter)
        """

        parameters = self.nodeData.getParametersByFilter(filter)
        
        parameterNames = [x.id() for x in parameters]
        return parameterNames



    def retrieveOutputPortNamesFromDataObject(self):
        filter = FilterModule.constructOrFilter()

        outputValueFilter = FilterModule.ObjectKeyMatchesFilter(
            filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_DIRECTION_OUTPUT),
            keyFunction=lambda x: x.portDirection()
        )

        if not self.shouldDrawTemporalParameters():
            f = FilterModule.constructAndFilter()
            f.addFilter(outputValueFilter)
            outputValueFilter = f
            
            notTemporalFilter = FilterModule.constructNotFilter()
            notTemporalFilter.addFilter(
                FilterModule.ObjectKeyMatchesFilter(
                    filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL),
                    keyFunction=lambda x: x.portType()
                )
            )
            outputValueFilter.addFilter(notTemporalFilter)
            pass
        
        filter.addFilter(outputValueFilter)
        filter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter=FilterModule.IdentityFilter(True),
                keyFunction=lambda x: x.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT)
            )
        )

        parameters = self.nodeData.getParametersByFilter(filter)
        parameterNames = [x.id() for x in parameters]
        return parameterNames

    

    def getResourceKeyForPort(self, portName):
        return 'gui port class'


    def setupPorts(self, nodePolicy):

        portPolicy = nodePolicy.portPolicy()

        inputPortNames = self.retrieveInputPortNamesFromDataObject()
        outputPortNames = self.retrieveOutputPortNamesFromDataObject()

        for portDirection, portNames, portMap in [
            (Port.PORT_DIRECTION_INPUT, inputPortNames, self.inputPorts),
            (Port.PORT_DIRECTION_OUTPUT, outputPortNames, self.outputPorts)]:

            positionCount = len(portNames)
            for index, portName in enumerate(portNames):

                resourceKey = self.getResourceKeyForPort(portName)
                portClass = self.contextManager().app().getResourceValue(
                    resourceKey, default=Port)
                port = portClass()
                port.name = portName
                port.node = self
                port.direction = portDirection
                port.positionIndex(index)
                port.positionCount(positionCount)

                port.initialSetup()

                portPolicy.setupDimensions(port)

                # we need to first know the port's dimensions
                # beefore we can set its position
                nodePolicy.setPortPosition(self, port)

                port.setupPrimitives(portPolicy)

                portMap[portName] = port
                pass
            pass

        return


    def setupPrimitives(self, nodePolicy):

        nodePolicy.setupDimensions(self)

        #font = nodePolicy.visualPolicy().font(
        #    PolicyModule.VisualPolicy.KEY_FONT_DEFAULT)
        #self.font = font

        background = self.createBackgroundPrimitive()

        nameLabel = self.createNamePrimitive(nodePolicy)

        self.parts[Node.PART_BACKGROUND] = background
        self.parts[Node.PART_LABEL] = nameLabel
        self.parts["colors"] = nodePolicy._colors

        self.setupPorts(nodePolicy)

        self.shouldUpdateDisplay(True)

        # TODO: 
        # consolidate code that creates a new label
        executeLabel = Text()
        executeLabel.alpha = 1.0
        executeLabel.color = [1.0, 1.0, 1.0, 1.0]
        executeLabel.position = nodePolicy.getPositionForExecuteStatusLabel()
        executeLabel.size = [self.width, self.height, 0]

        # TODO:
        # this text should be dependent upon
        # whether there's a task associated with it
        executeLabel.text = TaskModule.Task.EXECUTE_STATUS_UNINITIALIZED
        self.parts[Node.PART_EXECUTE_STATUS] = executeLabel

        self.setupImageMap(nodePolicy)

        return

    def createNamePrimitive(self, nodePolicy):
        # Fit node to text size or simply to
        # what graphviz gives us, which may not look good
        # depending on the NodePolicy
        #stringBounds = font.getSize(node.nodeData.name)
        #nodeSize = (stringBounds[0] + 2*10, stringBounds[1] + 2*10)
        # nodeSize = self.getBounds()


        # initialize the name label
        nameLabel = Text()
        nameLabel.alpha = 1.0
        nameLabel.color = [1.0, 1.0, 1.0, 1.0]
        nameLabel.position = nodePolicy.getPositionForNameLabel()
        nameLabel.size = [self.width, self.height, 0]
        # nameLabel.font = self.font
        nameLabel.text = self.nodeData.name()
        return nameLabel


    def createBackgroundPrimitive(self, size=None):

        if size is None:
            size = self.getBounds()
        background = Rect(0, 0, size[0], size[1])

        background.size = size
        background.position = [0, 0, 0]


        background.corner_mode = True
        return background

    def getBounds(self):
        return (self.width, self.height)


    def getParameterSweepImage(self):
        return 'ps unselected.png'
    
    def getImageSelectedFile(self):
        return 'node selected.png'

    def getImageNotSelectedFile(self):
        return 'node unselected.png'

    def setupImageMap(self, nodePolicy):
        self._setupImageMap(nodePolicy)
        self.setImageSelected(False)
        return


    def setImageParameterSweep(self, isParameterSweep):
        imageMap = self.parts[Node.PART_DISPLAY_IMAGES]

        imageMap[IMAGE_PARAMETER_SWEEP].visible(isParameterSweep)
        return

    def setImageSelected(self, isSelected):
        imageMap = self.parts[Node.PART_DISPLAY_IMAGES]

        imageMap[IMAGE_SELECTED_TRUE].visible(isSelected)
        imageMap[IMAGE_SELECTED_FALSE].visible(not isSelected)
            
        return


    def _setupImageMap(self, nodePolicy):

        self.shouldUpdateImage(True)
        self.shouldUpdateColors(False)

        contextManager = nodePolicy.contextManager()
        app = contextManager.app()

        imageSelectedPath = os.path.join(contextManager.imagePath(),
                                         self.getImageSelectedFile())
        imageNotSelectedPath = os.path.join(contextManager.imagePath(),
                                            self.getImageNotSelectedFile())
        imageParameterSweepPath = os.path.join(contextManager.imagePath(),
                                           self.getParameterSweepImage())
        
        imageSelected = self.createBackgroundPrimitive()
        imageSelected._texture_image_file = imageSelectedPath
        imageSelected.use_texture = True

        imageNotSelected = self.createBackgroundPrimitive()
        imageNotSelected._texture_image_file = imageNotSelectedPath
        imageNotSelected.use_texture = True

        size = self.getBounds()
        diffX = size[0]/12.0
        diffY = -1*diffX
        imageParameterSweep = self.createBackgroundPrimitive(size=size)
        imageParameterSweep._texture_image_file = imageParameterSweepPath
        imageParameterSweep.use_texture = True

        # NOTE:
        # this is a hack to get the PS image drawing
        imageParameterSweep.offsetPosition = (diffX, diffY, 0)

        # now specify the images for selected/unselected
        imageMap = {
            IMAGE_SELECTED_TRUE:imageSelected,
            IMAGE_SELECTED_FALSE:imageNotSelected,
            IMAGE_PARAMETER_SWEEP:imageParameterSweep
        }

        self.parts[Node.PART_DISPLAY_IMAGES] = imageMap
        self.parts[Node.PART_BACKGROUND].visible(False)

        generator = TaskModule.getTaskGeneratorForDefinition(self.nodeData)
        isParameterSweep = isinstance(
            generator, TaskModule.ParameterSweepTaskGenerator)
        self.setImageParameterSweep(isParameterSweep)
        
        return


    def updateExecuteStatus(self, status):

        executeLabel = self.parts[Node.PART_EXECUTE_STATUS]
        executeLabel.text = status

        # reset the cached values
        # so that they will be recached
        if hasattr(self, '_children'):
            delattr(self, '_children')

        return


    def getPosition(self):
        return (self.x, self.y)

    def setPosition(self, x, y):
        self.x = x
        self.y = y
        return


    def updateColors(self):

        colors = self.parts["colors"]
        background = self.parts[Node.PART_BACKGROUND]
        text = self.parts[Node.PART_LABEL]
        if self.isSelected():
            logging.debug("updating for selected node")
            background.borderColor = colors[PolicyModule.NodePolicy.KEY_BORDER_SELECTION_TRUE]
            background.color = colors[PolicyModule.NodePolicy.KEY_BACKGROUND_SELECTION_TRUE]
            text.color = colors[PolicyModule.NodePolicy.KEY_TEXT_SELECTION_TRUE]
        else:
            logging.debug("updating for unselected node")
            background.borderColor = colors[PolicyModule.NodePolicy.KEY_BORDER_SELECTION_FALSE]
            background.color = colors[PolicyModule.NodePolicy.KEY_BACKGROUND_SELECTION_FALSE]
            text.color = colors[PolicyModule.NodePolicy.KEY_TEXT_SELECTION_FALSE]
            pass

        return


    def updateImage(self):
        self.setImageSelected(self.isSelected())
        return


    def intersectsRect(self, rect):

        if (rect.x+rect.width > self.x) and \
           (rect.x < self.x+self.width) and \
           (rect.y+rect.height > self.y) and \
           (rect.y < self.y+self.height):
            return True 

        return False


    def overlaps(self, point):
        if point.x < self.x:
            return False
        if point.x > self.x+self.width:
            return False
        if point.y < self.y:
            return False
        if point.y > self.y+self.height:
            return False
        return True


    # END class Node
    pass


class NestNode(Node):


    def getImageSelectedFile(self):
        return 'nest selected.png'

    def getImageNotSelectedFile(self):
        return 'nest unselected.png'

    # END class NestNode
    pass


class BranchNode(Node):

    # TODO:
    # implement the generation of the branch node image
    # and have this class return that value
    
    # END class BranchNode
    pass


class LoopNode(Node):

    # TODO:
    # implement the generation of the loop node image
    # and have this class return that value
    
    # END class LoopNode
    pass



class Edge(LocalGraphObject):

    DEFAULT_WIDTH = 3
    DEFAULT_WIDTH_SELECTED = 4

    ATTRIBUTES = LocalGraphObject.ATTRIBUTES + []

    def __init__(self, dataPath=None, guiPath=None):
        LocalGraphObject.__init__(self)

        self._dataPath = dataPath
        self.guiPath = guiPath

        self.isSelectable(True)
        self.isClickable(True)
        return


    def isDynamic(self, value=None):
        if value is not None:
            self._isDynamic = value
        if not hasattr(self, '_isDynamic'):
            self._isDynamic = False
        return self._isDynamic

    def getWidth(self):
        if self.isSelected():
            return Edge.DEFAULT_WIDTH_SELECTED
        return Edge.DEFAULT_WIDTH

    def getColor(self):
        if self.isDynamic():
            return self._dynamicColor
        if self.isSelected():
            return self._selectedColor
        return self._unselectedColor


    def inputPort(self):
        return self.guiPath[1]

    def outputPort(self):
        return self.guiPath[-2]

    def inputNode(self):
        return self.guiPath[0]

    def outputNode(self):
        return self.guiPath[-1]

    def sourceNode(self):
        return self.inputNode()

    def targetNode(self):
        return self.outputNode()


    def intersectsRect(self, rect):
        # contains = any([rect.containsPoint(Point(*x)) for x in self.points])
        # return contains
        # def intersectsLine(self, line):
        for startPoint, endPoint in zip(self.points[:-1], self.points[1:]):
            line = Line()
            line.points = [startPoint, endPoint]
            if rect.intersectsLine(line):
                return True
        if any([rect.containsPoint(x) for x in self.points]):
            return True
        return False


    def setupPrimitives(self, edgePolicy):
        self.children = []

        try:
            inputPort = self.inputPort()
            outputPort = self.outputPort()

            point1 = Point(
                self.inputNode().x + inputPort.x + inputPort.width/2, 
                self.inputNode().y + inputPort.y + inputPort.height/2)
            point2 = Point(
                self.outputNode().x + outputPort.x + outputPort.width/2, 
                self.outputNode().y + outputPort.y + outputPort.height/2)
        except AttributeError, e:
            logging.error(e)
            return

        line = Line()
        points = edgePolicy.createPath((point1.x, point1.y),
                                       (point2.x, point2.y))
        pointObjects = [Point(x, y, z) for x,y,z in points]
        line.points= pointObjects
        self.points = pointObjects
        self.children.append(line)
        edgePolicy.updateEdge(self)

        self.setupColors(edgePolicy)
        return



    def shouldUpdateDisplay(self, value):
        # no need for edges to update for now
        return

    def updateDisplay(self):
        # no need for edges to update for now
        return

    def setupColors(self, edgePolicy):

        visualPolicy = edgePolicy.visualPolicy()

        self._selectedColor = visualPolicy.color(
            PolicyModule.EdgePolicy.KEY_SELECTION_TRUE)
        self._unselectedColor = visualPolicy.color(
            PolicyModule.EdgePolicy.KEY_SELECTION_FALSE)
        self._dynamicColor = visualPolicy.color(
            PolicyModule.EdgePolicy.KEY_DYNAMIC)

        return

    def overlaps(self, point):
        rect = Rect(
            point.x-3, point.y-3,
            6, 6)
        return self.intersectsRect(rect)


    # END class Edge
    pass


class Port(LocalGraphObject):

    ATTRIBUTES = LocalGraphObject.ATTRIBUTES + [
        'positionIndex',
        'positionCount',
        ]

    PART_BACKGROUND = "port background"

    PORT_DIRECTION_INPUT = 1
    PORT_DIRECTION_OUTPUT = 2


    def __init__(self, *args, **kwds):

        LocalGraphObject.__init__(self)

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.children = []
        self.edge = None
        self.basePosition = (0, 0)

        self.isClickable(True)
        self.isSelectable(False)
        return


    def createBackgroundPrimitive(self, portPolicy):
        
        dataNode = self.node.nodeData
        contextManager = portPolicy.contextManager()
        parameterId = self.name
        
        parameter = dataNode.getParameter(parameterId)

        background = None
        if self.dataType == ParameterModule.PORT_TYPE_TEMPORAL:
            background = Circle(0, 0, self.width/2.0)
            pass
        else:
            background = Rect(0, 0, self.width, self.height)
            pass
        
        background.position = [0, 0, 0]
        background.size = [self.width, self.height, 1.0]
        background.corner_mode = True
        
        background.color = None
        background.borderColor = [0.5, 0.5, 0.0, 1.0]
        
        return background
    
    
    def initialSetup(self):
        
        dataNode = self.node.nodeData
        parameterId = self.name
        parameter = dataNode.getParameter(parameterId)
        self.dataType = parameter.portType()
        
        return
    

    def overlaps(self, point):
        """
        TODO:
        This is copied from Node.Node
        Need to remove duplication
        """

        selfX = self.x + self.node.x
        selfY = self.y + self.node.y

        if point.x < selfX:
            return False
        if point.x > selfX+self.width:
            return False
        if point.y < selfY:
            return False
        if point.y > selfY+self.height:
            return False
        return True

    
    def setupPrimitives(self, portPolicy):
        
        background = self.createBackgroundPrimitive(portPolicy)
        
        self.parts = {}
        self.parts[Port.PART_BACKGROUND] = background

        self.children.append(background)

        return


    def updateColors(self):

        # No color policy for Ports set up yet 
        #colors = self.parts["colors"]

        background = self.parts[Port.PART_BACKGROUND]
        if self.edge is not None:
            background.borderColor = [0.8, 0.8, 0.0, 1.0]
            # background.color = [0.5, 0.5, 0.0, 1.0]
        else:
            background.borderColor = [0.8, 0.8, 0.0, 1.0]
            background.color = None
            pass

        return


    # END class Port
    pass
