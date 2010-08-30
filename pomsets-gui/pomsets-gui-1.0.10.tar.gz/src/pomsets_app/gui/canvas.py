import functools
import logging

import numpy

import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


import pypatterns.filter as FilterModule

import pypatterns.relational as RelationalModule
import pomsets.resource as ResourceModule

import pomsets.definition as DefinitionModule
import pomsets.task as TaskModule
import pomsets.parameter as ParameterModule

import pomsets_app.gui.graph as GraphModule



class Canvas(ResourceModule.Struct):

    ATTRIBUTES = [
        'contextManager',
        'nodePolicy',
        'edgePolicy',
        'layoutPolicy',
        'visualPolicy',
        'portPolicy'
        ]

    def __init__(self):

        ResourceModule.Struct.__init__(self)

        self.scroll_position = [0.0, 0.0]

        # set up the zoom and pan matrices
        self.zoomMatrix = numpy.matrix('1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1')
        self.panMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; 0 0 0 0')

        self.selection_rectangle = None

        self._selected = []
        self.resetDrawables()
        return


    def resetDrawables(self):
        self._dynamicEdge = None
        self.nodes = []
        self.edges = []
        self.selectables = set([])
        self.clickables = set([])
        self.layers = {}
        for layerName in ['edges', 'nodes']:
            layer = CanvasLayer(layerName)
            self.layers[layerName] = layer
            pass
        self.setSelection([])
        return


    def addDrawable(self, drawable):
        if isinstance(drawable, GraphModule.Node):
            self.nodes.append(drawable)
            self.layers['nodes'].addChild(drawable)

            ports = drawable.inputPorts.values() + drawable.outputPorts.values()
            for port in ports:
                self.determineSelectable(port)
                self.determineClickable(port)

        if isinstance(drawable, GraphModule.Edge):
            self.edges.append(drawable)
            self.layers['edges'].addChild(drawable)

        self.determineSelectable(drawable)
        self.determineClickable(drawable)
        return


    def determineSelectable(self, object):
        if object.isSelectable():
            self.selectables.add(object)
        return

    def determineClickable(self, object):
        if object.isClickable():
            self.clickables.add(object)

        return

    def removeDrawable(self, drawable):
        return self.removeChild(drawable)
    
    def removeChild(self, drawable):
        # remove from layers
        for layer in self.layers.values():
            layer.removeChild(drawable)

        if isinstance(drawable, GraphModule.Node):
            ports = drawable.inputPorts.values() + drawable.outputPorts.values()
            for port in ports:
                self.selectables.discard(port)
                self.clickables.discard(port)

        self.selectables.discard(drawable)
        self.clickables.discard(drawable)
        return

    def getSelectables(self):
        return self.selectables

    def getClickables(self):
        return self.clickables

    def computeLayout(self):

        if not len(self.nodes):
            # no need to compute layout if self has no nodes
            return

        (x_max, y_max) = self.layoutPolicy().layoutNodes(
            self.nodes, self.edges)
        self.scroll_bounds = (x_max, y_max)

        # because the node positions have been updated
        # the edge points need to be recomputed
        # map(lambda x: x.setupPrimitives(self.nodePolicy()), self.nodes)
        map(lambda x: x.setupPrimitives(self.edgePolicy()), self.edges)

        return


    def setScrollPosition(self, new_scroll_position):
        self.scroll_position = new_scroll_position
        self.validateScrollPosition()


    def computeDynamicEdge(self, initialPosition, finalPosition):

        edgePolicy = self.edgePolicy()

        initialCanvasMatrix = numpy.matrix(
            '1 0 0 0; 0 1 0 0; 0 0 1 0; %s %s 0 1' % 
            (initialPosition.x, initialPosition.y))
        finalCanvasMatrix = numpy.matrix(
            '1 0 0 0; 0 1 0 0; 0 0 1 0; %s %s 0 1' % 
            (finalPosition.x, finalPosition.y))

        initialWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(
            initialCanvasMatrix)
        finalWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(
            finalCanvasMatrix)

        point1 = GraphModule.Point(
            initialWorldMatrix[3,0], initialWorldMatrix[3,1])
        point2 = GraphModule.Point(
            finalWorldMatrix[3,0], finalWorldMatrix[3,1])

        line = GraphModule.Line()

        points = edgePolicy.createPath((point1.x, point1.y),
                                       (point2.x, point2.y))
        pointObjects = [GraphModule.Point(x,y,0) for x,y,z in points]
        line.points = pointObjects

        line.position = (0.0, 0.0, 0.01)
        line.color = [0.7, 0.7, 1.0, 0.3]
        
        edgeClass = self.contextManager().app().getResourceValue(
            'gui edge class', default=GraphModule.Edge)
        self._dynamicEdge = edgeClass()
        self._dynamicEdge.children = [line]
        self._dynamicEdge.setupColors(self.edgePolicy())
        # self.points = line.points

        pass


    def drawLayers(self):
        # Draw nodes
        for layerName, layer in self.layers.iteritems():
            for child in layer.getChildren():
                child.draw()
        return

    def drawDynamicEdge(self):
        if self._dynamicEdge is not None:
            self._dynamicEdge.draw()
        return

    def drawSelectionBox(self):
        # Draw selection rectangle
        if self.selection_rectangle is not None:
            glColor4f(0.8, 0.5, 0.2, 0.2)
            self.drawRect(self.selection_rectangle)
        return


    def draw(self):
        glPushMatrix()

        glTranslate(self.panMatrix[3,0], self.panMatrix[3,1], self.panMatrix[3,2])
        glScale(1.0/self.zoomMatrix[0,0], 1.0/self.zoomMatrix[1,1], 1.0/self.zoomMatrix[2,2])

        self.drawLayers()

        self.drawDynamicEdge()

        self.drawSelectionBox()

        glPopMatrix()
        return


    def getObjectsIntersectingRect(self, rect):

        # recalculate the rect so that its in the form 
        # where width and height are both positive
        baseX = rect.x
        baseY = rect.y
        diffX = baseX + rect.width
        diffY = baseY + rect.height

        minX = min(baseX, diffX)
        minY = min(baseY, diffY)
        maxX = max(baseX, diffX)
        maxY = max(baseY, diffY)
        # rect = (minX, minY, maxX-minX, maxY-minY)
        rect = GraphModule.Rect(minX, minY, maxX-minX, maxY-minY)

        objects = []
        for child in self.nodes + self.edges:
            if child.intersectsRect(rect):
                objects.append(child)
        return objects


    # END class Canvas
    pass




class GlCanvas(Canvas):
    
    ATTRIBUTES = Canvas.ATTRIBUTES + [
        'nodeTable',
    ]

    def __init__(self, parent, width, height, *args, **kwds):

        Canvas.__init__(self)

        self.width = width
        self.height = height

        self.initGL()
        self.initLighting()
        self.initViewport()

        self._frameIsInProcessOfShowing = False
        return

        return

    def resetDrawables(self):
        Canvas.resetDrawables(self)
        self.resetDataToGuiObjectMapping()

        # the check here is because
        # this is also being called in the constructor
        if self.nodeTable() is not None:
            self.nodeTable().clear()
        else:
            self.resetNodeTable()

        return


    def resetDataToGuiObjectMapping(self):
        self._dataToGuiObjectMapping = {}
        return

    def addDataToGuiObjectMapping(self, dataObject, guiObject):
        self._dataToGuiObjectMapping[dataObject] = guiObject
        return

    def getGuiObjectForDataObject(self, dataObject):
        return self._dataToGuiObjectMapping[dataObject]
 


    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.setViewport(width, height)
        return
    
    def initViewport(self):
        return self._initViewport(self.getWidth(), self.getHeight())

    def _initViewport(self, width, height):

        self.setViewport(width, height)
        self.panMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; 0 0 0 0')

        return

    def setViewport(self, width, height):
        # Reset The Current Viewport And Perspective Transformation
        glViewport(0, 0, width, height)		
        self._updateProjection(width, height)
        return

    def initLighting(self):
        return self._initLighting()

    def _initLighting(self):
        return


    def initGL(self):
        import platform
        if platform.system() in ['Linux']:
            glutInit([])
        return self._initGL()


    def _initGL(self):

        glClearDepth (1.0)
        glEnable (GL_DEPTH_TEST)
        # glClearColor (0.0, 0.0, 0.0, 0.0)
        glClearColor (0.6, 0.6, 0.6, 1.0)
        
        glShadeModel (GL_SMOOTH)
        glMatrixMode (GL_PROJECTION)

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Really Nice Perspective Calculations
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST) 

        # Enables Smooth Color Shading
        glShadeModel(GL_SMOOTH)
        # Enables Clearing Of The Depth Buffer
        glClearDepth(1.0)

        # Enables Depth Testing
        glEnable(GL_DEPTH_TEST)

        # The Type Of Depth Test To Do	
        glDepthFunc(GL_LEQUAL)

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        self.updateProjection()

        return


    def Render(self, dc):
        self.SetCurrent()

        self.displayFunc()

        self.SwapBuffers()
        return

    def displayFunc(self):
        return self._displayFunc()

    def _displayFunc(self):
        glDrawBuffer(GL_BACK)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        """main drawing stuff goes here"""
        self.draw()

        self.drawMetaInfo()
        return


    def drawMetaInfo(self):

        x = 30
        y = self.getHeight() - 30
        self.drawFPS(x, y)

        return


    def updateProjection(self):
        return self._updateProjection(self.getWidth(), self.getHeight())


    def _updateProjection(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0.0, width, 0.0, height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return


    def drawFPS(self, x, y):
        return


    def getClickableObjectsAtCanvasCoordinates(self, x, y):
        canvasMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % (x, y))
        worldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(canvasMatrix)
        world_x = worldMatrix[3,0]
        world_y = worldMatrix[3,1]

        point = GraphModule.Point(world_x, world_y)

        for clickable in self.getClickables():
            if clickable.overlaps(point):
                yield clickable
        raise StopIteration


    def getSelectableObjectAtCanvasCoordinates(self, x, y):

        """
        this should instead be a composite filter
        # object is selectable
        # object contains point
        """

        canvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % (x, y))
        worldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(canvasMatrix)
        world_x = worldMatrix[3,0]
        world_y = worldMatrix[3,1]

        point = GraphModule.Point(world_x, world_y)

        for selectable in self.getSelectables():
            if selectable.overlaps(point):
                return selectable

        return None

    def getViewportCoordinatesFromCanvasCoordinates(self, canvasMatrix):
        rotationMatrix = numpy.matrix(
            '1 0 0 0; 0 -1 0 0; 0 0 -1 0; 0 0 0 1')
        translationMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; 0 %s 0 0' % self.getHeight())

        viewportMatrix = (canvasMatrix*rotationMatrix) +translationMatrix
        return viewportMatrix


    def getWorldCoordinatesFromViewportCoordinates(self, viewportMatrix):

        worldMatrix = self.zoomMatrix * (viewportMatrix - self.panMatrix)

        return worldMatrix


    def getWorldCoordinatesFromCanvasCoordinates(self, canvasMatrix):
        viewportMatrix = self.getViewportCoordinatesFromCanvasCoordinates(canvasMatrix)
        worldMatrix = self.getWorldCoordinatesFromViewportCoordinates(viewportMatrix)

        return worldMatrix


    """
    def setSelection(self, selected):

        oldSelection = self._selected
        self._selected = selected

        self.contextManager().selectionChanged(oldSelection, self._selected)

        return
    """

    """
    def addToSelection(self, selected):

        self._selected.extend(selected)

        self.contextManager().selectionChanged([], self._selected)
        pass
    """

    def getSelection(self):
        return self._selected


    def getResourceKeyForNode(self, dataNode):

        # TODO:
        # return the appropriate key
        # for the composite node,
        # e.g. nest, parameter sweep, loop, branch

        if not dataNode.isAtomic():
            generator = TaskModule.getTaskGeneratorForDefinition(dataNode)
            if isinstance(generator, TaskModule.NestTaskGenerator):
                return 'gui nest node class'
            #if isinstance(generator, TaskModule.ParameterSweepTaskGenerator):
            #    return 'gui parameter sweep node class'
            if isinstance(generator, TaskModule.LoopTaskGenerator):
                return 'gui loop node class'
            if isinstance(generator, TaskModule.BranchTaskGenerator):
                return 'gui branch node class'
            pass

        # default to generic node
        return 'gui node class'


    def addNode(self, dataNode, worldMatrix=None):

        resourceKey = self.getResourceKeyForNode(dataNode)
        nodeClass = self.contextManager().app().getResourceValue(
            resourceKey, default=GraphModule.Node)
        
        uiNode = nodeClass(dataNode)
        # need to do this so that the node
        # will have access to app contextual information
        uiNode.contextManager(self.contextManager())
        
        uiNode.setupPrimitives(self.nodePolicy())

        self.addDrawable(uiNode)

        if worldMatrix is None:
            worldMatrix = numpy.matrix('1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1')

        uiNode.setPosition(worldMatrix[3,0], worldMatrix[3,1])

        dataObjectFunction = self.addDataToGuiObjectMapping

        dataObjectFunction(dataNode, uiNode)
        # ports = uiNode.inputPorts.values()+uiNode.outputPorts.values()
        for portDirection, ports in [('input', uiNode.inputPorts.values()),
                                  ('output',uiNode.outputPorts.values())]:
            for port in ports:
                portName = port.name

                # parameters have __eq__ defined
                # such that they are equivalent if their ids are equivalent
                # and since the ids are not unique (and are contextualized)
                # we need to include the context, ie the data node
                dataObjectFunction((dataNode, portName, portDirection), port)

            pass

        return uiNode


    def addEdge(self, dataEdge):
        # find the gui objects
        # for the outputNode, outputPort, inputPort, inputNode
        dataPath = dataEdge.path()

        dataObjectFunction = self.getGuiObjectForDataObject

        guiPath = map(
            dataObjectFunction,
            [
                dataPath[0], # source node
                (dataPath[0], dataPath[1], 'output'), # source port
                (dataPath[-1], dataPath[-2], 'input'), # target port
                dataPath[-1] # target node
            ]
        )

        edgeClass = self.contextManager().app().getResourceValue(
            'gui edge class', default=GraphModule.Edge)

        edge = edgeClass(dataPath, guiPath)
        edge.setupPrimitives(self.edgePolicy())
        self.addDrawable(edge)

        return

    def addDrawable(self, drawable):
        Canvas.addDrawable(self, drawable)

        # is it possible for the code that draws the nodes
        # to simply iterate over the rows of the table?
        if isinstance(drawable, GraphModule.Node):
            logging.debug("adding node %s to self.nodeTable()" % drawable.nodeData.name())
            row = self.nodeTable().addRow()
            row.setColumn('data', drawable.nodeData)
            row.setColumn('gui', drawable)
            pass

        pass


    def removeDrawable(self, drawable):
        if isinstance(drawable, GraphModule.Node):
            filter = RelationModule.ColumnValueFilter(
                'gui',
                FilterModule.IdentityFilter(drawable))
            self.nodeTable().removeRows(filter)
            pass

        Canvas.removeDrawable(self, drawable)
        return


    def computeLayout(self):
        Canvas.computeLayout(self)
        for uiNode in self.nodes:
            dataNode = uiNode.nodeData
            dataNode.guiOptions()['canvas position'] = uiNode.getPosition()
        return




    def resetNodeTable(self):
        table = RelationalModule.createTable(
            'node table',
            ['data', 'gui']
        )
        self.nodeTable(table)
        return

    def _getFilterForDataNode(self, node):
        filter = RelationalModule.ColumnValueFilter(
            'data',
            FilterModule.IdentityFilter(node)
        )
        return filter

    def hasGuiObjectForDataNode(self, node):
        filter = self._getFilterForDataNode(node)
        guiNodes = RelationalModule.Table.reduceRetrieve(
            self.nodeTable(),
            filter,
            ['gui']
        )
        if len(guiNodes) is 0:
            return False
        return True


    def getGuiObjectForDataNode(self, node):
        """
        should be able to use getGuiObjectForDataObject
        """

        filter = self._getFilterForDataNode(node)
        guiNodes = RelationalModule.Table.reduceRetrieve(
            self.nodeTable(),
            filter,
            ['gui']
        )
        if len(guiNodes) is 0:
            raise KeyError('no gui object found for node %s' % node.id())
        if len(guiNodes) is not 1:
            raise ValueError('expected only 1 gui object for node %s' % node.id())
        return guiNodes[0]


    def hasCanvasPosition(self, dataNode):
        guiOptions = dataNode.guiOptions()
        return 'canvas position' in guiOptions
    


    def updateExecutionStatus(self, task):
        # TODO:
        # this needs to handle the case that the task
        # is not pointing to the nest definition 
        # being displayed

        for uiNode in self.nodes:
            dataNode = uiNode.nodeData

            filter = task._getFilterForDefinition(dataNode)
            statusList = RelationalModule.Table.reduceRetrieve(
                task.tasksTable(),
                filter, ['status'], [])

            # update only if there's a status to update
            if not len(statusList):
                continue
            uiNode.updateExecuteStatus(statusList[0])
            pass

        self.updateGL()
        return


    def displayPomset(self, pomsetReferencePath=None):

        shouldComputeLayout = True
        shouldQueryUser = False
        
        # TODO:
        # determine if should query user
        self.resetDrawables()

        if pomsetReferencePath is None:
            pomsetContext, pomsetReferencePath, isEditable = \
                self.contextManager().currentDisplayedPomsetInfo()
            return
        pomsetReference = pomsetReferencePath[-1]
        pomset = pomsetReference.definitionToReference()

        # draw the nodes
        for dataNode in pomset.nodes():
            logging.debug('drawing node %s' % dataNode.name())
            uiNode = self.addNode(dataNode)
            if self.hasCanvasPosition(dataNode):
                shouldComputeLayout = False
                x, y = dataNode.guiOptions()['canvas position']
                uiNode.setPosition(x, y)
            else:
                shouldQueryUser = True
            pass

        # draw the execute status on the nodes
        if self.contextManager().hasTaskForPomsetPath(pomsetReferencePath):
            task = self.contextManager().getTaskForPomsetPath(pomsetReferencePath)
            self.updateExecutionStatus(task)
        
        # draw the edges between the nodes
        notNoneFilter = FilterModule.constructNotFilter()
        notNoneFilter.addFilter(
            RelationalModule.ColumnValueFilter(
                'edge',
                FilterModule.IdentityFilter(None)
            )
            )
        for values in pomset.parameterConnectionPathTable().retrieve(
            # FilterModule.TRUE_FILTER, 
            notNoneFilter,
            ['edge']):
            edge = values[0]
            self.addEdge(edge)
            pass

        # draw the pomset's parameters

        # draw the edges between the pomset's parameters
        # and node parameters

        if shouldQueryUser and not shouldComputeLayout:
            print "should query user for auto arrange"
            # TODO:
            # if user confirms auto-arrange
            # set shouldComputeLayout to True

        # TODO:
        # call computeLayout only if the loaded pomset
        # does not already contain information about node positioning
        # self.computeLayout()
        if shouldComputeLayout:
            self.computeLayout()


        return



    def breadCrumbs(self, value=None):
        if value is not None:
            self._breadCrumbs = value
        if not hasattr(self, '_breadCrumbs'):
            self._breadCrumbs = 'No active pomset to display'
        return self._breadCrumbs


    def setSelection(self, selected):

        for x in self.getSelection():
            x.isSelected(False)
            x.updateDisplay()

        self._selected = selected

        for x in selected:
            x.isSelected(True)
            x.updateDisplay()

        return

    def addToSelection(self, selected):

        self._selected.extend(selected)

        for x in selected:
            x.isSelected(True)
            x.updateDisplay()
        pass


    def drawLine(self, line):
        glBegin(GL_LINE_STRIP)
        for point in line.points:
            glVertex3f(point.x, point.y, point.z)
        glEnd()
        return


    def drawRect(self, rect, filled=True):
        glPushMatrix()
        glTranslatef(rect.x, rect.y, 0)
        if filled:
            glBegin(GL_QUADS)
        else:
            glBegin(GL_LINE_LOOP)
        glVertex2f(0, 0)
        glVertex2f(0, rect.height)
        glVertex2f(rect.width, rect.height)
        glVertex2f(rect.width, 0)
        glEnd()
        glPopMatrix()
        return

    # END class GlCanvas
    pass




class CanvasLayer(object):

    def __init__(self, name):
        self.name = name
        self._children = []
        return

    def addChild(self, child):
        self.getChildren().append(child)
        return

    def removeChild(self, child):
        while child in self.getChildren():
            self.getChildren().remove(child)
        return

    def getChildren(self):
        return self._children


    # END class CanvasLayer
    pass
