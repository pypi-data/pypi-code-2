
import wx
import pomsets_app.gui.widget as WidgetModule

class MessageDialog(WidgetModule.Dialog):

    XRC_NAME = 'TaskOutputMessagesDialog'

    WIDGET_BINDINGS = WidgetModule.Dialog.WIDGET_BINDINGS + [
        ('treectrlTasks', 'OnTaskSelected', wx.EVT_TREE_SEL_CHANGED)
    ]

    def __init__(self, xmlResource, parent=None):

        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(parent, MessageDialog.XRC_NAME))

        self.SetSize(wx.Size(575, 380))
        self.SetAutoLayout(True)

        treeCtrl = self.getWidget('treectrlTasks')
        treeCtrl.SetMinSize(wx.Size(150, 300))

        textOutputMessage = self.getWidget('textOutputMessage')
        textOutputMessage.SetMinSize(wx.Size(400,300))

        # okButton = wx.xrc.XRCCTRL(self, 'wxID_OK')
        # self.Bind(wx.EVT_BUTTON, self.OnButtonOk, okButton)
        # treeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTaskSelected)

        self._taskMessageMap = {}

        return


    def populateTaskTree(self, task):

        tree = self.getWidget('treectrlTasks')

        root = tree.AddRoot('Root')

        taskItemMap = {}
        taskParentItemMap = {}
        taskNameMap ={}

        tasksToAdd = [task]
        taskParentItemMap[task] = root
        taskNameMap[task] = task.definition().id()

        while len(tasksToAdd):
            task = tasksToAdd.pop(0)
            itemData = wx.TreeItemData()
            itemData.SetData(task)
            taskItem = tree.AppendItem(
                # taskParentItemMap[task], str(task), data=itemData)
                taskParentItemMap[task], 
                taskNameMap.get(task, str(task)), data=itemData
            )
            taskItemMap[task] = taskItem

            import pomsets.task as TaskModule
            if isinstance(task, TaskModule.CompositeTask):

                # get all the child tasks
                for index, childTask in enumerate(task.getChildTasks()):
                    taskParentItemMap[childTask] = taskItem
                    taskNameMap[childTask] = str(index)
                    tasksToAdd.append(childTask)
                    pass

                pass
            pass

        return

    def updateMessageBox(self):

        task = self._selectedTask

        messageBox = self.getWidget('textOutputMessage')

        value = self._taskMessageMap.get(task, None)
        if not value:
            request = task.workRequest()
            stream = request.kwds.get('process message output', None)

            lines = []

            executedCommand = request.kwds.get('executed command', None)
            if executedCommand:
                lines.append('# executed command\n')
                lines.append('# %s \n' % ' '.join(executedCommand))
                lines.append('\n')

            if stream is not None:
                lines.extend(stream.readlines())

            if request.kwds.get('exception stack trace', None) is not None:
                exceptionStackTrace = request.kwds.get('exception stack trace')
                lines.extend(exceptionStackTrace)

            value = ''.join(lines)
            self._taskMessageMap[task] = value
            pass

        if value:
            messageBox.SetValue(value)
            #print "messageBox class >> %s" % messageBox.__class__
            #page = "<html>%s</html>" % value
            #messageBox.SetPage(page)

        return

    def OnTaskSelected(self, event):

        tree = self.getWidget('treectrlTasks')

        treeItem = event.GetItem()
        itemData = tree.GetItemData(treeItem)
        task = itemData.GetData()

        self._selectedTask = task
        self.updateMessageBox()

        return


    pass




class ParameterValuesDialog(WidgetModule.Dialog):

    XRC_NAME = 'ParameterValuesDialog'
    WIDGET_BINDINGS = WidgetModule.Dialog.WIDGET_BINDINGS + [
        ('wxID_APPLY', 'OnButtonApply', wx.EVT_BUTTON)
    ]

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(parent, ParameterValuesDialog.XRC_NAME))
        # self.Fit()
        self.SetSize(wx.Size(475, 475))
        self.SetAutoLayout(True)

        textCtrl = self.getWidget('textParameterValue')
        textCtrl.SetMinSize( wx.Size( 300,250 ) )
        staticText = self.getWidget('labelParameterDescription')
        staticText.SetMinSize( wx.Size( 300,100 ) );
        listBox = self.getWidget('listParameters')
        listBox.SetMinSize( wx.Size( 150,350 ) )

        self.Bind(wx.EVT_LISTBOX, self.OnSelect)



        return


    def dataNode(self, value=None):
        if value is not None:
            self._dataNode = value
        return self._dataNode

    def selectedParameter(self, value=None):
        if value is not None:
            self._selectedParameter = value
        return self._selectedParameter


    def OnButtonApply(self, event):
        (dataNode, parameter) = \
         self.dataNode().getParameterToEdit(self.selectedParameter())
        textCtrl = self.getWidget('textParameterValue')
        text = textCtrl.GetValue()
        values = text.split("\n")

        # the values are to be set on the blackboard parameter
        parameterId = parameter.id()
        logging.debug('binding parameter %s to value "%s" on dataNode %s' % 
                      (parameterId, values, dataNode))
        dataNode.setParameterBinding(
            parameterId, values)

        # file staging and parameter sweep are to be set on the 
        # actual parameter
        parameter = self.selectedParameter()

        # set the value for file staging
        checkboxFileStaging = self.getWidget('checkboxFileStaging')
        value = checkboxFileStaging.GetValue()
        self.dataNode().parameterStagingRequired(
            parameter, value)

        # set the value for parameter sweep
        checkboxParameterSweep = self.getWidget('checkboxParameterSweep')
        value = checkboxParameterSweep.GetValue()
        logging.debug("in ParameterValuesDialgo.OnButtonApply")
        self.dataNode().isParameterSweep(
            parameter, value
        )

        return


    def OnSelect(self, event):

        listBox = self.getWidget('listParameters')
        selectionIndex = listBox.GetSelection()

        # this should be the parameter object
        # event.ClientData
        self.selectedParameter(event.ClientData.id())


        self.updateValues()

        return

    def updateValues(self):
        # could probably combine populateTextCtrl and SetParameterName
        # by calling something like setParameter(parameter)
        self.populateTextCtrl()
        self.setParameterName()

        parameterId = self.selectedParameter()
        parameter = self.dataNode().getParameter(parameterId)

        # enable the checkbox only if the value is supposed to be a file
        checkboxFileStaging = self.getWidget('checkboxFileStaging')
        if parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT) or\
           parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISINPUTFILE):
            checkboxFileStaging.Enable(True)

            value = self.dataNode().parameterStagingRequired(parameterId)
            checkboxFileStaging.SetValue(value)


        else:
            checkboxFileStaging.SetValue(False)
            checkboxFileStaging.Enable(False)

        # update the value for parameter sweep
        checkboxParameterSweep = self.getWidget('checkboxParameterSweep')
        value = self.dataNode().isParameterSweep(parameterId)
        checkboxParameterSweep.SetValue(value)

        return

    def populateParameterList(self):
        """
        fill in the values for the list box
        """

        listBox = self.getWidget('listParameters')

        filter = FilterModule.ObjectKeyMatchesFilter(
            keyFunction=lambda x: x.portType(),
            filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL)
        )
        notFilter = FilterModule.constructNotFilter()
        notFilter.addFilter(filter)

        for index, parameter in enumerate(
            self.dataNode().getParametersByFilter(notFilter)):

            listBox.Insert(parameter.name(),
                           index,
                           parameter)
            pass

        return

    def selectParameterInListBox(self):
        parameterName = self.selectedParameter()
        listBox = self.getWidget('listParameters')
        listBox.SetStringSelection(parameterName)
        return

    def setParameterName(self):
        staticText = self.getWidget('labelParameterDescription')
        staticText.SetLabel(self.selectedParameter())
        return

    def populateTextCtrl(self):

        # first we have to get the actual dataNode and parameter
        (dataNode, parameter) = \
         self.dataNode().getParameterToEdit(self.selectedParameter())

        values = ''
        try:
            values = '\n'.join(dataNode.getParameterBinding(parameter.id()))
        except KeyError, e:
            logging.error(e)
            pass

        textCtrl = self.getWidget('textParameterValue')
        textCtrl.SetValue(values)
        return


    # END class ParameterValuesDialog
    pass


class ExecutionPreviewDialog(WidgetModule.Dialog):

    ID_EXECUTIONPREVIEW = wx.NewId()

    XRC_NAME = 'ExecutionPreviewDialog'

    WIDGET_BINDINGS = WidgetModule.Dialog.WIDGET_BINDINGS + []

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(parent, ExecutionPreviewDialog.XRC_NAME))
        self.SetSize(wx.Size(520, 375))
        self.SetAutoLayout(True)


        textCtrl = self.getWidget('textCtrl')
        textCtrl.SetMinSize( wx.Size( 500,300 ) )


        # okButton = wx.xrc.XRCCTRL(self, 'wxID_OK')
        # self.Bind(wx.EVT_BUTTON, self.OnButtonOk, okButton)

        return


    def populateTextCtrl(self, value):
        # TODO:
        # will have to hande the case where nodes are selected

        textCtrl = self.getWidget('textCtrl')
        textCtrl.SetValue(value)

        return


    # END ExecutionPreviewDialog
    pass
