import math
import numpy

import OpenGL
from OpenGL.GL import *

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *


import pomsets_app.gui.canvas as CanvasModule
import pomsets_app.gui.graph as GraphModule




class Canvas(QGLWidget, CanvasModule.GlCanvas):

    ATTRIBUTES = CanvasModule.GlCanvas.ATTRIBUTES + []

    MODE_MOUSE_NONE = 0
    MODE_MOUSE_PAN = 1
    MODE_MOUSE_ZOOM = 2
    MODE_MOUSE_MOVE_OBJECTS = 3
    MODE_MOUSE_SELECTION_BOX = 4
    MODE_MOUSE_CREATE_EDGE = 5

    def __init__(self, parent, width, height, *args, **kwds):
        QGLWidget.__init__(self, parent)
        CanvasModule.GlCanvas.__init__(self, parent, width, height, 
                                       *args, **kwds)
        self.setMinimumSize(600, 400)

        # we want mouse tracking
        # so that we can get tooltips
        self.setMouseTracking(True)

        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint&)'), self.OnContextMenu)

        self.textureMap = {}

        self.setAcceptDrops(True)
        return


    def setCurrentContextModified(self):
        self.contextManager().currentDisplayedPomsetInfo()[0].isModified(True)
        return


    def mouseMoveMode(self, value=None):
        if value is not None:
            self._mouseMoveMode = value
        if not hasattr(self, '_mouseMoveMode'):
            self._mouseMoveMode = Canvas.MODE_MOUSE_NONE
        return self._mouseMoveMode

    def isCurrentlyDrawing(self, value=None):
        if value is not None:
            self._isCurrentlyDrawing = value
        if not hasattr(self, '_isCurrentlyDrawing'):
            self._isCurrentlyDrawing = False
        return self._isCurrentlyDrawing


    def getWidth(self):
        return QGLWidget.width(self)
    
    def getHeight(self):
        return QGLWidget.height(self)
    

    def initGL(self):
        # override the superclass's implementation
        # so that the GL initialization is not done in the constructor
        return


    def initializeGL(self):
        # call the superclass's actual GL initialization
        return self._initGL()


    def initViewport(self):
        # override the superclass's implementation
        # so that GL viewport initialization is not called by default
        return


    def resizeGL(self, w, h):
        # call the superclass's implementation
        # for recomputing the viewport upon resizing
        return self.resize(w, h)

    def resize(self, w, h):
        QGLWidget.resize(self, w, h)
        CanvasModule.GlCanvas.resize(self, w, h)
        

    def displayFunc(self):
        # override the superclass's implementation
        # so that GL drawing is not called by default
        return


    def paintGL(self):
        # handle re-entrancy
        if self.isCurrentlyDrawing():
            return
        self.isCurrentlyDrawing(True)
        
        # call the superclass's implementation
        # for doing the actual GL drawing
        returnVal =  self._displayFunc()

        self.isCurrentlyDrawing(False)
        return returnVal

    def OnContextMenu(self, point):

        clickedObjects = [
            x for x in 
            self.getClickableObjectsAtCanvasCoordinates(point.x(), point.y())]
        clickedObject = None
        if len(clickedObjects) is not 0:
            clickedObject = clickedObjects[0]
           
        selection = self.getSelection()[:]

        if clickedObject is None:
            pass
        elif len(selection) is 0 or not clickedObject in selection:
            selection = [clickedObject]

        import pomsets_app.gui.qt.menu as MenuModule

        # create a new popup menu
        if len(selection) is 0:
            menuClass = self.contextManager().app().getResourceValue(
                'canvas contextual menu class', 
                MenuModule.CanvasContextualMenu)
            popupMenu = menuClass(self)
            pass
        else:
            # get the contextual menu
            # from the most recent item selected
            isMultiple = any(
                [isinstance(x, GraphModule.Edge) for x in selection]) and \
                any([isinstance(x, GraphModule.Node) for x in selection])
            
            if isMultiple:
                menuClass = MenuModule.MultipleSelectionContextualMenu
                pass
            elif isinstance(selection[-1], GraphModule.Node):
                menuClass = self.contextManager().app().getResourceValue(
                    'node contextual menu class',
                    MenuModule.NodeContextualMenu)
            elif isinstance(selection[-1], GraphModule.Port):
                menuClass = self.contextManager().app().getResourceValue(
                    'port contextual menu class',
                    MenuModule.PortContextualMenu)
            elif isinstance(selection[-1], GraphModule.Edge):
                menuClass = self.contextManager().app().getResourceValue(
                    'port contextual menu class',
                    MenuModule.EdgeContextualMenu)

            popupMenu = menuClass(self)
            popupMenu.selection(selection)
            pass

        popupMenu.position(point)
        popupMenu.contextManager(self.contextManager())

        popupMenu.bindEvents()
        popupMenu.popup(self.mapToGlobal(point))

        return


    def dragMoveEvent(self, event):
        print "should process dragMoveEvent"
        return

    def dropEvent(self, event):
        print "should process dropEvent"
        return


    def mouseDoubleClickEvent(self, event):

        buttons = event.buttons()

        if buttons == Qt.LeftButton:
            eventX = event.x()
            eventY = event.y()
            clickedObjects = [
                x for x in 
                self.getClickableObjectsAtCanvasCoordinates(eventX, eventY)]
            if len(clickedObjects) is 0:
                return

            clickedNodes = [x for x in clickedObjects
                            if isinstance(x, GraphModule.Node)]
            clickedPorts = [x for x in clickedObjects
                            if isinstance(x, GraphModule.Port)]

            contextManager = self.contextManager()
            pomsetContext, pomsetReferencePath, isEditable = \
                contextManager.currentDisplayedPomsetInfo()

            if len(clickedNodes):
                # only do something if it's a nest
                clickedNode = clickedNodes[0]
                dataNode = clickedNode.nodeData
                if not dataNode.definitionToReference().isAtomic():
                    self.contextManager().mainWindow().displayPomset(
                        pomsetContext, 
                        pomsetReferencePath=pomsetReferencePath+[dataNode])
                pass
            elif len(clickedPorts):
                clickedPort = clickedPorts[0]

                dataNode = clickedPort.node.nodeData
                parameterId = clickedPort.name
                parameter = dataNode.getParameter(parameterId)

                # we don't want to allow users to edit 
                # bindings to temporal parameters
                # because bindings on them are pointless
                import pomsets.parameter as ParameterModule
                if parameter.portType() == ParameterModule.PORT_TYPE_DATA:
                    contextManager.mainWindow().OnEditParameterBinding(
                        pomsetContext, dataNode, parameter)
                pass

        return


    def mouseMoveEvent(self, event):
        buttons = event.buttons()
        keyModifiers = event.modifiers()
        mouseMoveMode= self.mouseMoveMode()

        if mouseMoveMode == Canvas.MODE_MOUSE_PAN:
            # should pan
            self.OnPanViewPort(event)
            pass
        elif mouseMoveMode == Canvas.MODE_MOUSE_ZOOM:
            # should zoom
            self.OnZoomViewPort(event)
            pass
        elif mouseMoveMode == Canvas.MODE_MOUSE_SELECTION_BOX:
            # should update the selection box
            self.OnSelectionBoundingBox(event)
            pass
        elif mouseMoveMode == Canvas.MODE_MOUSE_MOVE_OBJECTS:
            # should update the node positions
            self.OnMoveNodes(event)
            pass
        elif mouseMoveMode == Canvas.MODE_MOUSE_CREATE_EDGE:
            # should update the dynamic edge
            self.OnComputeDynamicEdge(event)
            pass

        self.updateGL()

        return


    def mouseReleaseEvent(self, event):

        mouseMoveMode = self.mouseMoveMode()
        if mouseMoveMode == Canvas.MODE_MOUSE_NONE:
            # process a drag selection from somewhere else
            pass
        elif mouseMoveMode == Canvas.MODE_MOUSE_SELECTION_BOX:
            # remove dynamic objects
            self.selection_rectangle = None
            pass
        elif mouseMoveMode == Canvas.MODE_MOUSE_CREATE_EDGE:
            # should create edge
            self.OnCreateEdge(event)
            pass

        self.mouseMoveMode(Canvas.MODE_MOUSE_NONE)
        self.updateGL()
        return


    def mousePressEvent(self, event):
        """
        Note: no need to handle contextual menu here
        """

        """
        Note: On Mac OS X, the ControlModifier value corresponds to the Command keys on the Macintosh keyboard, and the MetaModifier value corresponds to the Control keys.

Qt.NoModifier	0x00000000	No modifier key is pressed.
Qt.ShiftModifier	0x02000000	A Shift key on the keyboard is pressed.
Qt.ControlModifier	0x04000000	A Ctrl key on the keyboard is pressed.
Qt.AltModifier	0x08000000	An Alt key on the keyboard is pressed.
Qt.MetaModifier	0x10000000	A Meta key on the keyboard is pressed.
Qt.KeypadModifier	0x20000000	A keypad button is pressed.
Qt.GroupSwitchModifier	0x40000000	X11 only. A Mode_switch key on the keyboard is pressed.
        """

        eventX = event.x()
        eventY = event.y()

        buttons = event.buttons()
        keyModifiers = event.modifiers()


        self.baseMousePosition = event.pos()

        if buttons == Qt.LeftButton:

            if keyModifiers == Qt.AltModifier:
                # configure for pan
                self.initialPanMatrix = self.panMatrix
                self.mouseMoveMode(Canvas.MODE_MOUSE_PAN)
            elif keyModifiers == Qt.ShiftModifier:
                # configure for zoom
                self.initialZoomMatrix = self.zoomMatrix
                self.mouseMoveMode(Canvas.MODE_MOUSE_ZOOM)
                pass
            elif keyModifiers == Qt.ControlModifier:
                # should add to selection
                # this is the Command key on macs

                clickedObjects = [
                    x for x in 
                    self.getClickableObjectsAtCanvasCoordinates(eventX, eventY)
                    if x.isSelectable()]

                if len(clickedObjects) is 0:
                    self.initialSelection = self.getSelection()
                    self.mouseMoveMode(Canvas.MODE_MOUSE_SELECTION_BOX)
                #elif isinstance(clickedObject, GraphModule.Edge):
                #    self.mouseMoveMode(Canvas.MODE_MOUSE_CREATE_EDGE)
                else:
                    clickedObject = clickedObjects[0]
                    if clickedObject.isSelectable():
                        self.mouseMoveMode(Canvas.MODE_MOUSE_MOVE_OBJECTS)
                        self.addToSelection(clickedObjects)
                        for selected in self.getSelection():
                            if isinstance(selected, GraphModule.Edge):
                                continue
                            selected.initialX = selected.x
                            selected.initialY = selected.y
                pass
            elif keyModifiers == Qt.NoModifier:
                # should reset selection
                # and just select this object

                clickedObjects = [
                    x for x in self.getClickableObjectsAtCanvasCoordinates(eventX, eventY)]

                if len(clickedObjects) and \
                        isinstance(clickedObjects[0], GraphModule.Port):
                    self.mouseMoveMode(Canvas.MODE_MOUSE_CREATE_EDGE)
                    self.initialPort = clickedObjects[0]
                else:
                    newSelection = [x for x in clickedObjects 
                                    if x.isSelectable()]
                    if len(newSelection) is 0:
                        self.initialSelection = []
                        self.setSelection(newSelection)
                        self.mouseMoveMode(Canvas.MODE_MOUSE_SELECTION_BOX)
                    else:
                        self.mouseMoveMode(Canvas.MODE_MOUSE_MOVE_OBJECTS)
                        self.setSelection(newSelection)
                        for selected in self.getSelection():
                            if isinstance(selected, GraphModule.Edge):
                                continue
                            selected.initialX = selected.x
                            selected.initialY = selected.y

                    pass

                pass

            # attempt to select
            pass
        

        pass



    def computeMouseMoveInCanvas(self, initialPosition, finalPosition):

        initialMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % 
                                     (initialPosition.x(), initialPosition.y()))
        finalMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % 
                                   (finalPosition.x(), finalPosition.y()))

        return finalMatrix - initialMatrix


    def computeMouseMoveInWorld(self, initialPosition, finalPosition):
        baseCanvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
            (initialPosition.x(), initialPosition.y()))
        baseWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(
            baseCanvasMatrix)

        newCanvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
            (finalPosition.x(), finalPosition.y()))
        newWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(
            newCanvasMatrix)

        deltaMatrix = newWorldMatrix - baseWorldMatrix
        return deltaMatrix


    def OnZoomViewPort(self, event):
        delta = self.computeMouseMoveInCanvas(
            self.baseMousePosition, event.pos())

        delta_zoom = -0.005 * delta[3,0]

        newZoomFactor = min(max(
                self.initialZoomMatrix[0,0]+delta_zoom,0.5),10.0)

        newZoomMatrix = numpy.matrix(
            '%s 0 0 0; 0 %s 0 0; 0 0 %s 0; 0 0 0 %s' %
            (newZoomFactor, newZoomFactor, newZoomFactor, newZoomFactor))
        
        self.zoomMatrix = newZoomMatrix
        return

    def OnPanViewPort(self, event):
        deltaMatrix = self.computeMouseMoveInWorld(
            self.baseMousePosition, event.pos())

        self.panMatrix = deltaMatrix + self.initialPanMatrix
        return


    def OnMoveNodes(self, event):
        worldDeltaMatrix = self.computeMouseMoveInWorld(
            self.baseMousePosition, event.pos())

        delta = (worldDeltaMatrix[3,0], worldDeltaMatrix[3,1])

        for selected in self.getSelection():
            if isinstance(selected, GraphModule.Edge):
                continue
            x = selected.initialX + delta[0]
            y = selected.initialY + delta[1]
            selected.setPosition(x, y)
            dataNode = selected.nodeData
            guiOptions = dataNode.guiOptions()
            guiOptions['canvas position'] = (x,y)
            pass


        edgesToProcess = filter(
            lambda x: x.inputNode() in self.getSelection() or x.outputNode() in self.getSelection(),
            self.edges
        )
        map(lambda x: x.setupPrimitives(self.edgePolicy()), edgesToProcess)


        # emit this signal so that the active pomsets library
        # will know to update that the context has been modified
        self.setCurrentContextModified()
        self.emit(SIGNAL("OnNodesMoved()"))

        return


    def OnSelectionBoundingBox(self, event):

        deltaMatrix = self.computeMouseMoveInWorld(
            self.baseMousePosition, event.pos())

        baseCanvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
            (self.baseMousePosition.x(), self.baseMousePosition.y()))
        baseWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(
            baseCanvasMatrix)

        rect = GraphModule.Rect(
            baseWorldMatrix[3,0], baseWorldMatrix[3,1],
            deltaMatrix[3,0], deltaMatrix[3,1]
            )
        self.selection_rectangle = rect

        objectsInBoundBox = self.getObjectsIntersectingRect(
            self.selection_rectangle)

        self.setSelection(self.initialSelection + 
                          [x for x in objectsInBoundBox if x.isSelectable()])

        return


    def OnCreateEdge(self, event):

        contextManager = self.contextManager()

        clickReleaseObjects = [
            x for x in self.getClickableObjectsAtCanvasCoordinates(
            event.x(), event.y())
            if isinstance(x, GraphModule.Port)]
        clickReleaseObject = None
        if len(clickReleaseObjects) is not 0:
            clickReleaseObject = clickReleaseObjects[0]

        edge = None
        if clickReleaseObject is not None and \
           contextManager.canConnect(self.initialPort, clickReleaseObject):
            edge = contextManager.connect(self.initialPort, clickReleaseObject)

            # add the gui edge
            self.addEdge(edge)

            self.setCurrentContextModified()
            self.emit(SIGNAL("OnEdgeCreated(PyQt_PyObject)"), edge)

            pass

        # reset the dynamic edge
        # (because there won't be one anymore)
        self._dynamicEdge = None
        self._initialPort = None
        
        return


    def OnComputeDynamicEdge(self, event):
        self.computeDynamicEdge(
            GraphModule.Point(self.baseMousePosition.x(),
                              self.baseMousePosition.y()),
            GraphModule.Point(event.pos().x(), event.pos().y()))
        self._dynamicEdge.isDynamic(True)
        return


    def drawLayers(self):
        """
        This is copied over from the base class
        """
        # Draw nodes
        for layerName, layer in self.layers.iteritems():
            for child in layer.getChildren():
                if isinstance(child, GraphModule.Node):
                    self.drawNode(child)
                    continue
                if isinstance(child, GraphModule.Edge):
                    self.drawEdge(child)
                    continue
                child.draw()
        return


    def getEdgeWidth(self, baseWidth):
        # min width 1, max width 5
        width = max(1, 
                    min(int(1.0*baseWidth / self.zoomMatrix[0,0]), 
                        baseWidth))
        return width

    def drawEdge(self, edge):
        glLineWidth(self.getEdgeWidth(edge.getWidth()))

        # TODO:
        # should set the color
        visualPolicy = self.visualPolicy()
        color = edge.getColor()
        glColor4f(*color)

        if not hasattr(edge, 'children'):
            edge.setupPrimitives(self.edgePolicy())

        self.drawLine(edge.children[0])

        glLineWidth(1)
        return

    def drawDynamicEdge(self):
        # TODO:
        # consolidate the code with drawEdge
        if self._dynamicEdge is not None:
            self.drawEdge(self._dynamicEdge)
            pass
        return

    def drawNode(self, node):

        if node.shouldUpdateDisplay():
            node.updateDisplay()
            node.shouldUpdateDisplay(False)

        glPushMatrix()
        glTranslate(node.x, node.y, 0)

        for nodePrimitive in node.partPrimitives():
            if not nodePrimitive.visible():
                continue

            if isinstance(nodePrimitive, GraphModule.Rect):
                self.drawRect(nodePrimitive)
                continue

            if isinstance(nodePrimitive, GraphModule.Text):
                self.drawText(nodePrimitive)
                continue

            if isinstance(nodePrimitive, GraphModule.Port):
                self.drawPort(nodePrimitive)
                continue

            nodePrimitive.draw()
            
        glPopMatrix()
        return


    def drawPort(self, port):
        glPushMatrix()
        glTranslate(port.x, port.y, 0)

        for child in port.children:
            if isinstance(child, GraphModule.Rect):
                glColor4f(*child.borderColor)
                self.drawRect(child, filled=child.filled())
                continue
            if isinstance(child, GraphModule.Circle):
                glColor4f(*child.borderColor)
                self.drawCircle(child)
                continue

            child.draw()

        glPopMatrix()
        return
    


    def drawText(self, primitive):
        color = primitive.color
        color[3] = color[3] * primitive.alpha
        glColor4f(*color)

        fontDb = self.contextManager().app()._fontDb
        fontSize = int(18.0 / self.zoomMatrix[0,0])

        # TODO:
        # this should use the visual policy instead
        font = fontDb.font('FreeUniversal', 'Normal', 18)

        zoom = self.zoomMatrix[0, 0]

        fontMetrics = QtGui.QFontMetrics(font)
        rect = fontMetrics.boundingRect(primitive.text)
        
        offsetX = primitive.position[0] + (primitive.size[0]-rect.width())/2
        offsetY = primitive.position[1] + (primitive.size[1]-rect.height())/2

        font = fontDb.font('FreeUniversal', 'Normal', fontSize)
        self.renderText(offsetX, offsetY, 0,
                        primitive.text,
                        font)
        return


    def drawCircle(self, circle, *args, **kwds):

        # we want at least 8 wedges
        # and for now, a max 
        smoothness = max(8, circle.size[0])
        smoothness = min(smoothness, 360)
        
        x = circle.size[0]/2.0
        y = circle.size[1]/2.0
        radius = circle.radius
            
        glBegin(GL_LINE_LOOP)
        for i in range(0, smoothness):    
            angle = i * math.pi * 2.0 / smoothness
            glVertex2f(x + radius * math.cos(angle), 
                       y + radius * math.sin(angle))
        glEnd() 

        return



    def drawRect(self, rect, *args, **kwds):
        if hasattr(rect, 'use_texture') and rect.use_texture:
            textureFile = rect._texture_image_file
            if not textureFile in self.textureMap:
                image = QtGui.QImage(textureFile)
                textureId = self.bindTexture(image)
                self.textureMap[textureFile] = (textureId, image)
            else:
                textureId, image = self.textureMap[textureFile]
                pass

            # NOTE:
            # this is a hack to get the PS image drawing
            # TODO:
            # find a better solution

            # cache the value so that it does not get changed
            shouldTranslate = False
            if hasattr(rect, 'offsetPosition'):
                shouldTranslate=True

            if shouldTranslate:
                glPushMatrix()
                glTranslate(*rect.offsetPosition)

            textureRect = QRectF(0.0, 0.0, rect.width, rect.height)
            self.drawTexture(textureRect, textureId)

            if shouldTranslate:
                glPopMatrix()

        elif isinstance(rect, GraphModule.Rect):
            CanvasModule.GlCanvas.drawRect(self, rect, *args, **kwds)
            pass
        else:
            rect.draw()
        return


    def OnRefresh(self):
        pomsetContext, pomsetReferencePath, isEditable = \
            self.contextManager().currentDisplayedPomsetInfo()

        self.displayPomset(pomsetReferencePath)

        self.updateGL()
        return


    def OnNodesDuplicated(self, nodeMap):
        for nodeCopy, originalNode in nodeMap.iteritems():
            # TODO:
            # this should be relative to the gui node
            # rather than hardcoded to 0, 0
            guiOptions = originalNode.guiOptions()
            if 'canvas position' in guiOptions:
                copyGuiOptions = nodeCopy.guiOptions()
                x, y = guiOptions['canvas position']
                x = x + 25
                y = y - 25
                copyGuiOptions['canvas position'] = (x,y)
            pass

        # rebuild the gui objects
        pomsetContext, pomsetReferencePath, isEditable = \
            self.contextManager().currentDisplayedPomsetInfo()
        self.displayPomset(pomsetReferencePath)

        # update the selection to the duplicated objects
        guiNodes = map(self.getGuiObjectForDataNode, nodeMap.keys())
        self.setSelection(guiNodes)

        # redraw
        self.updateGL()
        return


    def OnNodeCreated(self, node, pos):
        uiNode = self.addNode(node)
        uiNodeSize = uiNode.getBounds()

        canvasMatrix = numpy.matrix(
            '1 0 0 0; 0 1 0 0; 0 0 1 0; %s %s 0 1' % 
            (pos.x() - uiNodeSize[0]/2.0,
             pos.y() + uiNodeSize[1]/2.0)
        )
        worldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(
            canvasMatrix)

        position = (worldMatrix[3,0], worldMatrix[3,1])
        guiOptions = node.guiOptions()
        guiOptions['canvas position'] = position
        uiNode.setPosition(*position)

        self.updateGL()
        return




    def drawMetaInfo(self):
        
        CanvasModule.GlCanvas.drawMetaInfo(self)

        # draw breadcrumbs
        x = 30
        y = self.height - 30
        glColor3f(1.0, 1.0, 1.0)
        fontSize = 12
        fontDb = self.contextManager().app()._fontDb
        font = fontDb.font('Arial', 'Normal', fontSize)
        self.renderText(x, y, 0,
                        ">>> " + self.breadCrumbs(),
                        font)
        return


    def getScaledPosition(self, rawPosition):
        positionString = ' '.join([str(x) for x in rawPosition+[0]])
        rawPositionMatrix = numpy.matrix(positionString)
        scaledPositionMatrix = rawPositionMatrix / self.zoomMatrix
        return [scaledPositionMatrix[0,0],
                scaledPositionMatrix[1,1],
                scaledPositionMatrix[2,2]]
        

    def event(self, event):
        if event.type() == QEvent.ToolTip:
            position = event.pos()

            clickedObjects = [
                x for x in 
                self.getClickableObjectsAtCanvasCoordinates(
                    position.x(), position.y())]

            clickedObject = None
            if len(clickedObjects) is not 0:
                clickedObject = clickedObjects[0]
                if not isinstance(clickedObject, GraphModule.Port):
                    clickedObject = None
                pass

            if clickedObject is not None:
                QtGui.QToolTip.showText(event.globalPos(),
                                        clickedObject.name)
            else:
                QtGui.QToolTip.hideText()
                event.ignore()
            return True
        return QGLWidget.event(self, event)

    # END class Canvas
    pass



