import wx
import wx.lib.agw.foldpanelbar

import zgl_graphdrawer.Application as ApplicationModule
import zgl_graphdrawer.Frame as zglFrameModule

import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.gui.event as EventModule
import pomsets_app.gui.canvas as CanvasModule
import pomsets_app.gui.menu as MenuModule

import pomsets.definition as DefinitionModule
import pomsets.library as LibraryModule

import pomsets_app.gui.frame as FrameModule

class WxFrame(zglFrameModule.wxFrame, FrameModule.Frame):

    FBP_MIN_WIDTH = 200
    
    def __init__(self, app, *args, **kwds):
        zglFrameModule.wxFrame.__init__(self, *args, **kwds)
        self.app(app)

        self.layoutContent()
        self.Centre()
        
        self.bindEvents()
        
        pass

    def displayPomset(self, pomsetContext, pomset=None):
        FrameModule.Frame.displayPomset(self, pomsetContext, pomset=pomset)

        # need to call this to force the canvas to update
        self.resizeCanvas()

        # update the fold panel menu
        # TODO: each of these should be able to update
        #       when events are fired instead
        self.populateActivePomsetTreeCtrl()
        self.populateLibraryDefinitionTreeCtrl()
        self.populateLoadedDefinitionsPane()

        self.updatePomsetMenu()
        return

    def bindEvents(self):
        zglFrameModule.wxFrame.bindEvents(self)

        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnSplitterReposition)

        self.currentActivePomsetTreeCtrl.Bind(
            wx.EVT_LEFT_DOWN, self.OnFbpLeftMouseDown)
        self.currentActivePomsetTreeCtrl.Bind(
            wx.EVT_LEFT_DCLICK, self.OnFbpLeftMouseDoubleClick)
        self.currentActivePomsetTreeCtrl.Bind(
            wx.EVT_RIGHT_DOWN, self.OnActivePomsetsPaneRightMouseDown)
        
        self.libraryDefinitionTreeCtrl.Bind(
            wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDragDefinitionTreeCtrl)
        self.libraryDefinitionTreeCtrl.Bind(
            wx.EVT_LEFT_DOWN, self.OnFbpLeftMouseDown)
        self.libraryDefinitionTreeCtrl.Bind(
            wx.EVT_RIGHT_DOWN, self.OnLibraryDefinitionPaneRightMouseDown)
        
        self.loadedDefinitionTreeCtrl.Bind(
            wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDragDefinitionTreeCtrl)
        self.loadedDefinitionTreeCtrl.Bind(
            wx.EVT_LEFT_DOWN, self.OnFbpLeftMouseDown)
        self.loadedDefinitionTreeCtrl.Bind(
            wx.EVT_RIGHT_DOWN, self.OnLoadedDefinitionPaneRightMouseDown)
        
        self.Bind(EventModule.EVT_DEFINITION_VALUES_CHANGED, 
                  self.OnDefinitionValuesChanged)

        import platform
        if platform.system() in ['Darwin']:
            print "calling wx.App.SetMacExitMenuItemId(wx.ID_EXIT)"
            wx.App.SetMacExitMenuItemId(wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.OnExitApplication)
        return
    
    def OnExitApplication(self, event):

        # first check whether there are any modified pomsets
        # if so, query the user as to whether 
        contextManager = self.app().contextManager()

        shouldQueryUser = any(
            [x.isModified() 
             for x in contextManager.activePomsetContexts()])

        import sys
        shouldExit = True
        if shouldQueryUser:
            shouldExit = False

            resourcePath = contextManager.resourcePath()
            res =  wx.xrc.XmlResource(
                os.path.join(resourcePath, 'xrc', 'verify exit application.xrc'))

            import pomsets_app.gui.wx.widget.application as WidgetModule
            dialog = WidgetModule.VerifyExitDialog(res, self)

            try:
                if dialog.ShowModal() == wx.ID_OK:
                    shouldExit = True
                    pass
                pass
            except Exception, e:
                # if any errors, should exit
                sys.exit(1)
                raise
            finally:
                dialog.Destroy()
            pass


        if shouldExit:
            sys.exit(0)

        return
    

    
    
    def layoutContent(self):
        self.createApplicationMenus()
        
        splitter = wx.SplitterWindow(self, -1)
        self.splitter = splitter
        
        self._updateActivePomsetTreeCtrlSelection = True

        foldPanelBar = self.initializeFoldPanel(splitter)
        canvas = self.initializeCanvas(splitter)
        
        # need to set this so that we can update the canvas 
        # for the callbacks later on
        self.canvas = canvas
        canvas.app = lambda: self.app()

        splitter.SplitVertically(foldPanelBar, canvas, Frame.FBP_MIN_WIDTH)
 
        pass

    
    def initializeCanvas(self, parent):
        canvas = CanvasModule.Canvas(parent, 
                                  ApplicationModule.DEFAULT_WIDTH,
                                  ApplicationModule.DEFAULT_HEIGHT,
                                  style=wx.FULL_REPAINT_ON_RESIZE)
        canvas.resetDrawables()
        return canvas
    
    
    def initializeFoldPanel(self, parent):
        
        foldPanelBar = wx.lib.agw.foldpanelbar.FoldPanelBar(parent, -1)
        
        item = foldPanelBar.AddFoldPanel("Active pomsets", True)
        currentActivePomsetTreeCtrl = wx.TreeCtrl(
            item, wx.ID_ANY, style=wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.TR_HAS_BUTTONS)
        foldPanelBar.AddFoldPanelWindow(
            item, currentActivePomsetTreeCtrl)
        self.currentActivePomsetTreeCtrl = currentActivePomsetTreeCtrl
        self.populateActivePomsetTreeCtrl()
        # need to do this ensure that 
        # the treectrl is drawn correctly
        foldPanelBar.Collapse(item)
        foldPanelBar.Expand(item)        
        
        item = foldPanelBar.AddFoldPanel("Library definitions", True)
        libraryDefinitionTreeCtrl = wx.TreeCtrl(
            item, wx.ID_ANY, style=wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.TR_HAS_BUTTONS)
        foldPanelBar.AddFoldPanelWindow(item, libraryDefinitionTreeCtrl)
        self.libraryDefinitionTreeCtrl = libraryDefinitionTreeCtrl
        self.populateLibraryDefinitionTreeCtrl()
        # need to do this ensure that 
        # the treectrl is drawn correctly
        foldPanelBar.Collapse(item)
        foldPanelBar.Expand(item)

        
        item = foldPanelBar.AddFoldPanel("Loaded definitions", True)
        loadedDefinitionsPane = self.buildLoadedDefinitionsPane(item)
        foldPanelBar.AddFoldPanelWindow(item, loadedDefinitionsPane)
        # need to do this ensure that 
        # the treectrl is drawn correctly
        foldPanelBar.Collapse(item)
        foldPanelBar.Expand(item)

        
        # TODO:
        # add stuff for 
        # - eucalyptus/amazon aws
        # - celery
        # - hadoop
        item = foldPanelBar.AddFoldPanel("Application configuration", True)

        return foldPanelBar

    
    def buildLoadedDefinitionsPane(self, parent):
        
        import pomsets_app.gui.widget as WidgetModule
        
        contextManager = self.app().contextManager()
        
        loadedDefinitionTreeCtrl = wx.TreeCtrl(
            parent, wx.ID_ANY, style=wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.TR_HAS_BUTTONS)
        
        self.loadedDefinitionTreeCtrl = loadedDefinitionTreeCtrl

        self.populateLoadedDefinitionsPane()
        
        return self.loadedDefinitionTreeCtrl
    
    
    
    
    def addPomsetToTreeCtrl(self, ctrl, parentItem, 
                            pomsetContext, pomset, name=None, isRoot=False):
        
        if name is None:
            name = pomset.name() or "anonymous"
        
        if isRoot and pomsetContext.isModified():
            name = name + ' (modified)'
            
        pomsetItem = ctrl.AppendItem(
            parentItem, name, data=wx.TreeItemData((pomsetContext, pomset)))
        
        if not pomset.isAtomic():
            for node in pomset.nodes():
                nodeName = "%s (def: %s)" % (
                    node.name() or "anonymous",
                    node.definitionToReference().name() or "anonymous"
                )
                
                self.addPomsetToTreeCtrl(
                    ctrl, pomsetItem, pomsetContext,
                    node.definitionToReference(),
                    name=nodeName,
                    isRoot = False
                )
            
        return
    
    def populateActivePomsetTreeCtrl(self):
        
        ctrl = self.currentActivePomsetTreeCtrl
        ctrl.DeleteAllItems()
        
        contextManager = self.app().contextManager()
        activePomsetContexts = contextManager.activePomsetContexts()
        numItems = max(len(activePomsetContexts), 1)
        root = ctrl.AddRoot('Active pomsets')
        if len(activePomsetContexts) is 0:
            ctrl.AppendItem(root, 'No active pomsets')
        else:
            for activePomsetContext in activePomsetContexts:
                activePomset = activePomsetContext.pomset()
                self.addPomsetToTreeCtrl(
                    ctrl, root, activePomsetContext, activePomset, isRoot=True)
            pass
 
        # select the currently displayed pomset
        self.selectActivePomset(contextManager.activePomset())
        
        height = min(max(numItems * 25, 100), 250)
        ctrl.SetSize(wx.Size(Frame.FBP_MIN_WIDTH, height))
        
        return
    
    def populateLibraryDefinitionTreeCtrl(self):
        ctrl = self.libraryDefinitionTreeCtrl
        contextManager = self.app().contextManager()

        ctrl.DeleteAllItems()
        root = ctrl.AddRoot('Library definitions')
        
        definitionContexts = [x for x in contextManager.getLibraryDefinitions()]
        for definitionContext in definitionContexts:
            definition = definitionContext.pomset()

            name = definition.name()
            
            # we don't want users to have access 
            # to the boostrap pomsets
            if definition.id() in [LibraryModule.ID_LOADLIBRARYDEFINITION,
                                   LibraryModule.ID_BOOTSTRAPLOADER]:
                continue
            
            ctrl.AppendItem(root, name, data=wx.TreeItemData(definitionContext))
            pass

                
        numItems = len(definitionContexts)
        height = min(max(numItems * 25, 100), 250)
        ctrl.SetSize(wx.Size(Frame.FBP_MIN_WIDTH, height))
                
        return

    
    def populateLoadedDefinitionsPane(self):
        ctrl = self.loadedDefinitionTreeCtrl
        contextManager = self.app().contextManager()

        # if something is currently selected
        # let's save that off
        selectedItem = ctrl.GetSelection()
        selectedContext = None
        if selectedItem.IsOk():
            data = ctrl.GetItemData(selectedItem)
            if data:
                selectedContext = data.GetData()
        selectedItem = None
        
        ctrl.DeleteAllItems()
        root = ctrl.AddRoot('Loaded definitions')
        
        definitionContexts = [x for x in contextManager.getLoadedDefinitions()]
        if len(definitionContexts) is 0:
            ctrl.AppendItem(root, 'No loaded definitions')
        else:
            for definitionContext in definitionContexts:
                definition = definitionContext.pomset()

                name = definition.name() or "Anonymous"
                if definitionContext.isModified():
                    name = name + ' (modified)'

                item = ctrl.AppendItem(
                    root, name, data=wx.TreeItemData(definitionContext))
                if definitionContext is selectedContext:
                    selectedItem = item
            pass

        if selectedItem is not None:
            ctrl.SelectItem(selectedItem)
        
        numItems = max(len(definitionContexts), 1)
        height = min(max(numItems * 25, 100), 250)
        ctrl.SetSize(wx.Size(Frame.FBP_MIN_WIDTH, height))
                
        return

    
    
    def Show(self, *args, **kwds):
        self.canvas._frameIsInProcessOfShowing = True
        zglFrameModule.wxFrame.Show(self, *args, **kwds)
        self.canvas._frameIsInProcessOfShowing = False
        self.resizeCanvas()
        return
    
    def moveToRefreshCanvas(self):
        """
        for some reason, the canvas only refreshes 
        its positioning relative to its containers
        only when the frame is moved
        """
        currentPosition = self.GetPosition()
        x,y = currentPosition.Get()
        point = wx.Point(x+1,y)
        self.SetPosition(point)
        self.SetPosition(currentPosition)
        return
    
    
    def resizeCanvas(self):
        """
        A lot of places will call this
        in order to force the canvas to refresh correctly
        """
        canvasWindow = self.splitter.GetWindow2()
        windowSize = canvasWindow.GetSize()
        newWidth = max(windowSize.GetWidth(), 10)
        newHeight = max(windowSize.GetHeight(), 10)
        self.canvas.resize(newWidth, newHeight)
        
        # we need to do this to force the canvas
        # to reposition itself relative to its containers
        self.moveToRefreshCanvas()

        return

    
    def OnResize(self, event):
        self.resizeCanvas()
        event.Skip()
        return
    
    
    def OnSplitterReposition(self, event):
        self.resizeCanvas()
        return
    
    
    def createApplicationMenus(self):
        menuBar = wx.MenuBar()
    
        # create a new menu for file/serialization stuff
    
        menuPomset = wx.Menu()
        menuPomset.Append(wx.ID_NEW, "New", "Create new pomset")
        menuPomset.Append(wx.ID_OPEN, "Load", "Load pomset")
        menuPomset.Append(wx.ID_CLOSE, "Close", "Close pomset")
        menuPomset.Append(wx.ID_SAVE, "Save", "Save pomset")
        menuPomset.Append(wx.ID_SAVEAS, "Save as", "Save pomset as")
        ## menuPomset.AppendSeparator()
        ## create a new menu for the pomset stuff
        ## menuPomset.Append(MenuModule.ID_DEFINITIONS_EDIT, "Edit definitions")
        ## menuPomset.Append(MenuModule.ID_NODE_ADD, "Add node")
        ## menuPomset.Append(MenuModule.ID_NODE_REMOVE, "Remove selected nodes")
        menuBar.Append(menuPomset, "&Pomset")
        
        # create a new menu for pomset stuff
        menuExecute = wx.Menu()
        
        menuExecute.Append(
            AutomatonModule.ID_EXECUTE_PREVIEW, "Preview", "Preview commands")

        menuExecute.AppendSeparator()
    
        menuExecute.Append(
            AutomatonModule.ID_EXECUTE_LOCAL, "Local", "Execute local")


        # look into configuration 
        # to determine if should add remote execute item
        contextManager = self.app().contextManager()
        automaton = contextManager.automaton()
        configuration = automaton.otherConfigurations()
        if configuration.get('should display remote execute menu item', False):
            # TODO:
            # should verify that remote execute credentials have been specified
            menuExecute.Append(
                AutomatonModule.ID_EXECUTE_REMOTE, "Remote", "Execute remote")

        menuExecute.Append(
            AutomatonModule.ID_EXECUTE_EUCA2OOLS, 
            "Euca2ools", "Execute euca2ools")
        
        menuBar.Append(menuExecute, "&Execute")
    
        # create a new menu for connection stuff
        # TODO:
        # "connect" and "disconnect" should be a menu with their own menu items
        # those menu items will represent the connections
        menuConfiguration = wx.Menu()
        
        menuConfiguration.Append(
            MenuModule.ID_ACCOUNT_MANAGE, 'VMs', 'Manage virtual machines')
        menuConfiguration.Append(
            MenuModule.ID_HADOOP_MANAGE, 'Hadoop', 'Manage Hadoop')
        menuConfiguration.Append(
            MenuModule.ID_EUCA2OOLS_MANAGE, 'Euca2ools', 'Manage euca2ools')
        menuBar.Append(menuConfiguration, "&Configuration")
    
    

        menuHelp = wx.Menu()
        menuHelp.Append(wx.ID_ABOUT, "&About",
                        "More information About this program")
        menuBar.Append(menuHelp, "&Help")

        self.SetMenuBar(menuBar)
    


        eventHandler = EventModule.MenuEventHandler(self)
        self.PushEventHandler(eventHandler)
        eventHandler.bindEvents()
    
        pass

    def OnActivePomsetsPaneRightMouseDown(self, event):
        position = event.GetPosition()
        
        item, where = self.currentActivePomsetTreeCtrl.HitTest(position)
        
        userData = None
        if item.IsOk():
            data = self.currentActivePomsetTreeCtrl.GetItemData(item)
            userData = data.GetData()
        
        # create a popup menu
        popupMenu = MenuModule.ActivePomsetContextualMenu(
            self, userData, parent=self.currentActivePomsetTreeCtrl)

        popupMenu.bindEvents()
        self.currentActivePomsetTreeCtrl.PopupMenu(
            popupMenu, position)

        # according to http://wiki.wxpython.org/PopupMenuOnRightClick
        # need to call destroy
        popupMenu.Destroy()

        return


    def OnLibraryDefinitionPaneRightMouseDown(self, event):

        position = event.GetPosition()
        
        item, where = self.libraryDefinitionTreeCtrl.HitTest(position)
        
        userData = None
        if item.IsOk():
            data = self.libraryDefinitionTreeCtrl.GetItemData(item)
            userData = data.GetData()
        
        # create a popup menu
        popupMenu = MenuModule.LibraryDefinitionContextualMenu(
            self, userData, parent=self.libraryDefinitionTreeCtrl)

        popupMenu.bindEvents()
        self.libraryDefinitionTreeCtrl.PopupMenu(
            popupMenu, position)

        # according to http://wiki.wxpython.org/PopupMenuOnRightClick
        # need to call destroy
        popupMenu.Destroy()

        return


    def OnLoadedDefinitionPaneRightMouseDown(self, event):
        
        position = event.GetPosition()
        
        item, where = self.loadedDefinitionTreeCtrl.HitTest(position)
        
        userData = None
        if item.IsOk():
            data = self.loadedDefinitionTreeCtrl.GetItemData(item)
            userData = data.GetData()
        
        # create a popup menu
        popupMenu = MenuModule.LoadedDefinitionContextualMenu(
            self, userData, parent=self.loadedDefinitionTreeCtrl)

        popupMenu.bindEvents()
        self.loadedDefinitionTreeCtrl.PopupMenu(
            popupMenu, position)

        # according to http://wiki.wxpython.org/PopupMenuOnRightClick
        # need to call destroy
        popupMenu.Destroy()

        return
    
    
    
    def OnBeginDragDefinitionTreeCtrl(self, event):

        item = event.EventObject.GetSelection()
        data = event.EventObject.GetItemData(item)
        self.dragSelection = data.GetData()
        
        event.Skip()
        return
    
    
    def OnEndDragDefinitionTreeCtrl(self, event):
        print "on end drag treectrl"
        return

    
    def OnFbpLeftMouseDoubleClick(self, event):

        item = event.EventObject.GetSelection()
        data = event.EventObject.GetItemData(item)
        
        pomsetData = data.GetData()
        if pomsetData is None:
            # this happens when the user double clicks
            # multiple times in rapid succession
            # and the UI has not has a chance to attach
            # the data model yet
            return
        pomsetContext, pomset = pomsetData

        # TODO:
        # currently only handles root
        # this should handle the case that 
        # a non-root node is referencing a composite definition
        # should show in that case as well
        # (also remember to disable editing of the referenced child
        #  is a library definition)
        if not isinstance(pomset, DefinitionModule.CompositeDefinition):
            return
        
        # because this is activated as s result of
        # chaing the selection on the tree ctrl
        # we want to disable the updating of that selection
        # and avoid an infinite loop
        self._updateActivePomsetTreeCtrlSelection = False
        contextManager = self.app().contextManager()
        contextManager.activePomsetContext(pomsetContext)
        self.displayPomset(pomsetContext, pomset)
        self._updateActivePomsetTreeCtrlSelection = True

        return
    
    def OnFbpLeftMouseUp(self, event):
        return
    
    def OnFbpLeftMouseDown(self, event):
        if hasattr(self, 'dragSelection'):
            delattr(self, 'dragSelection')
        event.Skip()
        return
    
    
    def OnDefinitionValuesChanged(self, event):
        
        # handle the loaded definitions pane,
        # in the case the name got changed
        self.populateLoadedDefinitionsPane()
        
        return

    def processDragSelection(self, event):

        # add node only if the pomset has not been executed
        pomsetContext, pomset = self._currentPomsetInfo
        contextManager = self.app().contextManager()
        if not contextManager.hasTaskForPomset(pomsetContext.pomset()):
            # create the node
            import pomsets_app.gui.utils as GuiUtilsModule
            import uuid
            definitionContext = self.dragSelection
            definition = definitionContext.pomset()
            name = '%s_%s' % (definition.name() or "anonymous",
                              uuid.uuid4().hex[:3])
            position = event.GetPosition()

            contextManager = self.app().contextManager()
            GuiUtilsModule.addNode(
                contextManager, definition, name, position)

        # remove the attribute
        delattr(self, 'dragSelection')
        return


    def setMenuItemActive(self, menuTitle, menuItemTitle, isActive):
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindMenuItem(menuTitle, menuItemTitle)
        # menuItem.Enable(isActive)
        menuBar.Enable(menuItem, isActive)
        return


    def updatePomsetMenu(self):
        contextManager = self.app().contextManager()
        activePomsetContext = contextManager.activePomsetContext()
        self.setMenuItemActive(
            'Pomset', 'Close', activePomsetContext is not None)

        return
    
    def updateExecuteMenus(self):

        contextManager = self.app().contextManager()
        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        # update the menus
        shouldEnableExecute = True
        if contextManager.hasTaskForPomsetPath(pomsetReferencePath):
            # disable the execute menu
            shouldEnableExecute = False
            pass

        try:
            threadPoolId = AutomatonModule.ID_EXECUTE_EUCA2OOLS
            threadPool = contextManager.automaton().getThreadPoolUsingId(
                threadPoolId)
            shouldEnableExecuteEuca2ools = shouldEnableExecute
            if threadPool.isEmpty():
                # disable the execute eucalyptus menu item
                shouldEnableExecuteEuca2ools = False
                pass
        except ValueError, e:
            # this is probably because the threadpool
            # for euca2ools was not created
            shouldEnableExecuteEuca2ools = False
            pass

        self.setMenuItemActive('Execute', 'Local', shouldEnableExecute)
        self.setMenuItemActive('Execute', 'Euca2ools', shouldEnableExecuteEuca2ools)

        return


    
    # END class WxFrame
    pass

