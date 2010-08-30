import currypy
import logging
import os
import sys
import threadpool
import time

import StringIO

import wx
import wx.lib.newevent
import wx.xrc

import numpy

import zgl_graphdrawer.Event as EventModule
import zgl_graphdrawer.Node as NodeModule

import pypatterns.filter as FilterModule

import pomsets.command as CommandModule
import pomsets.context as ContextModule
import pomsets.parameter as ParameterModule
import pomsets.task as TaskModule

import cloudpool.environment as ExecuteEnvironmentModule
import cloudpool.shell as ShellModule

import pypatterns.relational as RelationalModule

# Custom event classes
# http://wiki.wxpython.org/CustomEventClasses
PomsetCreatedEvent, EVT_POMSET_CREATED = wx.lib.newevent.NewEvent()
PomsetLoadedEvent, EVT_POMSET_LOADED = wx.lib.newevent.NewEvent()
PomsetClosedEvent, EVT_POMSET_CLOSED = wx.lib.newevent.NewEvent()
PomsetSavedEvent, EVT_POMSET_SAVED = wx.lib.newevent.NewEvent()
NodeCreatedEvent, EVT_NODE_CREATED = wx.lib.newevent.NewEvent()
NodeRemovedEvent, EVT_NODE_REMOVED = wx.lib.newevent.NewEvent()
EdgeCreatedEvent, EVT_EDGE_CREATED = wx.lib.newevent.NewEvent()
EdgeRemovedEvent, EVT_EDGE_REMOVED = wx.lib.newevent.NewEvent()

CommandExecutionFailedEvent, EVT_COMMAND_EXECUTION_FAILED = wx.lib.newevent.NewEvent()

NodeRenamedEvent, EVT_NODE_RENAMED = wx.lib.newevent.NewEvent()
DefinitionValuesChangedEvent, EVT_DEFINITION_VALUES_CHANGED = wx.lib.newevent.NewEvent()
TaskValuesChangedEvent, EVT_TASK_VALUES_CHANGED = wx.lib.newevent.NewEvent()
ParameterModifiedEvent, EVT_PARAMETER_MODIFIED = wx.lib.newevent.NewEvent()
ParameterCreatedEvent, EVT_PARAMETER_CREATED = wx.lib.newevent.NewEvent()
ParameterDeletedEvent, EVT_PARAMETER_DELETED = wx.lib.newevent.NewEvent()

TaskStatusChangedEvent, EVT_TASK_STATUS_CHANGED = wx.lib.newevent.NewEvent()

class CanvasEventHandler(EventModule.CanvasEventHandler):

    def bindEvents(self):
        self.Bind(EVT_POMSET_CREATED, self.OnPomsetCreated)
        self.Bind(EVT_POMSET_LOADED, self.OnPomsetLoaded)
        self.Bind(EVT_POMSET_CLOSED, self.OnPomsetClosed)
        self.Bind(EVT_POMSET_SAVED, self.OnPomsetSaved)
        self.Bind(EVT_NODE_CREATED, self.OnNodeCreated)
        self.Bind(EVT_NODE_RENAMED, self.OnNodeRenamed)
        self.Bind(EVT_NODE_REMOVED, self.OnNodeRemoved)
        self.Bind(EVT_EDGE_CREATED, self.OnEdgeCreated)
        self.Bind(EVT_EDGE_REMOVED, self.OnEdgeRemoved)

        self.Bind(EVT_DEFINITION_VALUES_CHANGED, self.OnDefinitionValuesChanged)
        self.Bind(EVT_TASK_VALUES_CHANGED, self.OnTaskValuesChanged)
        self.Bind(EVT_PARAMETER_MODIFIED, self.OnParameterModified)
        self.Bind(EVT_PARAMETER_CREATED, self.OnParameterCreated)
        self.Bind(EVT_PARAMETER_DELETED, self.OnParameterDeleted)

        self.Bind(EVT_TASK_STATUS_CHANGED, self.OnTaskStatusChanged)
        
        EventModule.CanvasEventHandler.bindEvents(self)
        return


    def OnPomsetSaved(self, event):

        contextManager = event.contextManager

        app = contextManager.app()
        frame = app.GetTopWindow()

        frame.populateActivePomsetTreeCtrl()        
        return


    def OnPomsetCreated(self, event):

        contextManager = event.contextManager
        app = contextManager.app()
        frame = app.GetTopWindow()

        pomsetContext = event.object

        contextManager.addActivePomsetContext(pomsetContext)

        contextManager.activePomsetContext(pomsetContext)
        frame.displayPomset(pomsetContext)

        return

    
    def OnPomsetClosed(self, event):

        canvas = self.eventSource()
        pomset = event.object
        contextManager = event.contextManager

        # TODO:
        # this should be an event
        canvas.resetDrawables()

        app = contextManager.app()
        frame = app.GetTopWindow()

        activeContext = contextManager.activePomsetContext()
        frame.displayPomset(activeContext)

        frame.populateActivePomsetTreeCtrl()        
        
        return

    
    def OnPomsetLoaded(self, event):
        
        canvas = self.eventSource()
        pomsetContext = event.object
        contextManager = event.contextManager
        path = event.path

        contextManager.addActivePomsetContext(pomsetContext)
        contextManager.activePomsetContext(pomsetContext)
        
        app = contextManager.app()
        frame = app.GetTopWindow()
        frame.displayPomset(pomsetContext)
        
        return


    def OnNodeCreated(self, event):
        
        # TODO:
        # do we need to ensure that the node
        # being is in the current active pomset?
        
        canvas = self.eventSource()

        dataNode = event.object


        uiNode = canvas.addNode(dataNode)
        uiNodeSize = uiNode.getBounds()


        # TODO:
        # consolidate code for setting
        # node position using canvas position
        
        guiOptions = dataNode.guiOptions()
        if hasattr(event, 'position'):
            position = event.position
            canvasMatrix = numpy.matrix(
                '1 0 0 0; 0 1 0 0; 0 0 1 0; %s %s 0 1' % 
                (position[0] - uiNodeSize[0]/2.0,
                 position[1] + uiNodeSize[1]/2.0)
            )
            worldMatrix = canvas.getWorldCoordinatesFromCanvasCoordinates(
                canvasMatrix)

            position = (worldMatrix[3,0], worldMatrix[3,1])

            guiOptions['canvas position'] = position
            pass
        else:
            # TODO:
            # this should be at the center of the canvas
            # instead of hardcoded to (0, 0)
            position = guiOptions.get('canvas position', (0, 0))

        uiNode.setPosition(*position)
        

        contextManager = event.contextManager
        contextManager.activePomsetContext().isModified(True)
        
        # now force the frame to move
        # so that the canvas will resize correctly
        app = contextManager.app()
        frame = app.GetTopWindow()
        # frame.resizeCanvas()

        frame.populateActivePomsetTreeCtrl()

        return



    def OnEdgeCreated(self, event):

        # TODO:
        # extract this into a function that can add 
        # an arbitrary edge into the canvas
        canvas = self.eventSource()
        path = event.path
        canvas.addEdge(path)
        return


    def OnEdgeRemoved(self, event):
        canvas = self.eventSource()
        edge = canvas.getGuiObjectForDataObject(event.object)
        canvas.removeDrawable(edge)
        return


    def OnDefinitionValuesChanged(self, event):
        """
        If the parameter ordering got changed
        the we may need to re-order the parameters in the canvas
        """
        print "%s OnDefinitionValuesChanged" % self.__class__
        return


    
    
    def OnTaskStatusChanged(self, event):
        # update the status
        event.node.updateExecuteStatus(event.status)
        # rebuild primitives
        event.node._children = event.node._buildChildren()
        return

    
    def OnTaskValuesChanged(self, event):
        print "%s OnTaskValuesChanged" % self.__class__
        return
    

    def OnParameterCreated(self, event):
        print "%s OnParameterCreated" % self.__class__
        return

    def OnParameterDeleted(self, event):
        print "%s OnParameterDeleted" % self.__class__
        return

    def OnParameterModified(self, event):
        # need to check whether a node 
        definition = event.definition

        generator = TaskModule.getTaskGeneratorForDefinition(definition)
        isParameterSweep = isinstance(
            generator, TaskModule.ParameterSweepTaskGenerator)

        canvas = self.eventSource()
        node = canvas.getGuiObjectForDataNode(definition)
        node.setImageParameterSweep(isParameterSweep)        
        return


    def OnNodeRemoved(self, event):
        canvas = self.eventSource()
        node = canvas.getGuiObjectForDataNode(event.object)
        canvas.removeDrawable(node)
        return


    def OnNodeRenamed(self, event):
        # rebuild primitives

        canvas = self.eventSource()
        node = canvas.getGuiObjectForDataNode(event.node)

        nameLabel = node.createNamePrimitive(canvas.nodePolicy())
        node.parts[NodeModule.Node.PART_LABEL] = nameLabel

        node._children = node._buildChildren()

        # if a node got renamed,
        # then the pomset context is modified
        contextManager = canvas.contextManager()
        contextManager.activePomsetContext().isModified(True)
        app = contextManager.app()
        frame = app.GetTopWindow()
        frame.populateActivePomsetTreeCtrl()

        return
    
    def OnPomsetEvent(self, event):
        print "need to respond to pomset event"
        return


    # END class CanvasEventHandler
    pass



class MenuEventHandler(wx.EvtHandler, EventModule.EventHandler):

    def __init__(self, eventSource):
        wx.EvtHandler.__init__(self)
        self.eventSource(eventSource)
        return

    def getApp(self):
        return self.eventSource().app()

    def bindEvents(self):
        import pomsets_app.gui.menu as MenuModule
        import pomsets_app.controller.automaton as AutomatonModule

        # file
        wx.EVT_MENU(self, wx.ID_NEW, self.OnCreateNewPomset)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnLoadExistingPomset)
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSaveCurrentPomset)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveCurrentPomsetAs)
        wx.EVT_MENU(self, wx.ID_CLOSE, self.OnCloseCurrentPomset)

        #wx.EVT_MENU(self, MenuModule.ID_DEFINITIONS_EDIT, 
        #            self.OnEditDefinitionList)
        # wx.EVT_MENU(self, MenuModule.ID_NODE_ADD, self.OnAddNode)
        #wx.EVT_MENU(self, MenuModule.ID_NODE_REMOVE, self.OnRemoveNodes)

        # execute
        wx.EVT_MENU(self, AutomatonModule.ID_EXECUTE_LOCAL, self.OnExecutePomset)
        wx.EVT_MENU(self, AutomatonModule.ID_EXECUTE_REMOTE, self.OnExecutePomset)
        wx.EVT_MENU(self, AutomatonModule.ID_EXECUTE_EUCA2OOLS, self.OnExecutePomset)
        wx.EVT_MENU(self, AutomatonModule.ID_EXECUTE_PREVIEW, 
                    self.OnPreviewExecution)

        # connections
        #wx.EVT_MENU(self, MenuModule.ID_CONNECTION_MANAGE, self.OnManageConnections)
        #wx.EVT_MENU(self, MenuModule.ID_CONNECTION_CONNECT, self.OnConnect)
        #wx.EVT_MENU(self, MenuModule.ID_CONNECTION_DISCONNECT, self.OnDisconnect)
        wx.EVT_MENU(self, MenuModule.ID_ACCOUNT_MANAGE, self.OnDisplayVirtualMachines)
        wx.EVT_MENU(self, MenuModule.ID_HADOOP_MANAGE, self.OnManageHadoop)
        wx.EVT_MENU(self, MenuModule.ID_EUCA2OOLS_MANAGE, 
                    self.OnManageEC2Credentials)


        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAboutApplication)
        # wx.EVT_MENU(self, wx.ID_EXIT, self.OnExitApplication)
        return

    def OnUnknownAction(self, event):
        print "unknown action"
        return

    def OnMenuItem(self, event):
        menuId = event.GetMenuId()
        actionId = MenuEventHandler.MENU_EVENTS.get(menuId, 'OnUnknownAction')
        action = getattr(self, actionId)
        return action(event)

    def OnPreviewExecution(self, event):

        contextManager = self.getApp().contextManager()

        parent = self.eventSource()
        #res =  wx.xrc.XmlResource(
        #    '%s/app/resources/xrc/execution preview dialog.xrc' % os.getenv('APP_ROOT'))
        resourcePath = contextManager.resourcePath()
        res =  wx.xrc.XmlResource(
            os.path.join(resourcePath, 'xrc', 'execution preview dialog.xrc')
            )


        import pomsets_app.gui.widget.task as WidgetModule
        dialog = WidgetModule.ExecutionPreviewDialog(res, parent)

        stream = StringIO.StringIO()

        contextManager.outputCommandsToStream(stream)
        dialog.populateTextCtrl(stream.getvalue())
        # TODO:
        # should ensure that we wait only 
        # for the specific thread that's running the preview
        # and not for threads running other pomsets
        # in the case where we have multiple active pomsets
        # contextManager.automaton().threadpool().wait()

        # TODO: 
        # should provide the above with a callback
        # that will update the textCtrl
        # when the execution/printing has completed


        # event is the event originating from the contextual menu
        # self.event is the event
        # dialog.populateTextCtrl(value)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

        return


    def OnDisplayVirtualMachines(self, event):

        contextManager = self.getApp().contextManager()

        automaton = contextManager.automaton()

        dataModel = automaton.virtualMachineTable()

        parent = self.eventSource()

        
        import pomsets_app.gui.widget.eucalyptus as WidgetModule
        vmWindow = WidgetModule.VirtualMachineWindow(
            parent,
            automaton,
            WidgetModule.ID_DIALOG_VIRTUALMACHINES,
            "Virtual machines",
            dataModel
        )
        # event is the event originating from the contextual menu
        # self.event is the event
        vmWindow.contextManager = contextManager
        vmWindow.populateData()

        vmWindow.Show()
        return


    def OnManageHadoop(self, event):
        contextManager = self.getApp().contextManager()

        parent = self.eventSource()
        import pomsets_app.gui.utils as GuiUtilsModule
        GuiUtilsModule.manageHadoopConfiguration(contextManager, parent)

        return

    def OnCreateNewDefinition(self, event):
        raise NotImplementedError('not implemented OnCreateNewDefinition')



    def OnEditDefinitionList(self, event):
        contextManager = self.getApp().contextManager()
        parent = self.eventSource()

        import pomsets_app.gui.utils as GuiUtilsModule
        GuiUtilsModule.editDefinitionList(contextManager, parent)
        return


    def OnAddNode(self, event):
        raise NotImplementedError('not implemented OnAddNode')

    def OnRemoveNodes(self, event):
        raise NotImplementedError('not implemented self.OnRemoveNodes')


    def OnManageEC2Credentials(self, event):

        contextManager = self.getApp().contextManager()
        parent = self.eventSource()


        import pomsets_app.gui.utils as GuiUtilsModule
        GuiUtilsModule.manageEc2Credentials(contextManager, parent)

        return


    def OnExecutePomset(self, event):

        import menu as MenuModule

        app = self.getApp()
        contextManager = app.contextManager()

        executionEnvId = event.GetId()

        try:
            import pomsets.command as ExecuteCommandModule
            commandBuilder = ExecuteCommandModule.CommandBuilder(
                ExecuteCommandModule.buildCommandFunction_commandlineArgs
            )
            commandBuilderMap = {
                'shell process':commandBuilder
            }

            # TODO:
            # is there a way to figure out env here,
            # rather than using executionEnvId
            
            requestKwds = contextManager.generateRequestKwds(
                executeEnvironmentId = executionEnvId,
                commandBuilderMap = commandBuilderMap)


            # TODO:
            # need to determine 

            contextManager.executePomset(
                pomset=contextManager.activePomset(), 
                requestKwds=requestKwds)

        except Exception, e:
            logging.error("error executing pomset >> %s" % e)
            
            # post an event about the failure
            failEvent = CommandExecutionFailedEvent(
                object=contextManager.activePomset(),
                exception=e,
                originalEvent=event)
            contextManager.postEvent(failEvent)
            pass
        finally:
            # update the execute menu items
            # i.e. disable execution for this pomset
            # now that execution has happened
            contextManager.app().GetTopWindow().updateExecuteMenus()
            

        return



    def OnCreateNewPomset(self, event):

        # TODO:
        # verify that there are no unsaved edits

        contextManager = self.getApp().contextManager()
        pomsetContext = contextManager.createNewPomset()

        guiEvent = PomsetCreatedEvent(
            object=pomsetContext,
            originalEvent=event,
            contextManager=contextManager)
        contextManager.postEvent(guiEvent)

        return


    def OnLoadExistingPomset(self, event):

        # TODO:
        # this code is the same as MenuEventHandler.OnLoadExistingPomset
        # should consolidate

        import pomsets_app.gui.utils as GuiUtilsModule
        try:
            window = self.eventSource()
            contextManager = self.getApp().contextManager()

            path = GuiUtilsModule.selectPathToLoadPomsetDefinition(
                contextManager, window, 
                title="Select a pomset to load" )

            if path is not None:
                pomsetContext = ContextModule.loadPomset(path=path)

                guiEvent = PomsetLoadedEvent(
                    object=pomsetContext,
                    originalEvent=event,
                    path=path,
                    contextManager=contextManager)

                contextManager.postEvent(guiEvent)

        except Exception, e:
            raise

        return


    def OnSaveCurrentPomset(self, event):

        # if the current pomset was loaded from file
        # then save back out to the same file

        # otherwise, treat this as a "save as"

        app = self.getApp()
        contextManager = app.contextManager()

        ContextModule.savePomset(contextManager.activePomsetContext())

        guiEvent = PomsetSavedEvent(
            object=contextManager.activePomsetContext(),
            contextManager = contextManager,
            originalEvent=self.event)
        contextManager.postEvent(guiEvent)

        return


    def OnSaveCurrentPomsetAs(self, event):

        import pomsets_app.gui.utils as GuiUtilsModule
        
        app = self.getApp()
        contextManager = app.contextManager()
        window = app.GetTopWindow()
        path = GuiUtilsModule.selectPathToSavePomsetDefinition(
            contextManager, window
            )

        if path is not None:
            ContextModule.savePomsetAs(
                contextManager.activePomsetContext(), 
                path)

            guiEvent = PomsetSavedEvent(
                object=contextManager.activePomsetContext(),
                contextManager = contextManager,
                originalEvent=self.event)
            contextManager.postEvent(guiEvent)

        return


    def OnCloseCurrentPomset(self, event):

        contextManager = self.getApp().contextManager()
        contextManager.closeActivePomset()

        return

    #def OnExitApplication(self, event):
    #    print "exiting application"
    #    return

    def OnAboutApplication(self, event):
        print "about application"
        import pomsets_app.gui.utils as GuiUtilsModule
        contextManager = self.getApp().contextManager()
        GuiUtilsModule.showAboutDialog(contextManager)
        return




    # END class MenuEventHandler
    pass


class MouseEventHandler(EventModule.MouseEventHandler):

    def OnLeftMouseButtonUpDefault(self, event):

        EventModule.MouseEventHandler.OnLeftMouseButtonUpDefault(self, event)

        contextManager = self.contextManager()
        frame = contextManager.app().GetTopWindow()

        # if the start of the drag
        # was from the library definitions (or loaded definitions)
        # then create a new node
        if hasattr(frame, 'dragSelection') and \
           frame.dragSelection is not None:

            frame.processDragSelection(event)

            pass


        return

    # END class MouseEventHandler
    pass

