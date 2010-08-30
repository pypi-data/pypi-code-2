import logging
import os
import sys
import time

import wx

import currypy

import zgl_graphdrawer.Menu as MenuModule
import zgl_graphdrawer.Node as NodeModule
import zgl_graphdrawer.Port as PortModule

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.context as ContextModule
import pomsets.library as LibraryModule

import pomsets_app.gui.event as EventModule
import pomsets_app.utils as UtilsModule

ID_ACCOUNT_MANAGE = wx.NewId()
ID_ACCOUNTMENU_CONNECT = wx.NewId()
ID_ACCOUNTMENU_DISCONNECT = wx.NewId()
ID_ACCOUNT_CONNECT = wx.NewId()
ID_ACCOUNT_DISCONNECT = wx.NewId()

ID_HADOOP_MANAGE = wx.NewId()

ID_EUCA2OOLS_MANAGE = wx.NewId()

ID_DEFINITIONS_EDIT = wx.NewId()

ID_NODE_ADD = wx.NewId()
ID_NODE_REMOVE = wx.NewId()



class NodeContextualMenu(NodeModule.SelectionContextualMenu):


    def bindEvents(self):

        # should be enabled only if the node has not yet been started
        contextManager = self.canvas.contextManager()
        frame = contextManager.app().GetTopWindow()
        pomsetContext, pomset = frame._currentPomsetInfo
        if not contextManager.hasTaskForPomset(pomsetContext.pomset()):
 
            self.addMenuItem('Edit task', self.OnEditTask)

            # should also add "Edit definition"
            # if the definition is not a library definition
            dataNode = self.objects[0].nodeData
            if not dataNode.definitionToReference().isLibraryDefinition():
                self.addMenuItem('Edit definition', self.OnEditTaskDefinition)

            self.addMenuItem('Delete', self.OnDelete)
            self.addMenuItem('Duplicate', self.OnDuplicate)
        else:
            # TODO:
            # These should be enabled only if the node has executed
            # or errored out
            if len(self.objects) == 1:
                self.addMenuItem('View output messages', 
                                 self.OnViewOutputMessages)

        return

    def OnViewOutputMessages(self, event):
        """
        Assumes that this only got called for a single GUI node
        Currently this assumption is enforced by the node contextual menu
        which only adds the menu item to call this function
        if the selection consists only of the node
        """

        dataNode = self.objects[0].nodeData

        import pypatterns.filter as FilterModule
        import pypatterns.relational as RelationalModule
        filter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(dataNode)
        )
        contextManager = self.canvas.contextManager()

        # get the active pomset
        activePomset = contextManager.activePomset()

        # get the task for the active pomset
        if not contextManager.hasTaskForPomset(activePomset):
            print "no task for active pomset %s found" % activePomset
            return
        rootTask = contextManager.getTaskForPomset(activePomset)

        # from the active pomset task, 
        # get the task for the data node
        if not rootTask.hasChildTaskForDefinition(dataNode):
            print "no task for pomset node %s found" % dataNode
            return
        task = rootTask.getChildTaskForDefinition(dataNode)




        # create a dialog that will display all the outputs
        #res =  wx.xrc.XmlResource(
        #    os.path.join(os.getenv('APP_ROOT'),
        #                 'app', 'resources', 'xrc',
        #                 'task output messages dialog.xrc')
        #)
        resourcePath = contextManager.resourcePath()
        res =  wx.xrc.XmlResource(
            os.path.join(resourcePath, 'xrc', 'task output messages dialog.xrc')
            )

        import pomsets_app.gui.widget.task as WidgetModule
        dialog = WidgetModule.MessageDialog(
            res, self.canvas.GetParent()
        )

        # self.event is the event originating from the contextual menu
        dialog.event = self.event
        dialog.contextManager = self.canvas.app().contextManager()
        dialog.populateTaskTree(task)
        dialog._selectedTask = task
        dialog.updateMessageBox()

        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

        return


    def OnDuplicate(self, event):
        print "should duplicate node"

        contextManager = self.canvas.contextManager()

        frame = self.canvas.app().GetTopWindow()
        pomsetContext, pomset = frame._currentPomsetInfo
        for guiNode in self.objects:
            dataNode = guiNode.nodeData
            copyDataNode = contextManager.pomsetBuilder().copyNode(
                pomset, dataNode)
            copyDataNode.name('copy of ' + dataNode.name())

            # TODO:
            # this should be relative to the gui node
            # rather than hardcoded to 0, 0
            guiOptions = dataNode.guiOptions()
            if 'canvas position' in guiOptions:
                copyGuiOptions = copyDataNode.guiOptions()
                uiNodeSize = guiNode.getBounds()
                x, y = guiOptions['canvas position']
                x = x + uiNodeSize[0]/2
                y = y + uiNodeSize[1]/2
                copyGuiOptions['canvas position'] = (x,y)
            
            guiEvent = EventModule.NodeCreatedEvent(
                object=copyDataNode,
                contextManager=contextManager)
            contextManager.postEvent(guiEvent)
            pass



        return


    def OnDelete(self, event):

        print "in OnDelete"

        if len(self.objects) is 0:
            return

        frame = self.canvas.app().GetTopWindow()
        pomsetContext, pomset = frame._currentPomsetInfo

        contextManager = self.canvas.contextManager()
        for guiNode in self.objects:
            dataNode = guiNode.nodeData
            contextManager.pomsetBuilder().removeNode(
                pomset, dataNode)

        frame.displayPomset(pomsetContext, pomset)
                
        return


    def OnEditTaskDefinition(self, event):
        import pomsets_app.gui.utils as GuiUtilsModule

        if len(self.objects) is 0:
            return

        guiNode = self.objects[0]
        dataNode =guiNode.nodeData
        definitionToEdit = dataNode.definitionToReference()

        GuiUtilsModule.editDefinition(
            self.canvas.app().contextManager(),
            self.canvas.GetParent(), definitionToEdit)
        return


    def OnEditTask(self, event):

        import pomsets_app.gui.utils as GuiUtilsModule

        if len(self.objects) is 0:
            return

        guiNode = self.objects[0]
        dataNode =guiNode.nodeData
        GuiUtilsModule.editReferenceDefinition(
            self.canvas.app().contextManager(),
            self.canvas.GetParent(), dataNode)
            
        return


    # END class NodeContextualMenu
    pass


class CanvasContextualMenu(MenuModule.CanvasContextualMenu):

    def bindEvents(self):

        self.addMenuItem('Auto arrange', self.OnAutoArrange)

        return

    def OnAutoArrange(self, event):

        self.canvas.computeLayout()
        
        return

    # END class CanvasContextualMenu
    pass


class CreateNodeCanvasContextualMenu(CanvasContextualMenu):
    
    def bindEvents(self):
        CanvasContextualMenu.bindEvents(self)

        # TODO:
        # add a separator here

        self.addMenuItem('Create node', self.OnCreateNode)
        # self.addMenuItem('Create nest', self.OnCreateNest)
        # self.addMenuItem('Create loop', self.OnCreateLoop)
        # self.addMenuItem('Create branch', self.OnCreateBranch)
        return

    def OnCreateNode(self, event):

        import pomsets_app.gui.utils as GuiUtilsModule

        GuiUtilsModule.selectDefinitionAndAddNode(
            self.canvas.app().contextManager(),
            self.canvas.app().GetTopWindow(), event)

        return

    # END class CreateNodeCanvasContextualMenu
    pass


class PortContextualMenu(PortModule.SelectionContextualMenu):


    def bindEvents(self):

        # TODO:
        # only allow editing if pomset execution has not started
        self.addMenuItem('Edit value', self.OnEditValue)

        # TODO:
        # this should enabled, but only for files
        # if the viewer is pre-defined, then just open
        # otherwise, need to query user for the viewer
        # possible to use the OS's filew viewer items?
        # self.addMenuItem('View output')

        return

    
    def OnEditValue(self, event):
        
        if len(self.objects) is 0:
            return
        
        import pomsets_app.gui.utils as GuiUtilsModule
        
        port = self.objects[0]
        uiNode = port.node
        dataNode = uiNode.nodeData
        
        # userParameterName is
        # the name of the parameter that the user right clicked to edit
        # it will be displayed to the user in the dialog box
        # it is also used to retrieve the actual parameter 
        # that should be edited
        userParameterName = port.name

        GuiUtilsModule.editReferenceDefinition(
            self.canvas.app().contextManager(),
            self.canvas.GetParent(), dataNode, userParameterName)
        return
    


    # END PortContextualMenu
    pass


class ActivePomsetContextualMenu(wx.Menu, MenuModule.Menu):

    def __init__(self, frame, pomsetData, *args, **kwds):
        wx.Menu.__init__(self)
    
        MenuModule.Menu.__init__(self, *args, **kwds)
    
        self._frame = frame

        if pomsetData is None:
            pomsetData = (None, None)

        self._selectedPomsetContext = pomsetData[0]
        self._selectedPomset = pomsetData[1]

        return

    def bindEvents(self):
        self.addMenuItem('New', self.OnCreate)

        self.addMenuItem('Load', self.OnLoad)

        if self._selectedPomsetContext is not None:
            
            # need a "save" and "save as"
            if self._selectedPomsetContext.url() is not None:
                self.addMenuItem('Save', self.OnSave)

            self.addMenuItem('Save as', self.OnSaveAs)

            self.addMenuItem('Close', self.OnClose)

            pass

        return

    def OnCreate(self, event):

        frame = self._frame
        contextManager = frame.app().contextManager()

        pomset = contextManager.createNewPomset()


        guiEvent = EventModule.PomsetCreatedEvent(
            object=pomset,
            originalEvent=event,
            contextManager=contextManager)
        contextManager.postEvent(guiEvent)

        return


    def OnLoad(self, event):

        # TODO:
        # this code is the same as MenuEventHandler.OnLoadExistingPomset
        # should consolidate

        import pomset_app.gui.utils as GuiModule
        try:
            window = self._frame
            contextManager = window.app().contextManager()

            path = GuiModule.selectPathToLoadPomsetDefinition(
                contextManager, window, 
                title="Select a pomset to load" )

            if path is not None:
                pomsetContext = ContextModule.loadPomset(path=path)

                guiEvent = EventModule.PomsetLoadedEvent(
                    object=pomsetContext,
                    originalEvent=event,
                    path=path,
                    contextManager=contextManager)

                contextManager.postEvent(guiEvent)
        except Exception, e:
            raise

        return


    def OnSave(self, event):
        window = self._frame
        contextManager = window.app().contextManager()

        ContextModule.savePomset(self._selectedPomsetContext)

        guiEvent = EventModule.PomsetSavedEvent(
            object=self._selectedPomsetContext,
            contextManager = contextManager,
            originalEvent=self.event)
        contextManager.postEvent(guiEvent)

        return


    def OnSaveAs(self, event):
        import pomsets_app.gui.utils as GuiUtilsModule
        
        window = self._frame
        contextManager = window.app().contextManager()
        path = GuiUtilsModule.selectPathToSavePomsetDefinition(
            contextManager, window
            )

        if path is not None:
            ContextModule.savePomsetAs(
                self._selectedPomsetContext,
                path)

            guiEvent = EventModule.PomsetSavedEvent(
                object=self._selectedPomsetContext,
                contextManager = contextManager,
                originalEvent=self.event)
            contextManager.postEvent(guiEvent)

        return


    def OnClose(self, event):
        window = self._frame
        contextManager = window.app().contextManager()
        contextManager.closePomset(self._selectedPomsetContext)
        return


    # END class ActivePomsetContextualMenu
    pass


class LibraryDefinitionContextualMenu(wx.Menu, MenuModule.Menu):
    def __init__(self, frame, selectedContext, *args, **kwds):
        wx.Menu.__init__(self)
    
        MenuModule.Menu.__init__(self, *args, **kwds)
    
        self._frame = frame
        self._selectedContext = selectedContext
        return

    def bindEvents(self):
        if self._selectedContext is not None:
            # add the "Delete menu item
            self.addMenuItem('Remove', self.OnRemoveDefinition)

        return

    def OnRemoveDefinition(self, event):

        context = self._selectedContext
        definition = context.pomset()

        frame = self._frame
        contextManager = frame.app().contextManager()
        persistentLibrary = contextManager.persistentLibrary()
        
        # backup the existing library
        UtilsModule.backupLibrary(
            persistentLibrary.bootstrapLoaderDefinitionsDir())
        
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definition)
        )
        
        # remove from transient library
        persistentLibrary.removeDefinition(definitionFilter)
        
        # remove the definition from the file system
        definitionUrl = os.path.sep.join([
                persistentLibrary.bootstrapLoaderDefinitionsDir(),
                definition.url()])

        if not os.path.exists(definitionUrl):
            logging.error('cannot remove definition from url %s' % definitionUrl)
            return
        else:
            os.unlink(definitionUrl)
            
        # save out the new bootstrapper pomset
        # that will not load the just removed pomset
        persistentLibrary.saveBootstrapLoaderPomset()
        
        # update GUI
        frame.populateLibraryDefinitionTreeCtrl()
        frame.populateLoadedDefinitionsPane()
        
        return

    # END class LibraryDefinitionContextualMenu
    pass

class LoadedDefinitionContextualMenu(wx.Menu, MenuModule.Menu):

    def __init__(self, frame, selectedContext, *args, **kwds):
        wx.Menu.__init__(self)
    
        MenuModule.Menu.__init__(self, *args, **kwds)
    
        self._frame = frame
        self._selectedContext = selectedContext
        return

    def bindEvents(self):
        self.addMenuItem('New', self.OnCreateDefinition)
        if self._selectedContext is not None:
            # add the "Edit" menu item
            # add the "Delete menu item
            self.addMenuItem('Edit', self.OnEditDefinition)
            self.addMenuItem('Remove', self.OnRemoveDefinition)

        if self._selectedContext is not None:
            self.AppendSeparator()
            self.addMenuItem('Add to library', self.OnAddDefinitionToLibrary)
            
            # TODO:
            # need a "save" and "save as"
            self.addMenuItem('Save to file', self.OnSaveToFile)
            pass

        self.AppendSeparator()
        self.addMenuItem('Load from file', self.OnLoadFromFile)

        return

    def OnLoadFromFile(self, event):
        frame = self._frame
        contextManager = frame.app().contextManager()
        transientLibrary = contextManager.transientLibrary()

        import pomsets_app.gui.utils as GuiUtilsModule
        try:
            path = GuiUtilsModule.selectPathToLoadPomsetDefinition(
                contextManager, frame,
                title="Select a pomset to load")

            pomsetContext = contextManager.loadExistingPomset(path=path)

            transientLibrary.addPomsetContext(pomsetContext)
            frame.populateLoadedDefinitionsPane()

        except Exception, e:
            logging.error(e)
            raise

        return


    def OnSaveToFile(self, event):
        print "should save definition to file"
        import pomsets_app.gui.utils as GuiUtilsModule
        
        app = self.getApp()
        contextManager = app.contextManager()
        windo = app.GetTopWindow()
        GuiUtilsModule.selectPathToSavePomsetDefinition(
            contextManager, window
            )

        return


    def OnAddDefinitionToLibrary(self, event):

        context = self._selectedContext
        definition = context.pomset()
        frame = self._frame
        contextManager = frame.app().contextManager()
        persistentLibrary = contextManager.persistentLibrary()
        transientLibrary = contextManager.transientLibrary()
        
        # backup the existing library
        UtilsModule.backupLibrary(
            persistentLibrary.bootstrapLoaderDefinitionsDir())
        
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definition)
        )
        
        # remove from transient library
        transientLibrary.removeDefinition(definitionFilter)
        
        # define the url for the definition
        definitionPath = definition.id() + '.pomset'
        definition.url(definitionPath)
        outputDir = persistentLibrary.bootstrapLoaderDefinitionsDir()
        
        # save out the definition
        ContextModule.pickleDefinition(
            os.path.join(outputDir, definitionPath), definition)
        
        # add to persistent library
        definition.isLibraryDefinition(True)
        persistentLibrary.addPomsetContext(context)
        
        # save out the bootstrap loader pomset
        # that will load this definition on the next startup
        persistentLibrary.saveBootstrapLoaderPomset()
        
        # update GUI
        frame.populateLibraryDefinitionTreeCtrl()
        frame.populateLoadedDefinitionsPane()
        
        return

    def OnCreateDefinition(self, event):
        import pomsets_app.gui.utils as GuiUtilsModule
    
        context = GuiUtilsModule.createDefinition(
            self._frame.app().contextManager(), self)
    
        self._frame.populateLoadedDefinitionsPane()
        return

    
    def OnEditDefinition(self, event):
        import pomsets_app.gui.utils as GuiUtilsModule
        try:
            # need to pull the context
            context = self._selectedContext
            GuiUtilsModule.editDefinition(
                self._frame.app().contextManager(), 
                self._frame, context.pomset())
            # need to repopulate
        except ValueError, e:
            raise
        return


    def OnRemoveDefinition(self, event):

        context = self._selectedContext
        definition = context.pomset()

        frame = self._frame
        contextManager = frame.app().contextManager()
        transientLibrary = contextManager.transientLibrary()

        # remove from transient library
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definition)
        )
        transientLibrary.removeDefinition(definitionFilter)

        frame.populateLoadedDefinitionsPane()
        return

    # END class CanvasContextualMenu
    pass
