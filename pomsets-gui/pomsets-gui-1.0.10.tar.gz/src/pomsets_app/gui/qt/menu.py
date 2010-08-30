import functools

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *

import logging
import os
import uuid

import numpy

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.parameter as ParameterModule

import pomsets_app.utils as AppUtilsModule

import pomsets_app.gui.graph as GraphModule

class ContextualMenu(QtGui.QMenu):

    def position(self, value=None):
        if value is not None:
            self._position = value
        if not hasattr(self, '_position'):
            self._position = None
        return self._position

    def selection(self, value=None):
        if value is not None:
            self._selection = value
        if not hasattr(self, '_selection'):
            self._selection = []
        return self._selection

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        if not hasattr(self, '_contextManager'):
            self._contextManager = None
        return self._contextManager


    # END class ContextualMenu
    pass

class CanvasContextualMenu(ContextualMenu):

    def bindEvents(self):
        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()
        pomsetReference = pomsetReferencePath[-1]

        if isEditable and not contextManager.hasTaskForPomsetPath(pomsetReferencePath):
            self.addAction(QString('Create nest'), self.OnCreateNest)

            if pomsetContext is not None:
                self.addSeparator()
                self.addAction(QString('Auto arrange'), self.OnAutoArrange)

        return


    def OnAutoArrange(self):
        canvas = self.contextManager().mainWindow().canvas
        canvas.computeLayout()
        canvas.updateGL()
        return

    def OnCreateNest(self):
        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        pomsetReference = pomsetReferencePath[-1]
        builder = contextManager.pomsetBuilder()

        # query the user for the name of the nest
        nodeName, status = QtGui.QInputDialog.getText(
            contextManager.mainWindow(),
            QString("Create nest:"),
            QString("Name:"))

        # create the node only if the user provided a name
        # and did not cancel the request
        if status:
            nodeName = str(nodeName)
            nestName = 'nest_%s' % uuid.uuid4().hex[:3]
            nestContext = builder.createNewNestPomset(name=nestName)
            nestDefinition = nestContext.pomset()

            contextManager.mainWindow().OnCreateNode(
                pomsetContext, pomsetReference,
                nestDefinition, self.position(),
                name=nodeName)

        return

    # END class CanvasContextualMenu
    pass


class CanvasContextualMenuWithCreateNodeEnabled(CanvasContextualMenu):

    def bindEvents(self):
        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        if isEditable:
            pomsetReference = pomsetReferencePath[-1]
            if pomsetContext is not None and \
                    not contextManager.hasTaskForPomsetPath(pomsetReferencePath):
                self.addAction(QString('Create node'), self.OnCreateNode)
                self.addSeparator()

            CanvasContextualMenu.bindEvents(self)

        return

    def OnCreateNode(self):
        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()
        pomsetReference = pomsetReferencePath[-1]

        # import the modules
        import pomsets_app.gui.qt.select_definition.widget as WidgetModule
        import pomsets_app.gui.qt.select_definition.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(pomsetContext)
        controller.pomsetReference(pomsetReference)
        controller.canvasPosition(self.position())

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return

    # END class CanvasContextualMenuWithCreateNodeEnabled
    pass


class MultipleSelectionContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('Duplicate'), self.OnDuplicate)
        self.addAction(QString('Delete'), self.OnDelete)
        return

    def OnDuplicate(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnDuplicateSelection(self.selection())
        return


    def OnDelete(self):

        contextManager = self.contextManager()
        builder = contextManager.pomsetBuilder()

        contextManager.mainWindow().OnDeleteSelection(self.selection())
        return

    # END class MultipleSelectionContextualMenu
    pass


class NodeContextualMenu(ContextualMenu):

    def bindEvents(self):

        contextManager = self.contextManager()

        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()
        if not contextManager.hasTaskForPomsetPath(pomsetReferencePath):
 
            if isEditable:
                self.addAction(QString('Edit task'), self.OnEditTask)

                # should also add "Edit definition"
                # if the definition is not a library definition
                dataNode = self.selection()[0].nodeData
                if not dataNode.definitionToReference().isLibraryDefinition():
                    self.addAction(QString('Edit definition'), 
                                   self.OnEditTaskDefinition)
                else:
                    self.addAction(QString('View definition'), 
                                   self.OnViewTaskDefinition)

                self.addAction(QString('Duplicate'), self.OnDuplicate)
                self.addAction(QString('Delete'), self.OnDelete)
            else:
                self.addAction(QString('View definition'), 
                               self.OnViewTaskDefinition)
        else:
            # enabled only if the node has executed or errored out
            # and there's only one node selected
            if len(self.selection()) == 1:
                self.addAction(QString('View output messages'), 
                               self.OnViewOutputMessages)

        return


    def OnEditTask(self):

        contextManager = self.contextManager()

        guiNode = self.selection()[0]
        definitionToEdit = guiNode.nodeData

        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        self.contextManager().mainWindow().OnEditTask(
            pomsetContext, definitionToEdit)

        return

    
    def OnViewTaskDefinition(self):
        self.OnDisplayTaskDefinition(False)
        return


    def OnEditTaskDefinition(self):
        self.OnDisplayTaskDefinition(True)
        return


    def OnDisplayTaskDefinition(self, allowEdit):

        contextManager = self.contextManager()

        guiNode = self.selection()[0]
        dataNode = guiNode.nodeData
        definitionToEdit = dataNode.definitionToReference()

        # now determine if the definition is in the transient library
        # or defined internally in the pomset
        # and then get the pomset context associated with that definition
        filter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definitionToEdit))
        library = contextManager.transientLibrary()

        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        if library.hasDefinition(filter):
            contexts = RelationalModule.Table.reduceRetrieve(
                library.definitionTable(), filter, ['context'], [])
            pomsetContext = contexts[0]
            pomsetReferencePath = [pomsetContext.reference()]
            pass
        pomsetReferencePath = pomsetReferencePath + [dataNode]

        allowEdit = allowEdit and isEditable
        self.contextManager().mainWindow().OnDisplayDefinition(
            pomsetContext, pomsetReferencePath, allowEdit=allowEdit)
        return


    def OnDelete(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnDeleteNodes(self.selection())
        return

    def OnDuplicate(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnDuplicateNodes(self.selection())
        return

    def OnViewOutputMessages(self):

        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        # import the modules
        import pomsets_app.gui.qt.task_output.widget as WidgetModule
        import pomsets_app.gui.qt.task_output.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(pomsetContext)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()


        return

    # END class NodeContextualMenu
    pass


class EdgeContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('Disconnect edge'), self.OnDisconnect)
        return

    def OnDisconnect(self):

        contextManager = self.contextManager()
        builder = contextManager.pomsetBuilder()

        canvas = self.contextManager().mainWindow().canvas
        clickables = canvas.getClickableObjectsAtCanvasCoordinates(
            self.position().x(), self.position().y())
        edge = None
        for clickable in clickables:
            if not isinstance(clickable, GraphModule.Edge):
                continue
            edge = clickable
            break
        if edge is None:
            # TODO:
            # should display error box to user
            return

        contextManager.mainWindow().OnDeleteEdges([edge])
        return

    # END class EdgeContextualMenu
    pass


class PortContextualMenu(ContextualMenu):

    def getDataNode(self):
        selected = self.selection()[0]
        dataNode = selected.node.nodeData
        return dataNode

    def getParameter(self):
        dataNode = self.getDataNode()

        selected = self.selection()[0]
        parameterId = selected.name
        parameter = dataNode.getParameter(parameterId)
        return parameter

    def parameterIsData(self):
        parameter = self.getParameter()

        return parameter.portType() == ParameterModule.PORT_TYPE_DATA


    def bindEvents(self):
        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()
        if not isEditable:
            return

        if not self.parameterIsData():
            return

        if isEditable and not contextManager.hasTaskForPomsetPath(pomsetReferencePath):
            self.addAction(QString('Edit value'), self.OnEditValue)

            parameter = self.getParameter()

            # TODO:
            # determine if the parameter has already been exposed
            # if so, there no need to do so
            dataNode = self.getDataNode()
            containingNest = dataNode.graph()
            if containingNest.exposesNodeParameter(dataNode, parameter.id()):
                # add a "Unexpose parameter" menu item instead
                pass
            else:
                self.addSeparator()
                self.addAction(QString('Expose to new parameter on nest'), 
                               self.OnExposeAsNewParameter)

                # if a parameter is a side effect, i.e. output file,
                # or just an output
                # then we can can only expose as a new parameter
                # so don't do anything here
                # otherwise, determine if there are existing exposed parameters
                # and add them as possible choices
                if not (parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT) or 
                        parameter.portDirection()==ParameterModule.PORT_DIRECTION_OUTPUT):

                    filter = FilterModule.constructAndFilter()
                    filter.addFilter(
                        FilterModule.ObjectKeyMatchesFilter(
                            filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_DIRECTION_INPUT),
                            keyFunction=lambda x: x.portDirection()
                            )
                        )

                    notTemporalFilter = FilterModule.constructNotFilter()
                    notTemporalFilter.addFilter(
                        FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL)
                        )
                    filter.addFilter(
                        FilterModule.ObjectKeyMatchesFilter(
                            keyFunction = lambda x: x.portType(),
                            filter = notTemporalFilter
                            )
                        )

                    nest = pomsetReferencePath[-1].definitionToReference()
                    nestParameters = [x for x in nest.getParametersByFilter(filter)]
                    if len(nestParameters) is not 0:
                        submenu = self.addMenu(QString('Connect to existing nest parameter'))
                        for nestParameter in nestParameters:
                            nestParameterName = nestParameter.id()
                            function = functools.partial(self.OnConnectToExistingParameter,
                                                         parameterName=nestParameterName)
                            submenu.addAction(QString(nestParameterName),
                                              function)
                        pass

                    pass
                pass
            pass

        return


    def OnExposeAsNewParameter(self):
        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()
        pomsetReference = pomsetReferencePath[-1]

        dataNode = self.getDataNode()
        selected = self.selection()[0]
        parameterId = selected.name

        # TODO:
        # query the user for name of the exposed parameter
        # query the user for the name of the nest
        exposedParameterId, status = QtGui.QInputDialog.getText(
            contextManager.mainWindow(),
            QString("Expose node \"%s\"'s parameter \"%s\" to nest" % 
                    (dataNode.name(), parameterId)),
            QString("Exposed name:"))

        if status:
            exposedParameterId = str(exposedParameterId)

            logging.debug("exposing node \"%s\"'s parameter \"%s\" to nest as \"%s\"" % (dataNode.name(), parameterId, exposedParameterId))

            contextManager.pomsetBuilder().exposeNodeParameter(
                pomsetReference.definitionToReference(),
                exposedParameterId,
                dataNode, parameterId,
                shouldCreate=True
                )

        return


    def OnConnectToExistingParameter(self, parameterName=None):

        exposedParameterId = parameterName

        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()
        pomsetReference = pomsetReferencePath[-1]

        dataNode = self.getDataNode()
        selected = self.selection()[0]
        parameterId = selected.name

        # TODO:
        # find the exposed parameters that fits
        # the attributes of the selected parameter
        contextManager.pomsetBuilder().exposeNodeParameter(
            pomsetReference.definitionToReference(),
            exposedParameterId,
            dataNode, parameterId,
            shouldCreate=False
            )

        return
    

    def OnEditValue(self):

        contextManager = self.contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        dataNode = self.getDataNode()

        parameter = self.getParameter()
        contextManager.mainWindow().OnEditParameterBinding(
            pomsetContext, dataNode, parameter)

        return

    # END class PortContextualMenu
    pass


class ActivePomsetContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('New'), self.OnCreate)

        self.addAction(QString('Load'), self.OnLoad)

        pomsetContext, pomset = self.selection()
        if pomsetContext is not None:

            self.addAction(QString("Rename"), self.OnRename)

            # need a "save" and "save as"
            if pomsetContext.url() is not None:
                self.addAction(QString('Save'), self.OnSave)

            self.addAction(QString('Save as'), self.OnSaveAs)

            self.addAction(QString('Close'), self.OnClose)

            pass


        return

    def OnRename(self):

        # TODO:
        # get the name from the user
        newName, status = QtGui.QInputDialog.getText(
            self,
            QString("Rename pomset"),
            QString("New name:"))

        if status:
            newName = str(newName)
            if len(newName):
                self.contextManager().mainWindow().OnRenameTopLevelPomset(newName)
        return

    def OnCreate(self):
        self.contextManager().mainWindow().OnCreateNewTopLevelPomset()
        return

    def OnLoad(self):
        self.contextManager().mainWindow().OnLoadTopLevelPomset()
        return

    def OnSave(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(
            context, context.url())
        return

    def OnSaveAs(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(context)
        return

    def OnClose(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnCloseActivePomset(self.selection()[0])

        return

    # END class ActivePomsetContextualMenu
    pass


class LibraryDefinitionContextualMenu(ContextualMenu):
    
    def bindEvents(self):

        pomsetContext, pomset = self.selection()
        if pomsetContext is not None:
            self.addAction('View', self.OnViewDefinition)
            # add the "Delete menu item
            self.addAction('Remove', self.OnRemoveDefinition)
            
        return

    def OnViewDefinition(self):
        pomsetContext, pomsetReference = self.selection()
        contextManager = self.contextManager()
        contextManager.mainWindow().OnDisplayDefinition(
            pomsetContext, [pomsetReference], allowEdit=False)
        return


    def OnRemoveDefinition(self):
        """
        TODO: move this out of the menu
        """

        pomsetContext, pomsetReference = self.selection()
        pomset = pomsetReference.definitionToReference()
        contextManager = self.contextManager()


        persistentLibrary = contextManager.persistentLibrary()
        
        # backup the existing library
        AppUtilsModule.backupLibrary(
            persistentLibrary.bootstrapLoaderDefinitionsDir())
        
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(pomset)
        )
        
        # remove from transient library
        persistentLibrary.removeDefinition(definitionFilter)
        
        # remove the definition from the file system
        definitionUrl = os.path.sep.join([
                persistentLibrary.bootstrapLoaderDefinitionsDir(),
                pomset.url()])

        if not os.path.exists(definitionUrl):
            logging.error('cannot remove definition from url %s' % definitionUrl)
            return
        else:
            os.unlink(definitionUrl)
            
        # save out the new bootstrapper pomset
        # that will not load the just removed pomset
        persistentLibrary.saveBootstrapLoaderPomset()

        contextManager.mainWindow().OnDefinitionRemoved(
            persistentLibrary, pomsetContext)

        return


    # END class LibraryDefinitionContextualMenu
    pass



class LoadedDefinitionContextualMenu(ContextualMenu):


    def bindEvents(self):
        self.addAction(QString('New'), self.OnCreateAtomicDefinition)
        # self.addAction(QString('New nest'), self.OnCreateNestDefinition)

        pomsetContext, pomset = self.selection()

        if pomsetContext is not None:
            # add the "Edit" menu item
            # add the "Delete menu item
            self.addAction(QString('Edit'), self.OnEditDefinition)
            self.addAction(QString('Remove'), self.OnRemoveDefinition)

            self.addSeparator()
            self.addAction(QString('Add to library'), self.OnAddDefinitionToLibrary)
            
            # TODO:
            # need a "save" and "save as"
            self.addAction(QString('Save'), self.OnSave)
            self.addAction(QString('Save as'), self.OnSaveAs)
            pass

        self.addSeparator()
        self.addAction(QString('Load from file'), self.OnLoadFromFile)

        return

    def OnCreateAtomicDefinition(self):
        self.contextManager().mainWindow().OnCreateNewAtomicPomset()
        return

    def OnCreateNestDefinition(self):
        # self.contextManager().mainWindow().OnCreateNewNestPomset()
        print "should create new nest pomset"
        return

    def OnEditDefinition(self):
        pomsetContext, pomsetReference = self.selection()
        self.contextManager().mainWindow().OnDisplayDefinition(
            pomsetContext, [pomsetReference], allowEdit=True)
        return


    def OnRemoveDefinition(self):

        pomsetContext, pomsetReference = self.selection()
        pomset = pomsetReference.definitionToReference()

        contextManager = self.contextManager()
        transientLibrary = contextManager.transientLibrary()


        # remove from transient library
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(pomset)
        )
        transientLibrary.removeDefinition(definitionFilter)

        contextManager.mainWindow().OnDefinitionRemoved(
            transientLibrary, pomsetContext)
        return


    def OnAddDefinitionToLibrary(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnMoveDefinitionToLibrary(context)
        return

    def OnSave(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(
            context, context.url())
        return

    def OnSaveAs(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(context)
        return

    def OnLoadFromFile(self):
        contextManager = self.contextManager()
        transientLibrary = contextManager.transientLibrary()

        filter = FilterModule.ObjectKeyMatchesFilter(
            filter = FilterModule.IdentityFilter(True),
            keyFunction = lambda x: x.pomset().isAtomic()
            )
        contextManager.mainWindow().OnLoadPomsetIntoLibrary(
            transientLibrary, filter=filter)
        return

    # END class LoadedDefinitionContextualMenu
    pass
