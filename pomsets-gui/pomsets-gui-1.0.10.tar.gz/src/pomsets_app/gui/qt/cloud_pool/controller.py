import logging
import os

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.command as CommandModule
import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule
import pypatterns.relational.commands as RelationalCommandModule

import pomsets.parameter as ParameterModule

import pomsets_app.utils as AppUtilsModule
import pomsets_app.gui.qt as QtModule
import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.controller.commands as CloudCommandModule


class Controller(QtModule.Controller, QtGui.QDialog):

    INDEX_INSTANCEID = 3

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        self.updateGuiTable()
        return


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)
        if buttonRole == QtGui.QDialogButtonBox.ApplyRole:
            self.saveValues()
            pass
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            self.saveValues()
            self.accept()
            pass
        if buttonRole == QtGui.QDialogButtonBox.RejectRole:
            self.reject()
            pass
        return

    @pyqtSlot()
    def on_buttonCredentials_clicked(self):
        self.contextManager().mainWindow().OnEuca2oolsConfiguration()
        return

    @pyqtSlot()
    def on_buttonAssign_clicked(self):
        self.OnAssignSelected()
        return

    @pyqtSlot()
    def on_buttonUnassign_clicked(self):
        self.OnUnassignSelected()
        return

    @pyqtSlot()
    def on_buttonRefresh_clicked(self):
        self.refreshDataModel()
        self.updateGuiTable()
        return



    def getSelectedVmInstances(self):
        # get the thread to be dismissed
        # get the vm to be terminated
        # (only if there are no other threads)

        widget = self.widget()
        tableInstances = widget.tableInstances
        selectedItems = tableInstances.selectedItems()

        selectedRows = list(set([x.row() for x in selectedItems]))
        selectedInstances = []
        for selectedRow in selectedRows:
            item = tableInstances.item(selectedRow, Controller.INDEX_INSTANCEID)
            selectedInstances.append(str(item.data(Qt.DisplayRole).toString()))
        return selectedInstances


    def OnAssignSelected(self):

        contextManager = self.contextManager()
        automaton = contextManager.automaton()

        selectedVmInstances = self.getSelectedVmInstances()

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

            executeEnvironments[vmInstance] = \
                automaton.getExecuteEnvironmentsFromVmInstance(vmInstance)
            pass


        if len(executeEnvironments) is 0:
            logging.error('cannot assign threads as no execute environments are selected')
            return


        command = CommandModule.CompositeCommand()

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

            rowFilter = RelationalModule.ColumnValueFilter(
                'Instance ID',
                FilterModule.EquivalenceFilter(vmInstance))

            # TODO:
            # this should be a command builder
            # but we don't have a command builder right now
            # that sets a column using a row filter
            command.addCommand(
                RelationalCommandModule.SetColumnValueUsingRowFilterCommand(
                    rowFilter,
                    automaton.virtualMachineTable(),
                    'Enabled',
                    str(True)
                    )
                )
            

            pass


        success = automaton.executeCommand(command)
        if success:
            self.updateGuiTable()


        # update the execute menu items
        # contextManager.app().GetTopWindow().updateExecuteMenus()


        return

    def OnUnassignSelected(self):

        contextManager = self.contextManager()
        automaton = contextManager.automaton()
        dataModel = automaton.virtualMachineTable()

        selectedVmInstances = self.getSelectedVmInstances()

        vmInstances = []

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
            rows = [x for x in dataModel.retrieve(filter)]
            if len(rows):
                vmInstances.append(vmInstance)
            pass


        if len(vmInstances) is 0:
            logging.debug("nothing to do, as no rows are selected")
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


            rowFilter = RelationalModule.ColumnValueFilter(
                'Instance ID',
                FilterModule.EquivalenceFilter(vmInstance))

            # TODO:
            # this should be a command builder
            # but we don't have a command builder right now
            # that sets a column using a row filter
            command.addCommand(
                RelationalCommandModule.SetColumnValueUsingRowFilterCommand(
                    rowFilter,
                    automaton.virtualMachineTable(),
                    'Enabled',
                    str(False)
                    )
                )

            pass

        success = automaton.executeCommand(command)
        if success:
            self.updateGuiTable()

        return


    def refreshDataModel(self):


        contextManager = self.contextManager()
        automaton = contextManager.automaton()

        dataModel = automaton.virtualMachineTable()
        rows = dataModel.clear()

        vmEnvs = {}
        envThreads = {}
        for row in rows:
            vmInstance = row.getColumn('Instance ID')
            executeEnvironments = \
                automaton.getExecuteEnvironmentsFromVmInstance(vmInstance)
            if len(executeEnvironments) is 0:
                continue

            vmEnvs[vmInstance] = executeEnvironments[0]
            threads = automaton.getThreadsFromExecuteEnvironment(
                executeEnvironments[0])
            if len(threads) is 0:
                continue

            envThreads[executeEnvironments[0]] = threads[0]

            # TODO:
            # need to handle assigned tasks

            pass

        reservations = []
        try:
            controllerValues = \
                automaton.getCloudControllerCredentialsForAPI('euca2ools')
        except KeyError, e:
            logging.warn("should query user for credentials")
            pass


        try:

            # 'Service', 'Reservation ID', 'Instance ID', 'Image ID', 'IP', 
            # 'Enabled', 'Thread', 'Assigned task'

            from euca2ools import Euca2ool
            euca = Euca2ool()

            euca.ec2_url = controllerValues['url']
            euca.ec2_user_access_key = controllerValues['access key']
            euca.ec2_user_secret_key = controllerValues['secret key']

            euca_conn = euca.make_connection()

            reservations = euca_conn.get_all_instances([])
        except Exception, e:
            logging.error("error on making connecting to Eucalyptus >> %s" % e)
            pass

        if len(reservations) is 0:
            logging.debug("no active reservations")

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
                    if envThread:
                        envThread = envThreads.get(vmEnv, None)
                    row.setColumn('Enabled', 'True')
                else:
                    row.setColumn('Enabled', 'False')

                rows.append(row)
                pass
            pass
        return



    def updateGuiTable(self):

        widget = self.widget()
        contextManager = self.contextManager()
        automaton = contextManager.automaton()

        tableInstances = widget.tableInstances
        dataModel = automaton.virtualMachineTable()

        # first clear the table
        while tableInstances.rowCount():
            tableInstances.removeRow(0)


        tableInstances.setRowCount(dataModel.rowCount())
        
        for rowIndex, row in enumerate(dataModel.rows()):

            item = QtGui.QTableWidgetItem('Service')
            item.setData(Qt.DisplayRole, row.getColumn('Service'))
            tableInstances.setItem(rowIndex, 0, item)
            
            item = QtGui.QTableWidgetItem('API')
            item.setData(Qt.DisplayRole, row.getColumn('API'))
            tableInstances.setItem(rowIndex, 1, item)

            item = QtGui.QTableWidgetItem('Reservation ID')
            item.setData(Qt.DisplayRole, row.getColumn('Reservation ID'))
            tableInstances.setItem(rowIndex, 2, item)

            item = QtGui.QTableWidgetItem('Instance ID')
            item.setData(Qt.DisplayRole, row.getColumn('Instance ID'))
            tableInstances.setItem(rowIndex, Controller.INDEX_INSTANCEID, item)

            item = QtGui.QTableWidgetItem('Image ID')
            item.setData(Qt.DisplayRole, row.getColumn('Image ID'))
            tableInstances.setItem(rowIndex, 4, item)

            item = QtGui.QTableWidgetItem('IP address')
            item.setData(Qt.DisplayRole, row.getColumn('IP'))
            tableInstances.setItem(rowIndex, 5, item)

            item = QtGui.QTableWidgetItem('Key name')
            item.setData(Qt.DisplayRole, row.getColumn('Key name'))
            tableInstances.setItem(rowIndex, 6, item)

            item = QtGui.QTableWidgetItem('Assigned')
            item.setData(Qt.DisplayRole, row.getColumn('Enabled'))
            tableInstances.setItem(rowIndex, 7, item)
            pass

        return



    # END class Controller
    pass
