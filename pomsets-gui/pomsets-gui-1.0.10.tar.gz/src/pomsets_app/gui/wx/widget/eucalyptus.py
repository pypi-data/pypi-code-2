import logging

import wx

import pypatterns.command as CommandModule
import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule
import pypatterns.relational.commands as RelationalCommandModule

import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.controller.commands as CloudCommandModule

import pomsets_app.gui.commands as GuiCommandModule
import pomsets_app.gui.grid as PomsetGUITableModule

import pomsets_app.gui.widget as WidgetModule

ID_DIALOG_VIRTUALMACHINES = wx.NewId()


class ConfigDialog(WidgetModule.Dialog):

    XRC_NAME = 'EC2Dialog'
    WIDGET_BINDINGS = WidgetModule.Dialog.WIDGET_BINDINGS + []

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, xmlResource.LoadDialog(parent, ConfigDialog.XRC_NAME))

        valueKeyPair = self.getWidget('ValueKeyPair')
        valueKeyPair.SetMinSize(wx.Size(300, 25))
        valueIdentityFile = self.getWidget('ValueIdentityFile')
        valueIdentityFile.SetMinSize(wx.Size(300, 30))

        self.SetMinSize(wx.Size(325, 150))
        self.Fit()
        self.SetAutoLayout(True)
        return

    pass


class VirtualMachineWindow(wx.Frame):

    def __init__(self, parent, automaton, id, title, dataModel):
        wx.Frame.__init__(self, parent, id, 
                          size=(650, 320), name=title)


        panel = wx.ScrolledWindow(self, -1)
        panel.EnableScrolling(True,True)

        vbox = wx.BoxSizer(wx.VERTICAL)

        table = PomsetGUITableModule.Table(
            dataModel, automaton.contextManager().COLUMNS_VIRTUALMACHINE_DISPLAY)

        self.grid = wx.grid.Grid(panel, size=(640,250))
        self.grid.SetTable(table)
        self.grid.EnableEditing(False)
        self.grid.SetSelectionMode(wx.grid.Grid.wxGridSelectCells)

        vbox.Add(panel)


        hbox = wx.BoxSizer(wx.HORIZONTAL)

        credentialsButton = wx.Button(self, -1, 'Credentials', size=(120, 30))
        assignButton = wx.Button(self, -1, 'Assign', size=(120, 30))
        unassignButton = wx.Button(self, -1, 'Unassign', size=(120, 30))
        refreshButton = wx.Button(self, -1, 'Refresh', size=(70, 30))
        closeButton = wx.Button(self, -1, 'Close', size=(70, 30))

        hbox.Add(credentialsButton, 1)
        hbox.Add(assignButton, 1, wx.LEFT, 5)
        hbox.Add(unassignButton, 1, wx.LEFT, 5)
        hbox.Add(refreshButton, 1, wx.LEFT, 5)
        hbox.Add(closeButton, 1, wx.LEFT, 5)

        credentialsButton.Bind(wx.EVT_BUTTON, self.OnButtonCredentials)
        assignButton.Bind(wx.EVT_BUTTON, self.OnButtonAssign)
        unassignButton.Bind(wx.EVT_BUTTON, self.OnButtonUnassign)
        refreshButton.Bind(wx.EVT_BUTTON, self.OnButtonRefresh)
        closeButton.Bind(wx.EVT_BUTTON, self.OnButtonClose)

        vbox.Add(hbox, 1)

        self.SetSizer(vbox)


        # TODO:
        # add as listener to the system's events
        # generally modifications to this table
        # will only come from commands generated here
        # except when the workers take on tasks from the queue
        # so will need to listen to those events
        # in order to update the data


        return

    def OnButtonCredentials(self, event):

        import pomsets_app.gui.utils as GuiModule
        GuiModule.manageEc2Credentials(self.contextManager, self.GetParent())
        pass


    '''
    def OnButtonAdd(self, event):
        """
        This function as been deprecated
        until we decide to re-incorporate de/provisioning abilities
        back on the system
        """
        contextManager = self.contextManager
        automaton = contextManager.automaton()

        # TODO:
        # should bring up an option for the user to select
        # a particular service name
        # and not hardcode 'eucalyptus'

        command = CommandModule.CompositeCommand()

        # create the provision command
        provisionVmCommand = CloudCommandModule.ProvisionVmCommand(
            automaton, 'eucalyptus', keyPair, imageId)
        command.addCommand(provisionVmCommand)

        # add the commandbuilder
        # which will add the command to assign a worker to the vm
        commandBuilder = \
            CloudCommandModule.AssignWorkerToVmCommandBuilder(
            provisionVmCommand
            )
        command.addCommandBuilder(provisionVmCommand, commandBuilder)

        # add the commandbuilder
        # which will add the commands to synchronize the relational table
        commandBuilder = \
            CloudCommandModule.AddNewEntryToVmTableCommandBuilder(
            provisionVmCommand
            )
        command.addCommandBuilder(provisionVmCommand, commandBuilder)

        # now add the gui synchronization command
        command.addCommandBuilder(
            provisionVmCommand, 
            GuiCommandModule.NotifyRowAddedCommandBuilder(
                provisionVmCommand, self.grid)
        )

        automaton.executeCommand(command)

        pass
    '''

    def OnButtonAssign(self, event):

        contextManager = self.contextManager
        automaton = contextManager.automaton()


        selectedVmInstances = self.getSelectedVmInstances()

        dataModel = self.grid.GetTable().dataModel()

        command = CommandModule.CompositeCommand()
        for vmInstance in selectedVmInstances:

            executeEnvironments = \
                automaton.getExecuteEnvironmentsFromVmInstance(vmInstance)
            if len(executeEnvironments) is not 0:
                continue
            serviceAPI = automaton.getServiceApiFromVmInstance(vmInstance)

            assignEnvCommand = \
                CloudCommandModule.AssignExecuteEnvironmentForVmCommand(
                automaton, serviceAPI, vmInstance)

            command.addCommand(assignEnvCommand)
            pass


        executeEnvironments = []
        if len(command._subcommands):

            # execute the command
            success = automaton.executeCommand(command)

            # if not successful
            if not success:
                logging.error('failed creating execute environments for vmInstances %s' % selectedVmInstances)
                return
            pass
        else:
            logging.error('no commands were generated for assigning execute environments')

        executeEnvironments = {}
        for vmInstance in selectedVmInstances:

            #executeEnvironments.extend(
            #    automaton.getExecuteEnvironmentsFromVmInstance(vmInstance))
            executeEnvironments[vmInstance] = \
                automaton.getExecuteEnvironmentsFromVmInstance(vmInstance)
            pass


        if len(executeEnvironments) is 0:
            logging.error('cannot assign threads as no execute environments are selected')
            return


        command = CommandModule.CompositeCommand()

        # for executeEnvironment in executeEnvironments:
        for vmInstance, executeEnvironmentList in executeEnvironments.iteritems():

            if len(executeEnvironmentList) is not 1:
                raise NotImplementedError('need to handle multiple execute environments for the same vm instance')
            executeEnvironment = executeEnvironmentList[0]

            threads = automaton.getThreadsFromExecuteEnvironment(executeEnvironment)
            if len(threads) is not 0:
                # TODO:
                # will need a way to create multiple threads
                # for the same execute environment
                continue

            # TODO:
            # add ability to parameterize the threadPoolId
            threadPoolId = AutomatonModule.ID_EXECUTE_EUCA2OOLS

            assignWorkerCommand = \
                CloudCommandModule.AssignThreadForExecuteEnvironmentCommand(
                automaton, threadPoolId, executeEnvironment
                )

            command.addCommand(assignWorkerCommand)


            # cannot set thread
            # because it is not getting displayed
            #command.addCommandBuilder(
            #    assignWorkerCommand,
            #    GuiCommandModule.SetVmThreadCommandBuilder(
            #        assignWorkerCommand, self.grid, vmInstance
            #    )
            #)


            rowFilter = RelationalModule.ColumnValueFilter(
                'Instance ID',
                FilterModule.EquivalenceFilter(vmInstance))
            # since we expecte the command to succeed
            # we add a command that will set the value of "Enabled" to True
            command.addCommandBuilder(
                assignWorkerCommand,
                GuiCommandModule.UpdateGridCellValueCommandBuilder(
                    assignWorkerCommand, self.grid, 
                    rowFilter, 'Enabled', 'True'))
            pass


        success = automaton.executeCommand(command)

        # TODO: 
        # something needs to update the grid

        # update the execute menu items
        contextManager.app().GetTopWindow().updateExecuteMenus()

        return


    def OnButtonRefresh(self, event):

        from euca2ools import Euca2ool, InstanceValidationError, Util

        contextManager = self.contextManager
        automaton = contextManager.automaton()

        # TODO:
        # need to check if we have the necessary credentials
        # if not, query for it


        # TODO
        # retrieve all the currently active threads
        # associate the threads with the vmInstaces

        # first clear the table
        dataModel = self.grid.GetTable().dataModel()
        rows = dataModel.clear()

        vmEnvs = {}
        envThreads = {}
        for row in rows:
            vmInstance = row.getColumn('Instance ID')
            executeEnvironments = automaton.getExecuteEnvironmentsFromVmInstance(vmInstance)
            if len(executeEnvironments) is 0:
                continue

            vmEnvs[vmInstance] = executeEnvironments[0]
            threads = automaton.getThreadsFromExecuteEnvironment(executeEnvironments[0])
            if len(threads) is 0:
                continue

            envThreads[executeEnvironments[0]] = threads[0]

            # TODO:
            # need to handle assigned tasks

            pass

        if len(rows):
            msg = wx.grid.GridTableMessage(
                self.grid.GetTable(),
                wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                len(rows)
            )
            self.grid.ProcessTableMessage(msg)

        reservations = []

        try:
            controllerValues = automaton.getCloudControllerCredentialsForAPI('euca2ools')
        except KeyError, e:
            print "should query user for credentials"
            pass


        try:

            # 'Service', 'Reservation ID', 'Instance ID', 'Image ID', 'IP', 
            # 'Enabled', 'Thread', 'Assigned task'

            euca = Euca2ool()

            euca.ec2_url = controllerValues['url']
            euca.ec2_user_access_key = controllerValues['access key']
            euca.ec2_user_secret_key = controllerValues['secret key']

            """
            # TODO:
            # can remove this once euca2ools uses an exception model
            # instead of just calling sys.exit
            if not os.getenv('EC2_ACCESS_KEY'):
                raise KeyError('no value for EC2_ACCESS_KEY specified')

            # TODO:
            # can remove this once euca2ools uses an exception model
            # instead of just calling sys.exit
            if not os.getenv('EC2_SECRET_KEY'):
                raise KeyError('no value for EC2_SECRET_KEY specified')

            self.ec2_url
            """

            euca_conn = euca.make_connection()

            reservations = euca_conn.get_all_instances([])
        except Exception, e:
            print "error on making connecting to Eucalyptus >> %s" % e
            pass

        print "after querying Eucalyptus"

        if len(reservations) is 0:
            print "no active reservations"

        rows = []
        for reservation in reservations:
            for instance in reservation.instances:
                # reservation.id
                # instance.id
                # instance.image_id
                # instance.public_dns_name
                # instance.state (this is so we dont show terminated ones)
                # instance.key_name
                row = dataModel.addRow()
                row.setColumn('Service', 'Eucalyptus')
                row.setColumn('API', 'euca2ools')
                row.setColumn('Reservation ID', reservation.id)
                row.setColumn('Instance ID', instance.id)
                row.setColumn('Image ID', instance.image_id)
                row.setColumn('IP', instance.public_dns_name)
                row.setColumn('Key name', instance.key_name)


                # TODO:
                # this should be a join operation


                vmEnv = vmEnvs.get(instance.id, None)
                envThread = None
                if vmEnv:
                    envThread = envThreads.get(vmEnv, None)
                    row.setColumn('Enabled', 'True')
                else:
                    row.setColumn('Enabled', 'False')
                

                rows.append(row)
                pass
            pass

        if len(rows):
            msg = wx.grid.GridTableMessage(
                self.grid.GetTable(),
                wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                len(rows)
            )
            self.grid.ProcessTableMessage(msg)
            pass


        event.Skip()
        return



    def OnButtonClose(self, event):

        # remove self from the list of listeners
        # otherwise this window will not 
        # be released, due to reference counting

        self.Close()
        pass


    def getSelectedVmInstances(self):
        # get the thread to be dismissed
        # get the vm to be terminated
        # (only if there are no other threads)

        vmInstances = []

        selectedRowIndices = self.grid.GetSelectedRows()
        for rowIndex in selectedRowIndices:
            columnIndex = self.grid.GetTable().getIndexForColumn('Instance ID')
            vmInstance = self.grid.GetTable().GetValue(rowIndex, columnIndex)
            vmInstances.append(vmInstance)

        return vmInstances


    def OnButtonUnassign(self, event):

        contextManager = self.contextManager
        automaton = contextManager.automaton()


        selectedVmInstances = self.getSelectedVmInstances()

        vmInstances = []

        dataModel = self.grid.GetTable().dataModel()
        for vmInstance in selectedVmInstances:
            filter = FilterModule.constructAndFilter()
            filter.addFilter(
                RelationalModule.ColumnValueFilter(
                    'Instance ID',
                    FilterModule.EquivalenceFilter(vmInstance)
                    )
                )
            filter.addFilter(
                RelationalModule.ColumnValueFilter(
                    'Enabled',
                    FilterModule.EquivalenceFilter('True'))
                )
            #rows = [x for x in dataModel.retrieve(filter, ['Thread'])]
            #thread = rows[0][0]
            #if not (thread is RelationalModule.Table.NULL or
            #        thread is None):
            #    vmInstances.append(vmInstance)
            rows = [x for x in dataModel.retrieve(filter)]
            if len(rows):
                vmInstances.append(vmInstance)
            pass


        if len(vmInstances) is 0:
            print "nothing to do, as no rows are selected"
            return

        command = CommandModule.CompositeCommand()

        # TODO:
        # add ability to parameterize the threadPoolId
        threadPoolId = AutomatonModule.ID_EXECUTE_EUCA2OOLS

        for vmInstance in vmInstances:
            # create the command to dismiss the worker
            # but do it only if there's a worker assigned to the vm
            # which there should be
            dismissWorkerCommand = CloudCommandModule.UnassignWorkerFromVmCommand(
                automaton, threadPoolId, vmInstance
                )
            command.addCommand(dismissWorkerCommand)


            """
            command.addCommandBuilder(
                dismissWorkerCommand,
                GuiCommandModule.UnsetVmThreadCommandBuilder(
                    dismissWorkerCommand, self.grid
                )
            )
            """

            rowFilter = RelationalModule.ColumnValueFilter(
                'Instance ID',
                FilterModule.EquivalenceFilter(vmInstance))
            # since we expecte the command to succeed
            # we add a command that will set the value of "Enabled" to True
            command.addCommandBuilder(
                dismissWorkerCommand,
                GuiCommandModule.UpdateGridCellValueCommandBuilder(
                    dismissWorkerCommand, self.grid, 
                    rowFilter, 'Enabled', 'False'))

            pass

        automaton.executeCommand(command)

        return


    '''
    def OnButtonRemove(self, event):
        """
        this function is deprecated until we implement
        the ability to control clusters from within the application
        """

        # get the thread to be dismissed
        # get the vm to be terminated
        # (only if there are no other threads)
        selectedRowIndices = self.grid.GetSelectedRows()
        if len(selectedRowIndices) is 0:
            print "nothing to do, as no rows are selected"
            return
        elif len(selectedRowIndices) is not 1:
            raise NotImplementedError('currently implemented for only one row')

        columnIndex = self.grid.GetTable().getIndexForColumn('Instance ID')
        vmInstance = self.grid.GetTable().GetValue(selectedRowIndices[0], columnIndex)

        contextManager = self.contextManager
        automaton = contextManager.automaton()

        command = CommandModule.CompositeCommand()

        # create the command to dismiss the worker
        # but do it only if there's a worker assigned to the vm
        # which there should be
        dismissWorkerCommand = CloudCommandModule.UnassignWorkerFromVmCommand(
            automaton, vmInstance
            )
        command.addCommand(dismissWorkerCommand)

        # create the terminate command
        terminateVmCommand = CloudCommandModule.TerminateVmCommand(
            automaton, vmInstance)
        command.addCommand(terminateVmCommand)

        # create the command to remove entry from the table
        # unlike add, we do not use a command builder
        # because we already have all the data necessary
        filter = RelationalModule.ColumnValueFilter(
            'Instance ID',
            FilterModule.EquivalenceFilter(vmInstance.id)
        )
        removeEntryCommand = RelationalCommandModule.RemoveRowsCommand(
            automaton.virtualMachineTable(), filter)
        command.addCommand(removeEntryCommand)

        # TODO:
        # attach the command builder that creates the command
        # to notify that the grid needs to refresh

        automaton.executeCommand(command)

        return
    '''

    def populateData(self):
        return

    # END class VirtualMachineWindow
    pass
