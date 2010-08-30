import logging
import uuid
import wx

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.library as LibraryModule

import pomsets_app.gui.event as EventModule
import pomsets_app.gui.widget as WidgetModule

import pomsets.parameter as ParameterModule


ID_DIALOG_SELECTDEFINITION = wx.NewId()

class SelectDefinitionDialog(WidgetModule.Dialog):
    
    XRC_NAME = 'SelectDefinitionDialog'

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(parent, SelectDefinitionDialog.XRC_NAME))
        self.Fit()
        self.SetAutoLayout(True)

        treeCtrl = self.getWidget('definitionTreeCtrl')
        treeCtrl.SetSize(wx.Size(275, 400))

        self.SetSize(wx.Size(300, 450))

        return

    def populate(self):
        contextManager = self.contextManager

        treeCtrl = self.getWidget('definitionTreeCtrl')
        root = treeCtrl.AddRoot('Definitions')


        libraryRoot = treeCtrl.AppendItem(
            root, 'Library definitions')
        for definition in contextManager.getLibraryDefinitions():
            if definition.id() in [LibraryModule.ID_LOADLIBRARYDEFINITION,
                                   LibraryModule.ID_BOOTSTRAPLOADER]:
                continue
            name = definition.name() or "Anonymous"
            treeCtrl.AppendItem(
                libraryRoot, name, data=wx.TreeItemData(definition))
            pass

        loadedRoot = treeCtrl.AppendItem(
            root, 'Loaded definitions')
        for definition in contextManager.getLoadedDefinitions():
            name = definition.name() or "Anonymous"
            treeCtrl.AppendItem(
                loadedRoot, name, data=wx.TreeItemData(definition))
            pass

        treeCtrl.ExpandAll()

        return
    
    def OnButtonCancel(self, event):

        # close the dialog box with return code cancel
        self.EndModal(wx.ID_CANCEL)
        return

    def OnButtonOk(self, event):

        nameTextCtrl = self.getWidget('nameTextCtrl')
        name = nameTextCtrl.GetValue()

        treeCtrl = self.getWidget('definitionTreeCtrl')
        selectedItem = treeCtrl.GetSelection()
        selectedDefinition = None
        if selectedItem.IsOk():
            data = treeCtrl.GetItemData(selectedItem)
            selectedDefinition = data.GetData()
            selectedDefinition = selectedDefinition

        if selectedDefinition is None:
            self.EndModal(wx.ID_CANCEL)
            return

        self.nodeName = name
        self.selectedDefinition = selectedDefinition

        self.EndModal(wx.ID_OK)
        return

    # END SelectDefinitionDialog
    pass




class EditAtomicDefinitionDialog(WidgetModule.Dialog):
    XRC_NAME = 'EditDefinitionDialog'
    WIDGET_BINDINGS = [
        ('wxID_OK', 'OnButtonOk', wx.EVT_BUTTON),
        ('wxID_APPLY', 'OnButtonApply', wx.EVT_BUTTON),
        ('buttonAdd', 'OnAddParameter', wx.EVT_BUTTON),
        ('buttonEdit', 'OnEditParameter', wx.EVT_BUTTON),
        ('buttonRemove', 'OnRemoveParameter', wx.EVT_BUTTON),
        ('choiceExecutableType', 'OnChoiceExecutable', wx.EVT_CHOICE)
    ]


    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(parent, EditAtomicDefinitionDialog.XRC_NAME))
        self.Fit()
        self.SetAutoLayout(True)

        self.listBoxParameters = self.getWidget('listBoxParameters')
        self.definitionToEdit = None

        self.SetSize(wx.Size(300, 450))

        return

    def populate(self):

        # first populate the possible executable types
        choiceExecutableType = self.getWidget('choiceExecutableType')

        contextManager = self.contextManager
        executableTypes = contextManager.getExecutableTypes()
        map(choiceExecutableType.Append, executableTypes)
        self.executableTypes = executableTypes
        return


    def setObjectToEdit(self, contextToEdit):

        self.contextToEdit = contextToEdit

        definitionToEdit = contextToEdit.pomset()
        assert definitionToEdit is not None
        self.definitionToEdit = definitionToEdit

        textCtrlName = self.getWidget('textCtrlName')
        textCtrlName.SetValue(definitionToEdit.name())

        textCtrlDescription = self.getWidget('textCtrlDescription')
        textCtrlDescription.SetValue(definitionToEdit.description() or '')

        executable = self.definitionToEdit.executable()
        executableType = self.contextManager.getTypeForExecutable(executable)
        index = self.executableTypes.index(executableType)
        choiceExecutableType = self.getWidget('choiceExecutableType')
        choiceExecutableType.SetSelection(index)        
        self.displayGuiForEditingExecutableType(executableType)

        # populate parameters
        self.populateParameters()
        self.Refresh()

        return

    def OnChoiceExecutable(self, event):
        choiceExecutableType = self.getWidget('choiceExecutableType')
        executableType = choiceExecutableType.GetStringSelection()
        # type
        index = self.executableTypes.index(executableType)
        choiceExecutableType.SetSelection(index)

        self.displayGuiForEditingExecutableType(executableType)

        self.Refresh()
        return


    def displayGuiForEditingExecutableType(self, executableType):

        executable = self.definitionToEdit.executable()
        if executable is None or \
           not self.contextManager.getTypeForExecutable(executable) == executableType:
            executableClass = self.contextManager.getClassForExecutableType(executableType)
            executable = executableClass()

        dialogSizer = self.GetSizer()
        item =dialogSizer.GetItem(1)
        gbSizer = item.GetSizer()

        if executableType == 'Shell':
            # turn off unnecessary widgets and
            # turn on necessary widgets

            for x, y, showShow in [(1,0,True),(1,1,True),
                                   (2,0,True),
                                   (3,0,False),(3,1,False),
                                   (4,0,False),(4,1,False),
                                   (5,0,True),(5,1,True)]:
                item = gbSizer.FindItemAtPosition(wx.GBPosition(x, y))
                item.Show(showShow)

            for widgetId, value in [
                ('textCtrlExecutablePath', ' '.join(executable.path())),
                ('checkBoxStageable', executable.stageable()),
                ('textCtrlStaticArgs', ' '.join(executable.staticArgs()))
                ]:
                widget = self.getWidget(widgetId)
                widget.SetValue(value)

            pass
        elif executableType == 'Hadoop Jar':
            # turn off unnecessary widgets
            # turn on necessary widgets

            for x, y, showShow in [(1,0,False),(1,1,False),
                                   (2,0,False),
                                   (3,0,True),(3,1,True),
                                   (4,0,True),(4,1,True),
                                   (5,0,False),(5,1,False)]:
                item = gbSizer.FindItemAtPosition(wx.GBPosition(x, y))
                item.Show(showShow)

            for widgetId, value in [
                ('textCtrlJarFile', ' '.join(executable.jarFile())),
                ('textCtrlJarClass', ' '.join(executable.jarClass())),
                ('textCtrlStaticArgs', ' '.join(executable.staticArgs()))
                ]:
                widget = self.getWidget(widgetId)
                widget.SetValue(value)

            pass
        elif executableType == 'Hadoop Streaming':
            # turn off unnecessary widgets
            # turn on necessary widgets

            for x, y, showShow in [(1,0,False),(1,1,False),
                                   (2,0,False),
                                   (3,0,False),(3,1,False),
                                   (4,0,False),(4,1,False),
                                   (5,0,False),(5,1,False)]:
                item = gbSizer.FindItemAtPosition(wx.GBPosition(x, y))
                item.Show(showShow)
            pass

        elif executableType == 'Hadoop Pipes':
            # turn off unnecessary widgets
            # turn on necessary widgets

            for x, y, showShow in [(1,0,True),(1,1,True),
                                   (2,0,False),
                                   (3,0,False),(3,1,False),
                                   (4,0,False),(4,1,False),
                                   (5,0,False),(5,1,False)]:
                item = gbSizer.FindItemAtPosition(wx.GBPosition(x, y))
                item.Show(showShow)
            for widgetId, value in [
                ('textCtrlExecutablePath', ' '.join(executable.pipesFile())),
                ]:
                widget = self.getWidget(widgetId)
                widget.SetValue(value)

            pass

        gbSizer.Layout()
        self.Layout()

        return

    def populateParameters(self):

        self.listBoxParameters.Clear()

        parametersTable = self.definitionToEdit.parametersTable()

        filter = RelationalModule.ColumnValueFilter(
            'parameter',
            FilterModule.ObjectKeyMatchesFilter(
                filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_DATA),
                keyFunction=lambda x: x.portType()
            )
        )

        parameters = RelationalModule.Table.reduceRetrieve(
            parametersTable,
            filter,
            ['parameter'],
            []
        )
        parameterNames = [x.name() for x in parameters]


        self.listValueMap = dict(zip(parameterNames, parameters))
        self.listKeys = parameterNames

        map(self.listBoxParameters.Append, self.listKeys)

        return

    def getSelectedParameter(self):

        # this will return the selectedIndex
        selectionIndices = self.listBoxParameters.GetSelections()
        if len(selectionIndices) is not 1:
            raise ValueError('need to select a parameter')
        selectedLabel = self.listKeys[selectionIndices[0]]
        parameter = self.listValueMap[selectedLabel]
        return parameter


    def saveValues(self):

        definitionToEdit = self.definitionToEdit

        hasBeenModified = False
        
        textCtrlName = self.getWidget('textCtrlName')
        if not textCtrlName.GetValue() == definitionToEdit.name():
            definitionToEdit.name(textCtrlName.GetValue())
            hasBeenModified = True

        textCtrlDescription = self.getWidget('textCtrlDescription')
        if not textCtrlDescription.GetValue() == definitionToEdit.description():
            definitionToEdit.description(textCtrlDescription.GetValue())
            hasBeenModified = True

        choiceExecutableType = self.getWidget('choiceExecutableType')
        executableType = choiceExecutableType.GetStringSelection()

        executable = definitionToEdit.executable()
        currentExecutableType = self.contextManager.getTypeForExecutable(executable)
        if not currentExecutableType == executableType:
            executableClass = self.contextManager.getClassForExecutableType(executableType)
            executable = executableClass()
            definitionToEdit.executable(executable)
            hasBeenModified = True

        if executableType == 'Shell':
            textCtrlExecutablePath = self.getWidget('textCtrlExecutablePath')
            executablePath = textCtrlExecutablePath.GetValue().split(' ')
            if not executable.path() == executablePath:
                executable.path(executablePath)
                hasBeenModified = True

            checkBoxStageable = self.getWidget('checkBoxStageable')
            isStageable = checkBoxStageable.GetValue()
            if not executable.stageable() == isStageable:
                executable.stageable(isStageable)
                hasBeenModified = True

            textCtrlStaticArgs = self.getWidget('textCtrlStaticArgs')
            staticArgs = textCtrlStaticArgs.GetValue().split(' ')
            if not executable.staticArgs() == staticArgs:
                executable.staticArgs(staticArgs)
                hasBeenModified = True

        elif executableType == 'Hadoop Jar':

            textCtrlJarFile = self.getWidget('textCtrlJarFile')
            jarFile = textCtrlJarFile.GetValue().split(' ')
            if not executable.jarFile() == jarFile:
                executable.jarFile(jarFile)
                hasBeenModified = True

            textCtrlJarClass = self.getWidget('textCtrlJarClass')
            jarClass = textCtrlJarClass.GetValue().split(' ')
            if not executable.jarClass() == jarClass:
                executable.jarClass(jarClass)
                hasBeenModified = True
            pass

        elif executableType == 'Hadoop Streaming':
            executable.jarFile([self.contextManager.getHadoopStreamingJar()])
            executable.jarClass([])
            pass

        elif executableType == 'Hadoop Pipes':
            textCtrlExecutablePath = self.getWidget('textCtrlExecutablePath')
            pipesFile = textCtrlExecutablePath.GetValue().split(' ')
            if not executable.pipesFile() == pipesFile:
                executable.pipesFile(pipesFile)
                hasBeenModified = True
            pass

        if hasBeenModified:
            self.contextToEdit.isModified(True)
            import pomsets_app.gui.event as EventModule
            event = EventModule.DefinitionValuesChangedEvent(
                definition=definitionToEdit)
            self.contextManager.app().GetTopWindow().AddPendingEvent(event)
        
        return


    def OnButtonOk(self, event):
        self.saveValues()
        WidgetModule.Dialog.OnButtonOk(self, event)
        return

    def OnButtonApply(self, event):
        self.saveValues()
        return

    def OnAddParameter(self, event):

        name = '_'.join(['parameter', uuid.uuid4().hex[:3]])

        # default to input parameter
        parameter = ParameterModule.DataParameter(
            name=name, 
            portDirection=ParameterModule.PORT_DIRECTION_INPUT
        )

        self.definitionToEdit.addParameter(parameter)
        self.populateParameters()
        return


    def OnEditParameter(self, event):
        # contextManager, window, parameterToEdit
        import pomsets_app.gui.utils as GuiUtilsModule
        parameterToEdit = self.getSelectedParameter()
        GuiUtilsModule.editParameter(self.contextManager, self, parameterToEdit)
        self.populateParameters()
        return


    def OnRemoveParameter(self, event):
        import pomsets_app.gui.utils as GuiUtilsModule
        parameterToEdit = self.getSelectedParameter()
        self.definitionToEdit.removeParameter(parameterToEdit)
        return

    # END class EditDefinitionDialog
    pass


class EditDefinitionParameterDialog(WidgetModule.Dialog):

    XRC_NAME = 'EditDefinitionParameterDialog'
    WIDGET_BINDINGS = [
        ('wxID_OK', 'OnButtonOk', wx.EVT_BUTTON),
        ('wxID_APPLY', 'OnButtonApply', wx.EVT_BUTTON),
        ('checkBoxList', 'OnCheckboxList', wx.EVT_CHECKBOX),
        ('checkBoxCommandline', 'OnCheckboxCommandline', wx.EVT_CHECKBOX)
    ]

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(
                parent, EditDefinitionParameterDialog.XRC_NAME))
        self.Fit()
        self.SetAutoLayout(True)

        self.parameterToEdit = None
        return


    def setVisibilityOfWidgetItems(self):

        checkboxList = self.getWidget('checkBoxList')
        checkboxCommandline = self.getWidget('checkBoxCommandline')

        isList = checkboxList.GetValue()
        isCommandline = checkboxCommandline.GetValue()

        dialogSizer = self.GetSizer()
        item =dialogSizer.GetItem(0)
        gbSizer = item.GetSizer()

        shouldShowFlag = True
        shouldShowDistributeFlag = True
        # enable the flag items only if commandline is checked
        if isCommandline:
            shouldShowFlag = True
            # enable the distribute flag items only if 
            # both commandline and list are checked
            if isList:
                shouldShowDistributeFlag = True
            else:
                shouldShowDistributeFlag = False
            pass
        else:
            shouldShowFlag = False
            shouldShowDistributeFlag = False
            pass

        visibilitySettings = [
            (4,0,shouldShowFlag),
            (4,1,shouldShowFlag),
            (8,0,shouldShowDistributeFlag)
            ]
        for x, y, showShow in visibilitySettings:
            item = gbSizer.FindItemAtPosition(wx.GBPosition(x, y))
            item.Show(showShow)

        return


    def OnCheckboxList(self, event):
        self.setVisibilityOfWidgetItems()
        return

    def OnCheckboxCommandline(self, event):
        self.setVisibilityOfWidgetItems()
        return


    def getPortDirections(self):
        return ['Input', 'Output']

    def getIndexForPortDirection(self, direction):
        if direction == ParameterModule.PORT_DIRECTION_INPUT:
            return 0
        if direction == ParameterModule.PORT_DIRECTION_OUTPUT:
            return 1
        raise NotImplementedError('not implemented for direction %s' % direction)


    def populate(self):

        choiceDirection = self.getWidget('choiceDirection')
        map(choiceDirection.Append,
            ['Input', 'Output'])

        return

    def setObjectToEdit(self, parameterToEdit):

        self.parameterToEdit = parameterToEdit        

        textCtrlName = self.getWidget('textCtrlName')
        textCtrlName.SetValue(parameterToEdit.name())

        textCtrlDescription = self.getWidget('textCtrlDescription')
        description = parameterToEdit.description() or ''
        textCtrlDescription.SetValue(description)


        choiceDirection = self.getWidget('choiceDirection')
        parameterDirection = parameterToEdit.portDirection()
        choiceDirection.SetSelection(
            self.getIndexForPortDirection(parameterDirection))


        checkBoxCommandline = self.getWidget('checkBoxCommandline')
        isCommandline = parameterToEdit.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_COMMANDLINE)
        checkBoxCommandline.SetValue(isCommandline)
        if isCommandline:

            commandlineOptions = parameterToEdit.getAttribute(
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS,
                defaultValue = {}
            )

            textCtrlFlag = self.getWidget('textCtrlFlag')
            prefixFlag = commandlineOptions.get(
                ParameterModule.COMMANDLINE_PREFIX_FLAG, []
            )
            textCtrlFlag.SetValue(' '.join(prefixFlag))
            pass


        checkBoxOptional = self.getWidget('checkBoxOptional')
        isOptional = parameterToEdit.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISOPTIONAL)
        checkBoxOptional.SetValue(isOptional)

        checkBoxFile = self.getWidget('checkBoxFile')
        isFile =  parameterToEdit.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISINPUTFILE)
        checkBoxFile.SetValue(isFile)

        checkBoxList = self.getWidget('checkBoxList')
        argumentValueIsList = parameterToEdit.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISLIST)
        checkBoxList.SetValue(argumentValueIsList)

        if isCommandline and argumentValueIsList:
            checkBoxDistributeFlag = self.getWidget('checkBoxDistributeFlag')
            shouldDistributePrefixFlag = commandlineOptions.get(
                ParameterModule.COMMANDLINE_PREFIX_FLAG_DISTRIBUTE, False)
            checkBoxDistributeFlag.SetValue(shouldDistributePrefixFlag)
            pass

        self.setVisibilityOfWidgetItems()

        return


    def saveValues(self):

        parameter = self.parameterToEdit

        textCtrlName = self.getWidget('textCtrlName')
        parameter.name(textCtrlName.GetValue())

        textCtrlDescription = self.getWidget('textCtrlDescription')
        parameter.description(textCtrlDescription.GetValue())

        choiceDirection = self.getWidget('choiceDirection')
        choice = choiceDirection.GetStringSelection()
        if choice == 'Input':
            parameter.portDirection('input')
        elif choice == 'Output':
            parameter.portDirection('output')

        checkBoxOptional = self.getWidget('checkBoxOptional')
        parameter.setAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISOPTIONAL, 
            checkBoxOptional.GetValue())

        checkBoxFile = self.getWidget('checkBoxFile')
        parameter.setAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISINPUTFILE, 
            checkBoxFile.GetValue())

        checkBoxList = self.getWidget('checkBoxList')
        parameter.setAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISLIST, 
            checkBoxList.GetValue())

        checkBoxCommandline = self.getWidget('checkBoxCommandline')
        parameter.setAttribute(
            ParameterModule.PORT_ATTRIBUTE_COMMANDLINE, 
            checkBoxCommandline.GetValue())


        commandlineOptions = parameter.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS,
            defaultValue = {}
        )

        # flag
        # distribute flag
        textCtrlFlag = self.getWidget('textCtrlFlag')
        prefixFlag = textCtrlFlag.GetValue()
        commandlineOptions[ParameterModule.COMMANDLINE_PREFIX_FLAG] = prefixFlag.split(' ')

        checkBoxDistributeFlag = self.getWidget('checkBoxDistributeFlag')
        commandlineOptions[ParameterModule.COMMANDLINE_PREFIX_FLAG_DISTRIBUTE]  = checkBoxDistributeFlag.GetValue()

        parameter.setAttribute(
            ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS,
            commandlineOptions
        )

        return


    def OnButtonOk(self, event):
        self.saveValues()
        WidgetModule.Dialog.OnButtonOk(self, event)
        return

    def OnButtonApply(self, event):
        self.saveValues()
        return

    # END class EditDefinitionParameterDialog
    pass


class EditReferenceDefinitionDialog(WidgetModule.Dialog):
    """
    Internally we call this the EditDefinitionReferenceDialog
    but to the user, it's the Task editing dialog.
    The difference lies in that internally, 
    a task is not actually created until a pomset is executed
    but users do not usually make that kind of distinction
    """
    
    XRC_NAME = 'EditReferenceDefinitionDialog'
    WIDGET_BINDINGS = [
        ('wxID_OK', 'OnButtonOk', wx.EVT_BUTTON),
        ('wxID_APPLY', 'OnButtonApply', wx.EVT_BUTTON),
        ('choiceParameter', 'OnChoiceParameter', wx.EVT_CHOICE)
    ]

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(
                parent, EditReferenceDefinitionDialog.XRC_NAME))
        self.Fit()
        self.SetAutoLayout(True)
        self.definitionToEdit = None
        
        textCtrlParameterValues = self.getWidget('textCtrlParameterValues')

        textCtrlParameterValues.SetMinSize(wx.Size(250, 100))
        textCtrlParameterValues.SetSize(wx.Size(250, 100))
        
        return

    
    def setObjectToEdit(self, definitionToEdit):
        
        self.definitionToEdit = definitionToEdit

        textCtrlName = self.getWidget('textCtrlName')
        textCtrlName.SetValue(definitionToEdit.name())

        textCtrlComment = self.getWidget('textCtrlComment')
        textCtrlComment.SetValue(definitionToEdit.comment() or '')
        
        # populate parameters
        self.populateParameters()
        self.populateParameterValues()
        self.Refresh()

        return
    
        
    def populateParameters(self):
        
        # get the parameters from the referenced definition
        
        filter = FilterModule.ObjectKeyMatchesFilter(
            keyFunction=lambda x: x.portType(),
            filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL)
        )
        notFilter = FilterModule.constructNotFilter()
        notFilter.addFilter(filter)

        
        parameters = self.definitionToEdit.getParametersByFilter(notFilter)
        choiceParameter =self.getWidget('choiceParameter')
        if len(parameters) is 0:
            choiceParameter.Append('No parameters defined', None)
        else:
            for parameter in parameters:
                choiceParameter.Append(parameter.id(), parameter)
            self.selectParameter(parameters[0].id())
        return
        
    
    def OnChoiceParameter(self, event):
        self.populateParameterValues()
        self.Refresh()
        return
    
    
    def selectParameter(self, parameterId):
        choiceParameter =self.getWidget('choiceParameter')        
        item = choiceParameter.FindString(parameterId)
        choiceParameter.SetSelection(item)
        return
    
    
    def populateParameterValues(self):
        # get the parameter values from self
        choiceParameter =self.getWidget('choiceParameter')        
        selectedParameterIndex = choiceParameter.GetSelection()
        if selectedParameterIndex == wx.NOT_FOUND:
            return
        parameter = choiceParameter.GetClientData(selectedParameterIndex)
        if parameter is None:
            return
        
        parameterId = parameter.id()

        
        checkBoxStaging = self.getWidget('checkBoxStaging')
        checkBoxStaging.SetValue(
            self.definitionToEdit.parameterStagingRequired(parameterId))
                
        checkBoxSweep = self.getWidget('checkBoxSweep')
        checkBoxSweep.SetValue(
            self.definitionToEdit.isParameterSweep(parameterId))
        
        
        (dataNode, parameterToEdit) = \
         self.definitionToEdit.getParameterToEdit(parameterId)
        
        parameterId = parameterToEdit.id()
        
        values = ''
        try:
            if dataNode.hasParameterBinding(parameterId):
                values = '\n'.join(
                    dataNode.getParameterBinding(parameterId))
            else:
                logging.debug("data node has not parameter bindings for %s" % parameterId)
            pass
        except KeyError, e:
            logging.error("error on populating parameter values >> %s" % e)
            raise
        logging.debug("retrieved bindings for parameter %s >> %s" % (parameterId, values))
        
        textCtrl = self.getWidget('textCtrlParameterValues')
        textCtrl.SetValue(values)
        

        
        return
    
    
    def saveValues(self):
        print "%s saveValues" % self.__class__

        textCtrlName = self.getWidget('textCtrlName')
        textCtrlComment = self.getWidget('textCtrlComment')

        if not self.definitionToEdit.name() == textCtrlName.GetValue():
            self.definitionToEdit.name(textCtrlName.GetValue())

            import pomsets_app.gui.event as EventModule
            event = EventModule.NodeRenamedEvent(
                node = self.definitionToEdit
            )
            self.contextManager.postEvent(event)
            pass

        self.definitionToEdit.comment(textCtrlComment.GetValue())
        
        self.saveParameterValues()
        return

    
    def saveParameterValues(self):
        choiceParameter = self.getWidget('choiceParameter')
        
        selectedParameterIndex = choiceParameter.GetSelection()
        if selectedParameterIndex == wx.NOT_FOUND:
            return
        parameter = choiceParameter.GetClientData(selectedParameterIndex)
        if parameter is None:
            return
        
        parameterId = parameter.id()
        
        checkBoxStaging = self.getWidget('checkBoxStaging')
        checkBoxSweep = self.getWidget('checkBoxSweep')

        # set the value for file staging
        value = checkBoxStaging.GetValue()
        self.definitionToEdit.parameterStagingRequired(
            parameterId, value)

        # set the value for parameter sweep
        value = checkBoxSweep.GetValue()
        # need to set the value only if it has changed
        if not self.definitionToEdit.isParameterSweep(parameterId) == value:
            self.definitionToEdit.isParameterSweep(
                parameterId, value
            )
            
            # if the value has changed
            # we should send an event
            # so that we can update the node image if necessary
            # to hande for displaying parameter sweep
            import pomsets_app.gui.event as EventModule
            event = EventModule.ParameterModifiedEvent(
                definition=self.definitionToEdit,
                parameter=parameterId
            )
            self.contextManager.postEvent(event)
            pass
        
        
        (dataNode, parameterToEdit) = \
         self.definitionToEdit.getParameterToEdit(parameterId)
        parameterId = parameterToEdit.id()
        
        textCtrlParameterValues = self.getWidget('textCtrlParameterValues')
        text = textCtrlParameterValues.GetValue()
        values = text.split("\n")
        
        logging.debug('binding parameter %s to value "%s" on dataNode %s' % 
                      (parameterId, values, dataNode))
        dataNode.setParameterBinding(
            parameterId, values)
        
        
        
        return
    
    
    def OnButtonOk(self, event):
        self.saveValues()
        WidgetModule.Dialog.OnButtonOk(self, event)
        return

    def OnButtonApply(self, event):
        self.saveValues()
        return
    
    
    pass

