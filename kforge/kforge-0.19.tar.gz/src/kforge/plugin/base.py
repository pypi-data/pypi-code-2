import dm.plugin.base
import os
from dm.strategy import FindProtectionObject
from dm.strategy import CreateProtectionObject
from dm.dictionarywords import APACHE_RELOAD_CMD
import dm.times
from kforge.dictionarywords import *

class AbstractServicePlugin(dm.plugin.base.PluginBase):
    """
    Service plugins deploy adapted software applications as project services.
    """ 

    def checkDependencies(self):
        errors = []
        return errors

    def showDepends(self):
        return [
        ]
    showDepends = classmethod(showDepends)

    def getMaxServicesPerProject(self):
        raise Exception("Abstract method not implemented.")

    def isOurs(self, service):
        "Checks whether a service belongs to this plugin."
        return service and service.plugin and \
            service.plugin.name == self.domainObject.name
    
    def ensureProjectPluginDirectoryExists(self, service):
        self.assertServicesFolder(service)

    def assertServicesFolder(self, service):
        path = self.paths.getProjectPluginPath(service.project, service.plugin)
        self.paths.assertFolder(path, 'project %s services' % service.plugin.name)
    
    def backup(self, service, backupPathBuilder):
        """Backup the plugged-in application service.

        @backupPathBuilder: any object supporting a function getServicePath.
        """
        pass
    
    def onCreate(self):
        createObject = CreateProtectionObject(self.domainObject)
        protectionObject = createObject.create()
        import kforge.command
        cmd = kforge.command.GrantStandardProjectAccess(protectionObject)
        cmd.execute()
    
    def onDelete(self):
        findObject = FindProtectionObject(self.domainObject)
        protectionObject = findObject.find()
        if protectionObject:
            protectionObject.delete()

    def getUserHelp(self, service, serviceLocation):
        """Provide a service user help message.
        """
        return ''

    def getStatusMessage(self, service):
        """Provide a service status message.
        """
        # Todo: Check at least whether HEAD gets a 404?
        if not self.dictionary[APACHE_RELOAD_CMD]:
            msg = "Created"
        elif service.isSystemUpSinceModified():
            msg = "Running"
        else:
            msg = "Waiting"
        return msg

    def getApacheConfigCommon(self):
        """
        Return a fragment of Apache config that is only needed once per plugin
        per virtual host (so common across all instances
        """
        return ''

    def getApacheConfig(self, service):
        """
        Returns a fragment of apache config appropriate for the plugin instance
        The fragment can use the variables defined in the dictionary in
            ApacheConfigBuilder.getServiceSection
        by inserting them as %(var_name)s
        Alternatively it can build the config itself
        """
        return ''

    def buildWsgiFile(self):
        pass

    def buildCgiFile(self):
        pass

    def createWsgiScriptContent(self):
        pythonVirtualenvActivation = self.createVirtualenvActivation()
        if not pythonVirtualenvActivation:
            pythonPathActivation = self.createPythonPathActivation()
        else:
            pythonPathActivation = ''
        wsgiScriptBody = self.createWsgiScriptBody(pythonPathActivation)
        wsgiScriptContent = pythonVirtualenvActivation + wsgiScriptBody
        return wsgiScriptContent

    def createWsgiScriptBody(self, pythonPathActivation):
        raise Exception, "Method not implemented on %s" % self

    def createPythonPathActivation(self):
        pythonPathActivation = ''
        if self.dictionary[PYTHONPATH]:
            pythonPathActivation = """
for path in %(PYTHON_PATH_LIST)s:
    if path not in sys.path:
        sys.path.append(path)

"""         % {
                'PYTHON_PATH_LIST': self.dictionary[PYTHONPATH].split(':'),
            }
        return pythonPathActivation

    def createVirtualenvActivation(self):
        virtualenvActivation = ''
        if self.dictionary[VIRTUALENVBIN_PATH]:
            # Todo: Revisit in favour of 
            # http://code.google.com/p/modwsgi/wiki/VirtualEnvironments.
            # would just need to know "the full path to the 'site-packages'
            # directory for the virtual environment", but that is available 
            # as os.path.dirname(os.__file__)? Need to baseline WSGI with
            # WSGIPythonHome /usr/local/pythonenv/BASELINE in main Apache
            # configuration. So would have to add that to install guides?
            virtualenvActivation = """activate_this = '%(ACTIVATE_THIS_PATH)s'
execfile(activate_this, dict(__file__=activate_this))

"""         % {
                'ACTIVATE_THIS_PATH': os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'activate_this.py')
            }
        return virtualenvActivation

    # Todo: Move this to 'Filesystem'?
    def writeFile(self, path, content, purpose):
        path = os.path.normpath(path)
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.makedirs(parent)
        content = content.encode('utf-8', 'ignore')
        # Todo: Make this filewriting safer.
        file = open(path, 'w')
        file.write(content)
        file.close()
        self.logger.info("Wrote %s on path: %s" % (purpose, path))

    def onServicePurge(self, service):
        if self.isOurs(service):
            self.trashServiceFolder(service)

    def trashServiceFolder(self, service):
        servicePath = self.paths.getServicePath(service)
        msg = "%sPlugin: Trashing service folder: %s" % (self.domainObject.name.capitalize(), servicePath)
        self.logger.info(msg)
        if not os.path.exists(servicePath):
            return
        self.paths.assertTrashFolder()
        trashPath = self.paths.getTrashPath()
        trashBase = os.path.join(trashPath, str(service.id))
        trashNew = trashBase
        trashIndex = 0
        while os.path.exists(trashNew):
            trashNew = "%s.%s" % (trashBase, trashIndex)
            trashIndex += 1
        try:
            import shutil
            shutil.move(servicePath, trashNew)
        except Exception, inst:
            msg = "Couldn't move service files into trash: tried moving %s to %s: %s" % (
                servicePath, trashNew, inst
            )


class ServicePlugin(AbstractServicePlugin):
    
    def getMaxServicesPerProject(self):
        return None


class SingleServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 1


class NonServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 0

