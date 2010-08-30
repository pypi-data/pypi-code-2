import pypatterns.command as CommandModule


import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule
import pypatterns.relational.commands as RelationalCommandModule



class ProvisionVmCommand(CommandModule.Command):


    def __init__(self, automaton, 
                 clusterName, keyPair, imageId):
        CommandModule.Command.__init__(self)
        self._automaton = automaton
        self._clusterName = clusterName
        self._keyPair = keyPair
        self._imageId = imageId
        return


    def execute(self):
        vmInstance = self._automaton.provisionVM(
            self._clusterName, self._keyPair, self._imageId)
        self._vmInstance = vmInstance
        return

    def unexecute(self):

        # TODO:
        # if we are going to call terminateVM
        # then it should not run on a thread
        # self._automaton._terminateVmAndThread()
        self._automaton.terminateVmInstance(self._vmInstance)

        return

    # END class ProvisionVmCommand
    pass


class TerminateVmCommand(CommandModule.Command):

    def __init__(self, automaton, vmInstance):
        CommandModule.Command.__init__(self)
        self._vmInstance = vmInstance
        self._automaton = automaton
        return

    def execute(self):
        self._automaton.terminateVmInstance(self._vmInstance)
        return

    def unexecute(self):
        # what can we do to ensure that there's still a VM?
        return

    # END class TerminateVmCommand
    pass



class UnassignWorkerFromVmCommand(CommandModule.Command):

    def __init__(self, automaton, threadPoolId, vmInstance):
        CommandModule.Command.__init__(self)
        self._automaton = automaton
        self._threadPoolId = threadPoolId
        self._vmInstance = vmInstance
        return

    def execute(self):

        # find the worker thread that's associated with the vm instance
        # decouple the vm and the worker thread
        # dismiss the worker thread
        self._automaton.unassignThreadFromVmInstance(
            self._threadPoolId, self._vmInstance)

        return


    def unexecute(self):

        # for now, undoing this command will do nothing
        # there's a question of how the undo of the SetColumnValueCommand
        # can get the value of the new thread

        # create a new worker thread
        # assign the thread to the vm instance
        #worker = self._automaton.assignThreadToInstance(self._vmInstance)
        #self._worker = worker
        return

    # END class UnasignWorkerFromVmCommand
    pass


class AssignExecuteEnvironmentForVmCommand(CommandModule.Command):

    def __init__(self, automaton, serviceAPI, vmInstance):
        CommandModule.Command.__init__(self)
        self._automaton = automaton
        self._serviceAPI = serviceAPI
        self._vmInstance = vmInstance

        return

    def execute(self):
        env = self._automaton.assignExecuteEnvironmentForVmInstance(
            self._serviceAPI,
            self._vmInstance)
        self._executeEnvironment = env
        pass

    def unexecute(self):
        self._automaton.unassignExecuteEnvironmentFromVmInstance(
            self._vmInstance, executeEnvironment = self._executeEnvironment)
        return

    # END class AssignExecuteEnvironmentForVmCommand
    pass

class AssignThreadForExecuteEnvironmentCommand(CommandModule.Command):

    def __init__(self, automaton, threadPoolId, executeEnvironment):
        CommandModule.Command.__init__(self)
        self._automaton = automaton
        self._threadPoolId = threadPoolId
        self._executeEnvironment = executeEnvironment
        return


    def execute(self):
        worker = self._automaton.assignThreadForExecuteEnvironment(
            self._threadPoolId, self._executeEnvironment)
        self._worker = worker
        return

    def unexecute(self):
        # self._automaton.dismissWorker(worker=self._worker)
        threadPool = self._automaton.getThreadPoolUsingId(self._threadPoolId)
        #self._automaton.unassignThreadFromExecuteEnvironment(
        #    self._threadPoolId, self._executeEnvironment)
        threadPool.dismissWorker(worker=self._worker)
        return

    # END class AssignThreadToExecuteEnvironmentCommand
    pass


class AssignWorkerToVmCommandBuilder(CommandModule.CommandBuilder):

    def __init__(self, command):
        CommandModule.CommandBuilder.__init__(self, command)
        return

    def addCommandsPostExecute(self, commands):
        commands.append(
            AssignWorkerToVmCommand(
                self._command._automaton, 
                self._command._vmInstance
            )
        )
        return

    # END class AssignWorkerToVmCommandBuilder
    pass





class AddNewEntryToVmTableCommandBuilder(CommandModule.CommandBuilder):

    def __init__(self, command):
        CommandModule.CommandBuilder.__init__(self, command)
        return

    def addCommandsPostExecute(self, commands):

        vmInstance = self._command._vmInstance
        automaton = self._command._automaton

        vmTable = automaton.virtualMachineTable()

        command = CommandModule.CompositeCommand()

        addRowCommand = RelationalCommandModule.AddRowCommand(vmTable)
        command.addCommand(addRowCommand)

        for column, value in [('Service', vmInstance.region.name),
                              ('Instance ID', vmInstance.id),
                              ('Image ID', vmInstance.image_id),
                              ('IP', vmInstance.public_dns_name),
                              ('Enabled', 'True')]:

            commandBuilder = \
                           RelationalCommandModule.SetColumnValueCommandBuilder(
                               addRowCommand, column, value
                           )
            command.addCommandBuilder(addRowCommand, commandBuilder)
            pass

        commands.append(command)
        return

    # END class AddNewEntryToVmTableCommandBuilder
    pass



