import copy
import functools
import logging
import os
import time

import simplejson as ConfigModule

import currypy 

import pypatterns.command as CommandModule

import pomsets.automaton as AutomatonModule
import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule
import pypatterns.relational.commands as RelationalCommandModule

import pomsets.task as TaskModule

import cloudpool.shell as ShellModule

import pomsets_app.controller as CloudModule


ID_EXECUTE_LOCAL = 1
ID_EXECUTE_REMOTE = 2
ID_EXECUTE_EUCA2OOLS = 3

class Automaton(AutomatonModule.Automaton):

    ATTRIBUTES = AutomatonModule.Automaton.ATTRIBUTES + [
        'cloudControllerTable',
        'virtualMachineTable',
        'eventHandlers',
        'shouldProcessEndedTasks',
        'remoteExecuteCredentials',
        'threadPoolTable',
        'threadTable',
        'executeEnvironmentTable',
        'hadoopConfigurations',
        'otherConfigurations'
    ]

    COLUMNS_VIRTUALMACHINE = [
        'API', 'Instance ID', 'Service', 'Reservation ID', 'Image ID', 'IP', 
        'Enabled', 'Key name', 
    ]

    COLUMN_EXECUTEENVIRONMENTS = [
        'Instance ID', 
        'Execute environment'
    ]

    COLUMNS_THREADS = [
        'Thread', 'Execute environment', 'Assigned task'
    ]

    COLUMNS_CLOUDCONTROLLERCREDENTIALS = [
        'serviceName', 'serviceAPI', 'values']


    @staticmethod
    def doTask(*args, **kwds):
        AutomatonModule.Automaton.doTask(*args, **kwds)
        return


    @staticmethod
    def taskNotifyParentOfCompletion(request, result, 
                                     notifyFunction=None,
                                     contextManager=None):

        """
        this wraps the default completion callback
        the callback is called first,
        and it will update the task execute status
        the frame is then called to update the menu bar actions accordingly
        """

        notifyFunction(request, result)
        frame = contextManager.mainWindow()
        if frame is not None:
            frame.updateMenuBarActions()

        return
        
    @staticmethod
    def taskNotifyParentOfError(request, errorInfo, 
                                notifyFunction=None,
                                contextManager=None):
        """
        this wraps the default error callback
        the callback is called first,
        and it will update the task execute status
        the frame is then called to update the menu bar actions accordingly
        """
        notifyFunction(request, errorInfo)
        frame = contextManager.mainWindow()
        if frame is not None:
            frame.updateMenuBarActions()

        return



    @staticmethod
    def compositeTaskCompleteCallback(request, result):
        """
        this is meant to be called after the composite task
        has initialized all the minimal children,
        not after all maximal children have completed execution
        """
        # TODO:
        # update the gui

        AutomatonModule.Automaton.compositeTaskCompleteCallback(request, result)

        return


    @staticmethod
    def atomicTaskCompleteCallback(request, result):

        # TODO:
        # update the gui

        AutomatonModule.Automaton.atomicTaskCompleteCallback(request, result)

        return



    def __init__(self):

        AutomatonModule.Automaton.__init__(self)

        logging.debug("initializing automaton")

        self.virtualMachineTable(
            RelationalModule.createTable(
                'virtual machines',
                Automaton.COLUMNS_VIRTUALMACHINE
            )
        )

        self.executeEnvironmentTable(
            RelationalModule.createTable(
                'execute environments',
                Automaton.COLUMN_EXECUTEENVIRONMENTS
            )
        )

        self.threadTable(
            RelationalModule.createTable(
                'threads',
                Automaton.COLUMNS_THREADS
            )
        )

        self.eventHandlers(set([]))


        table = RelationalModule.createTable(
            'clouds',
            Automaton.COLUMNS_CLOUDCONTROLLERCREDENTIALS
        )
        self.cloudControllerTable(table)

        table = RelationalModule.createTable(
            'thread pools',
            ['id', 'threadPool']
        )
        self.threadPoolTable(table)

        self.remoteExecuteCredentials([])
        self.hadoopConfigurations({})

        pass


    def saveCloudControllerCredentials(self):
        raise NotImplementedError(
            'have not implemented saving cloud credentials to file')

    def loadConfig(self, config):
        self.loadCloudControllerCredentials(config)
        self.loadRemoteExecuteCredentials(config)
        self.loadHadoopConfigurationValues(config)
        self.loadOtherConfigurations(config)
        return

    def addConfigToSave(self, configData):
        self.addCloudControllerCredentialsToConfig(configData)
        self.addRemoteExecuteCredentialsToConfig(configData)
        self.addHadoopConfigurationsToConfig(configData)
        self.addOtherConfigurationsToSave(configData)
        return

    def loadOtherConfigurations(self, config):
        configCopy = copy.copy(config)
        
        for keyToRemove in ['hadoop configurations',
                            'remote execute credentials',
                            'cloud controller credentials']:
            if keyToRemove in configCopy:
                del configCopy[keyToRemove]

        self.otherConfigurations(configCopy)
        return

    #def addOtherConfigurationsToSave(self, key, configData):
    #    if not key in self.otherConfigurations():
    #        self.otherConfigurations()[key] = []
    #    self.otherConfigurations()[key].append(configData)
    #    return
    def addOtherConfigurationsToSave(self, configData):
        configData.update(self.otherConfigurations())
        return

    def addCloudControllerCredentialsToConfig(self, config):

        credentials = []
        table = self.cloudControllerTable()
        tableColumns = table.columns()
        configKeys = [x for x in tableColumns]
        configKeys[configKeys.index('serviceName')] = 'service name'
        configKeys[configKeys.index('serviceAPI')] = 'service API'
        for row in table.retrieve(columns=tableColumns):
            credentials.append(dict(zip(configKeys, row)))
            pass
        config['cloud controller credentials'] = credentials
        return

    def addRemoteExecuteCredentialsToConfig(self, config):
        config['remote execute credentials'] = self.remoteExecuteCredentials()
        return

    def loadRemoteExecuteCredentials(self, config):
        for credential in config['remote execute credentials']:
            #hostname = credential['hostname']
            #user = credential['user']
            #keyfile = credential['keyfile']
            # self.addRemoteExecuteCredential(hostname, user, keyfile)
            self.remoteExecuteCredentials().append(credential)
            pass
        return


    def loadCloudControllerCredentials(self, config):

        for credential in config['cloud controller credentials']:
            serviceName = credential['service name']
            serviceAPI = credential['service API']
            rawValues = credential['values']

            values = dict([(str(x), str(rawValues[x])) for x in rawValues.keys()])
            self.addCloudControllerCredential(serviceName, serviceAPI, **values)

            pass

        return


    def getCloudControllerCredentialsForAPI(self, serviceAPI):
        filter = RelationalModule.ColumnValueFilter(
            'serviceAPI',
            FilterModule.EquivalenceFilter(serviceAPI)
        )
        values = [x for x in self.getCloudControllerCredentials(filter)]
        if len(values) is not 1:
            raise KeyError("not implemented to handle %s values" % values)

        return values[0][0]


    def getCloudControllerCredentials(self, filter=None, columns=None):

        if columns is None:
            columns = ['values']

        if filter is None:
            filter = FilterModule.TRUE_FILTER

        for x in self.cloudControllerTable().retrieve(
            filter = filter,
            columns = columns):
            yield x
        raise StopIteration


    def addCloudControllerCredential(self, serviceName, serviceAPI, **kwds):
        """
        Possible values:
        * (Amazon, EC2, ...)
        * (Amazon, Euca2ools, ...)
        * (Eucalyptus, Euca2ools, ...)
        * (Rackspace, Rackspace, ...)
        """

        row = self.cloudControllerTable().addRow()
        row.setColumn('serviceName', serviceName)
        row.setColumn('serviceAPI', serviceAPI)
        row.setColumn('values', kwds)

        return

    def loadHadoopConfigurationValues(self, config):
        for configuration in config['hadoop configurations']:
            hostname = configuration.get('hostname', 'localhost')
            self.hadoopConfigurations()[hostname] = configuration
            pass
        return

    def addHadoopConfiguration(self, hadoopConfig):
        self.hadoopConfigurations()['hostname'] = hadoopConfig
        return

    def addHadoopConfigurationsToConfig(self, config):
        config['hadoop configurations'] = self.hadoopConfigurations().values()
        return

    def openConnection(self, name):

        # TODO:
        # should retrieve the value from the table
        # based upon the input parameter name
        kwds = CloudModule.defaultEC2Values()

        import boto
        import boto.ec2.regioninfo

        connection = boto.connect_ec2(
            aws_access_key_id=kwds[CloudModule.KEY_CONTROLLER_ACCESS_KEY],
            aws_secret_access_key=kwds[CloudModule.KEY_CONTROLLER_SECRET_KEY],
            is_secure=kwds['isSecure'],
            region=boto.ec2.regioninfo.RegionInfo(
                None, 
                kwds[CloudModule.KEY_CONTROLLER_SERVICE_NAME],
                kwds['host']
                ),
            port=kwds['port'],
            path=kwds['path']
        )

        return connection


    def _terminateVmAndThread(self):

        if True:
            raise NotImplementedError('_terminateVmAndThread')

        # start a thread that will wait to 
        thread = CloudModule.Thread(
            functools.partial(
                self.threadpool().dismissWorker,
                callback=self._removeVmEntryOfThread
            )
        )
        thread.start()
        return


    def _removeVmEntryOfThread(self, workerThread):

        # get the image id for the thread
        theFilter = RelationalModule.ColumnValueFilter(
            'Thread',
            FilterModule.IdentityFilter(workerThread)
        )
        instanceIds = RelationalModule.Table.reduceRetrieve(
            self.virtualMachineTable(),
            theFilter,
            ['Instance ID']
        )
        if not len(instanceIds):
            raise ValueError('Could not find any VMs assigned to thread %s' % 
                             workerThread)

        # remove the entry from the database
        # connection = self.openConnection('eucalyptus')
        # instances = connection.terminate_instances(instanceIds)
        self.terminateVmInstanceUsingIds(instanceIds)

        # now remove the rows
        self.virtualMachineTable().removeRows(theFilter)

        return


    def terminateVmInstance(self, instance):
        id = instance.id
        return self.terminateVmInstanceUsingIds([id])

    def terminateVmInstanceUsingIds(self, instanceIds):

        # remove the entry from the database
        connection = self.openConnection('eucalyptus')
        terminatedInstances = connection.terminate_instances(instanceIds)

        return


    def provisionVM(self, name, keyPair, imageId):

        # TODO:
        # request the machine be provisioned
        # image_id = None
        # TODO: switch image_id to be configurable

        kernel_id = None
        ramdisk_id = None
        min_count = 1
        max_count = 1
        instance_type = 'm1.small' 
        group_names = [] 
        user_data = None
        addressing_type = None
        zone = None

        connection = self.openConnection(name)

        reservation = connection.run_instances(
            image_id = imageId,
            min_count = min_count,
            max_count = max_count,
            key_name = keyPair,
            security_groups = group_names,
            user_data = user_data,
            addressing_type = addressing_type,
            instance_type = instance_type,
            placement = zone,
            kernel_id = kernel_id,
            ramdisk_id = ramdisk_id)


        # TODO:
        # add an entry into the table

        numInstances = len(reservation.instances)
        if numInstances is not 1:
            raise NotImplementedError('expected 1 instance, got %s' % 
                                      numInstances)
        instance = reservation.instances[0]

        return instance


    def unassignExecuteEnvironmentFromVmInstance(self, 
                                                 vmInstance, 
                                                 executeEnvironment=None):

        filter = RelationalModule.ColumnValueFilter(
            'Instance ID',
            FilterModule.EquivalenceFilter(vmInstance)
        )

        # TODO:
        # should enable removal of only a single row
        self.executeEnvironmentTable().removeRows(filter)
        return


    def assignExecuteEnvironmentForVmInstance(self, serviceAPI, vmInstance):

        filter = RelationalModule.ColumnValueFilter(
            'Instance ID',
            FilterModule.EquivalenceFilter(vmInstance)
        )
        credentials = self.getCloudControllerCredentialsForAPI(serviceAPI)

        for host, key in self.virtualMachineTable().retrieve(filter, ['IP', 'Key name']):
            if not key == credentials['user key pair']:
                logging.debug('key pair does not match')
                continue

            # create the env
            env = ShellModule.SecureShell()
            env.user('root')
            env.keyfile(credentials['identity file'])
            env.hostname(host)

            # add to the execute environment table 
            row = self.executeEnvironmentTable().addRow()
            row.setColumn('Execute environment', env)
            row.setColumn('Instance ID', vmInstance)

            return env

        raise KeyError('no instance with id %s found' % vmInstance)


    def assignThreadForExecuteEnvironment(self, threadPoolID, executeEnvironment):

        threadpool = self.getThreadPoolUsingId(threadPoolID)

        workerThread = threadpool.assignWorker()
        workerThread.executeEnvironment(executeEnvironment)

        row = self.threadTable().addRow()
        row.setColumn('Thread', workerThread)
        row.setColumn('Execute environment', executeEnvironment)

        return workerThread

    def getServiceApiFromVmInstance(self, vmInstance):
        filter = RelationalModule.ColumnValueFilter(
            'Instance ID',
            FilterModule.EquivalenceFilter(vmInstance)
        )

        apis = RelationalModule.Table.reduceRetrieve(
            self.virtualMachineTable(),
            filter,
            ['API'],
            []
        )
        if len(apis) is not 1:
            raise NotImplementedError(
                'not implemented for a vmInstance to have %s APIs' % len(apis))

        return apis[0]


    def getExecuteEnvironmentsFromVmInstance(self, vmInstance):

        filter = RelationalModule.ColumnValueFilter(
            'Instance ID',
            FilterModule.EquivalenceFilter(vmInstance)
        )

        executeEnvironments = RelationalModule.Table.reduceRetrieve(
            self.executeEnvironmentTable(),
            filter,
            ['Execute environment'],
            []
        )
        return executeEnvironments


    def unassignThreadFromVmInstance(self, threadPoolId, instance):
        """
        # TODO:
        # should be able to pull threadPoolId from the row as well
        """
        executeEnvironments = self.getExecuteEnvironmentsFromVmInstance(instance)

        self.unassignThreadFromExecuteEnvironment(
            threadPoolId, executeEnvironments[0])
        return


    def getThreadsFromExecuteEnvironment(self, executeEnvironment):
        filter = RelationalModule.ColumnValueFilter(
            'Execute environment',
            FilterModule.IdentityFilter(executeEnvironment)
        )
        threads = RelationalModule.Table.reduceRetrieve(
            self.threadTable(),
            filter,
            ['Thread'],
            []
        )
        return threads


    def unassignThreadFromExecuteEnvironment(self, threadPoolId, executeEnvironment):

        threads = self.getThreadsFromExecuteEnvironment(executeEnvironment)

        threadPool = self.getThreadPoolUsingId(threadPoolId)
        threadPool.dismissWorker(worker=threads[0])
        return


    def executeCommand(self, command):

        success = False
        try:
            self.commandManager().do(command)
            success = True
        except CommandModule.ExecutionError, e:

            # TODO:
            # notify the user that the command has failed
            pass

        return success


    def getThreadPoolUsingRequest(self, request):

        threadPoolId = request.kwds['execute environment id']
        return self.getThreadPoolUsingId(threadPoolId)


    def getThreadPoolUsingId(self, threadPoolId):

        filter = RelationalModule.ColumnValueFilter(
            'id',
            FilterModule.IdentityFilter(threadPoolId)
        )

        threadpools = RelationalModule.Table.reduceRetrieve(
            self.threadPoolTable(),
            filter,
            ['threadPool'],
            []
        )

        if len(threadpools) is 0:
            raise ValueError('no thread pool for id %s' % threadPoolId)
        if len(threadpools) is not 1:
            raise ValueError('too many thread pools for id %s' % threadPoolId)

        return threadpools[0]


    def setThreadPool(self, id, threadpool):
        row = self.threadPoolTable().addRow()
        row.setColumn('id', id)
        row.setColumn('threadPool', threadpool)
        return


    def enqueueRequest(self, request, shouldWait=True):
        """
        we don't want to call the superclass
        because currently the automaton in the pomset library
        can handle only one threadpool
        and waits on that threadpool when executing a request
        """

        # set the tasks' automaton as self
        task = request.kwds['task']
        task.automaton(self)

        # TODO:
        # this should not be in the code for the Automaton class
        # and instead, be located in the caller
        # who should check if there's a canvas involved
        if hasattr(self.contextManager(), 'canvas'):
            canvas = self.contextManager().canvas
            definition = task.definition()

            parentTask = task.parentTask()
            if parentTask:
                if parentTask.definition() is definition:
                    # do nothing
                    # because this is a parameter sweep
                    # and we don't want the status of the children
                    # of overwrite the status of the parent
                    # which is actually what's being shown to the user
                    logging.debug("not configuring performer for child parameter sweep task %s for definition %s" % (task, definition.name()))
                    pass
                elif canvas.hasGuiObjectForDataNode(definition):
                    # setup the canvas gui object to listen for updates
                    # on the execution status
                    guiNode = canvas.getGuiObjectForDataNode(definition)
                    guiNode.configurePerformers(task)

                    logging.debug("configured performers for task %s (definition %s)" % (task, definition.name()))
                    pass
                else:
                    logging.debug("canvas does not have gui object for task %s's definition %s" % (task, definition.name()))
                    pass
                pass
            else:
                # this is the root task
                # need to configure performers to also watch this
                # and update application menus accordingly

                completionCallback = request.callback
                newCompletionCallback = currypy.Curry(
                    Automaton.taskNotifyParentOfCompletion,
                    notifyFunction = completionCallback,
                    contextManager = self.contextManager())
                request.callback = newCompletionCallback

                errorCallback = request.exc_callback
                newErrorCallback = currypy.Curry(
                    Automaton.taskNotifyParentOfError,
                    notifyFunction = errorCallback,
                    contextManager = self.contextManager())
                request.exc_callback = newErrorCallback

                pass
        else:
            logging.debug('context manager does not have reference to a canvas, most likely because we are executing the library bootstrap loader')

        logging.debug('enqueuing task %s' % task)
        AutomatonModule.Automaton.enqueueRequest(
            self, request, shouldWait=shouldWait)

        return


    def getPostExecuteCallbackFor(self, task):
        callback = Automaton.atomicTaskCompleteCallback
        if isinstance(task, TaskModule.CompositeTask):
            callback = Automaton.compositeTaskCompleteCallback

        return callback


    def getExecuteTaskFunction(self, task):
        return Automaton.doTask


    def startProcessEndedTasksThread(self):

        thread = CloudModule.Thread(self.processEndedTasks)
        thread.start()
        return


    def processEndedTasks(self):
        """
        threadpool requires that we call wait()
        so that we can be notified of upates of execution status
        so we put this in a separate thread
        otherwise the GUI will block
        """

        # TODO:
        # add a check to verify that this is the only one running
        logging.debug('starting processing ended tasks')
        self.shouldProcessEndedTasks(True)
        while self.shouldProcessEndedTasks():

            threadpools = RelationalModule.Table.reduceRetrieve(
                self.threadPoolTable(),
                FilterModule.TRUE_FILTER,
                ['threadPool'],
                []
            )
            for threadpool in threadpools:
                threadpool.wait()

            time.sleep(1)
            pass
        logging.debug('ending processing ended tasks')
        return


    def addValuesToRequestContextForBootstrapLoader(self, requestContext, *args, **kwds):
        AutomatonModule.Automaton.addValuesToRequestContextForBootstrapLoader(
            self, requestContext, *args, **kwds)
        requestContext['execute environment id'] = ID_EXECUTE_LOCAL
        return


    # END class Automaton
    pass
