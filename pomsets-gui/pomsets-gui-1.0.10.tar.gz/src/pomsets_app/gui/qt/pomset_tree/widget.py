from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

class PomsetTreeWidget(QtGui.QTreeWidget):

    def __init__(self, *args, **kwds):
        QtGui.QTreeWidget.__init__(self, *args, **kwds)
        self.setColumnCount(1)
        
        # hide the header
        self.setHeaderLabels([''])
        self.setHeaderHidden(True)

        # enable the contextual menu
        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint&)'), self.OnContextMenu)

        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        return

    def shouldEnableDragToCanvas(self, value=None):
        if value is not None:
            self._shouldEnableDragToCanvas = value
        if not hasattr(self, '_shouldEnableDragToCanvas'):
            self._shouldEnableDragToCanvas = False
        return self._shouldEnableDragToCanvas


    def mouseDoubleClickCallback(self, value=None):
        if value is not None:
            self._mouseDoubleClickCallback = value
        if not hasattr(self, '_mouseDoubleClickCallback'):
            self._mouseDoubleClickCallback = None
        return self._mouseDoubleClickCallback


    def shouldShowInternals(self, value=None):
        if value is not None:
            self._shouldShowInternals = value
        if not hasattr(self, '_shouldShowInternals'):
            self._shouldShowInternals = False
        return self._shouldShowInternals


    def contextualMenuClass(self, value=None):
        if value is not None:
            self._contextualMenuClass = value
        if not hasattr(self, '_contextualMenuClass'):
            self._contextualMenuClass = False
        return self._contextualMenuClass


    def shouldIndicateModified(self, value=None):
        if value is not None:
            self._shouldIndicateModified = value
        if not hasattr(self, '_shouldIndicateModified'):
            self._shouldIndicateModified = False
        return self._shouldIndicateModified

    def dragSelection(self, value=None):
        if value is not None:
            self._dragSelection = value
        if not hasattr(self, '_dragSelection'):
            self._dragSelection = (None, None)
        return self._dragSelection


    def shouldExpand(self, value=None):
        if value is not None:
            self._shouldExpand = value
        if not hasattr(self, '_shouldExpand'):
            self._shouldExpand = False
        return self._shouldExpand


    def pomsetLibrary(self, value=None):
        if value is not None:
            self._pomsetLibrary = value
        if not hasattr(self, '_pomsetLibrary'):
            self._pomsetLibrary = None
        return self._pomsetLibrary

    def pomsetFilter(self, value=None):
        if value is not None:
            self._pomsetFilter = value
        if not hasattr(self, '_pomsetFilter'):
            self._pomsetFilter = FilterModule.TRUE_FILTER
        return self._pomsetFilter

    def selectedPomsetContext(self, value=None):
        if value is not None:
            self._selectedPomsetContext = value
        if not hasattr(self, '_selectedPomsetContext'):
            self._selectedPomsetContext = None
        return self._selectedPomsetContext

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        if not hasattr(self, '_contextManager'):
            self._contextManager = None
        return self._contextManager

    def emptyDataSourceString(self, value=None):
        if value is not None:
            self._emptyDataSourceString = value
        if not hasattr(self, '_emptyDataSourceString'):
            self._emptyDataSourceString = 'None'
        return self._emptyDataSourceString


    def addTreeNode(self, parentWidget, pomsetContext, 
                    name = None,
                    node = None, 
                    recursive=False):

        if name is None and node is not None:
            name = node.name()
            if not name or not len(name):
                name = 'Anonymous'

        isRoot = parentWidget is self
        if isRoot and self.shouldIndicateModified() and \
                pomsetContext is not None and \
                pomsetContext.isModified():
            name = name + ' (modified)'
            pass

        item = QtGui.QTreeWidgetItem([name])
        item.setData(0, Qt.UserRole, (pomsetContext, node))
        if isRoot:
            parentWidget.addTopLevelItem(item)
        else:
            parentWidget.addChild(item)

        if node:
            definitionToReference = node.definitionToReference()
            if recursive and not definitionToReference.isAtomic():
                for childNode in definitionToReference.nodes():
                    self.addTreeNode(item, pomsetContext, 
                                   name = childNode.name(),
                                   node = childNode,
                                   recursive=recursive)

        return

    def populate(self):
        self.clear()

        definitionTable = self.pomsetLibrary().definitionTable()
        pomsetContexts = RelationalModule.Table.reduceRetrieve(
            definitionTable,
            self.pomsetFilter(), ['context'], [])
        if len(pomsetContexts) is 0:
            # TODO:
            # add an empty item
            # with label being self.emptyDataSourceString()
            self.addTreeNode(self, None, name=self.emptyDataSourceString(),
                             node=None, recursive=False)
            pass
        else:
            for pomsetContext in pomsetContexts:

                # add pomsetContext to tree view
                # also check if self.shouldShowInternals()
                # if so, then recursively add 
                self.addTreeNode(self, pomsetContext,
                                 node=pomsetContext.reference(),
                                 recursive=self.shouldShowInternals())
                pass
            pass

        # TODO:
        # set the selection
        self.selectPomsetContext(self.selectedPomsetContext())
            
        if self.shouldExpand():
            self.expandAll()
        return



    def selectPomsetContext(self, pomsetContext):
        self.selectedPomsetContext(pomsetContext)
        return


    def mouseDoubleClickEvent(self, event):
        cb = self.mouseDoubleClickCallback()
        if cb is not None:
            cb(event)
        return


    def displayPomset(self, event, frame=None):
        item = self.itemAt(event.pos())
        if item:
            pomsetContext, pomsetReference = \
                item.data(0, Qt.UserRole).toPyObject()
            pomset = pomsetReference.definitionToReference()
            if pomsetContext is not None and not pomset.isAtomic():
                frame.app().contextManager().activePomsetContext(pomsetContext)

                # determine the path
                # using the tree widget items
                currentItem = item
                itemPath = [currentItem]
                while True:
                    parent = currentItem.parent()
                    if not isinstance(parent, QtGui.QTreeWidgetItem):
                        break
                    currentItem = parent
                    itemPath.insert(0, currentItem)
                    pass

                # extract the pomset path
                pomsetReferencePath = [
                    x.data(0, Qt.UserRole).toPyObject()[1]
                    for x in itemPath]

                frame.displayPomset(pomsetContext, pomsetReferencePath)
                frame.canvas.OnRefresh()
        return


    def mousePressEvent(self, event):

        buttons = event.buttons()
        keyModifiers = event.modifiers()
        if buttons == Qt.LeftButton:

            if self.shouldEnableDragToCanvas():
                item = self.itemAt(event.pos())
                if item:
                    pomsetContext, pomset = \
                        item.data(0, Qt.UserRole).toPyObject()
                    if pomsetContext is not None:
                        self.dragSelection((pomsetContext, pomset))
                pass

            # need to do this
            # because the tree view will not select something
            # if you're just clicking.  you have to 
            # move the mouse so that it has a rect to select
            self.setSelection(QRect(event.pos(), QSize(1,1)),
                              QtGui.QItemSelectionModel.SelectCurrent)

            pass

        event.ignore()
        return


    def mouseReleaseEvent(self, event):

        if self.shouldEnableDragToCanvas():
            self.OnDragToCanvas(event)

        # reset the drag selection
        self._dragSelection = (None, None)

        return


    def OnDragToCanvas(self, event):
        """
        NOTE:
        event.pos() is relative to the widget
        canvas.contentRect() is relative the canvas
        """

        pomsetContext, pomsetReference = self.dragSelection()
        if pomsetReference is None:
            return
        pomset = pomsetReference.definitionToReference()

        contextManager = self.contextManager()

        # TODO:
        # instead of doing nothing,
        # should query the user to see if they want to create a new context
        # and if so, continue 

        # TODO:
        # this check here should be extracted into something like
        # if contextManager.hasActivePomsetContext() and
        #      not contextManager.hasTaskForPomset(activePomsetContext.reference())
        displayedPomsetContext, displayedPomsetReferencePath, displayedIsEditable = \
            contextManager.currentDisplayedPomsetInfo()


        if displayedPomsetContext is None:
            # there's no active pomset to modify
            return

        if not displayedIsEditable:
            # not editable, so should not add
            return

        if contextManager.hasTaskForPomsetPath(displayedPomsetReferencePath):
            # execution has already started, so should not add
            return

        displayedPomsetReference = displayedPomsetReferencePath[-1]

        canvas = contextManager.canvas
        canvasLocalRect = canvas.contentsRect()

        # compute the canvas' position globally
        canvasScreenPosition = canvas.mapToGlobal(QPoint(0,0))
        canvasScreenRect = canvasLocalRect.translated(canvasScreenPosition)

        eventLocalPos = event.pos()
        eventScreenPos = self.mapToGlobal(eventLocalPos)
        eventCanvasPos = canvas.mapFromGlobal(eventScreenPos)
        
        if canvasScreenRect.contains(eventScreenPos):

            self.emit(
                SIGNAL("OnCreateNode(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,QPoint)"), 
                displayedPomsetContext, displayedPomsetReference, 
                pomset, eventCanvasPos)

            pass

        return


    def OnContextMenu(self, point):
        
        menuClass = self.contextualMenuClass()
        popupMenu = menuClass(self)

        item = self.itemAt(point)
        if item:
            pomsetContext, pomset = \
                item.data(0, Qt.UserRole).toPyObject()
            popupMenu.selection((pomsetContext, pomset))
        else:
            popupMenu.selection((None, None))

        popupMenu.position(point)
        popupMenu.contextManager(self.contextManager())

        popupMenu.bindEvents()
        popupMenu.popup(self.mapToGlobal(point))

        return


    def OnRefresh(self, *args, **kwds):
        self.populate()
        return

    # END class PomsetTreeWidget
    pass
