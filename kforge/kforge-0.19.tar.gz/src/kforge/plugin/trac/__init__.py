"""KForge Trac Plugin

Enabling this plugin allows KForge project administrators to create Trac project services.

Creating services with this plugin requires:

  * Trac. The 'trac-admin' command is used to create Trac environments. It depends on the Trac Python library.  A set of Trac templates is also required if the version of Trac is less than 0.11.

Providing access to this plugin's services requires:

  * Trac. The Trac Python library is used to handle requests. Trac's htdocs is required for older versions.
  * Apache. The mod_python Apache module is used by KForge to provide access to Trac through Apache. For example, on Debian the libapache2-mod-python package must be installed and enabled.

Using Git repositories with Trac projects (optional) requires:

  * Trac's Git plugin. For example, on Debian the trac-git package can be installed.

If using Trac v0.11 or later, you do not need to add anything to the KForge config file. Otherwise, if necessary add the following section to your KForge configuration file. Set the 'admin_script' if trac-admin is available on the executable path. Set the 'templates_path' if you are using a version of Trac earlier than version 0.11. Set the 'htdocs_path' if your Trac pages aren't finding their static resources (style sheets, images, etc.). Please note, if you are using Trac v0.11 or later, this section is no longer required.

[trac]
# Path to Trac admin script.
#admin_script = /path/to/trac-admin
# Path to trac templates (only for < 0.11).
#templates_path = /usr/share/trac/templates
# Path to htdocs files (will be served at /trac).
#htdocs_path = /usr/share/trac/htdocs

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable trac
  $ kforge-admin plugin show trac
  $ kforge-admin plugin disable trac

[Optional] It is highly recommended that you also install the official WebAdmin trac plugin: <http://trac.edgewall.org/wiki/WebAdmin>. Full instructions can be found at that link (NB: as of trac v0.11 WebAdmin is part of trac core and therefore does not need to be separately installed).  WebAdmin allows users to administer most aspects of trac (trac specific permissions, template links, etc etc) from the web rather than needing access to the trac-admin command line utility.

"""
from kforge.dictionarywords import *
import kforge.plugin.base
from kforge.plugin.trac.command import TracProjectEnvironmentCreate
from kforge.plugin.trac.command import AddAdminUserCommand
from kforge.plugin.trac.command import RemoveAdminUserCommand
from kforge.plugin.trac.command import IsAdminUserCommand
from kforge.plugin.trac.dom import TracProject
import os
import distutils.version
import commands

class Plugin(kforge.plugin.base.ServicePlugin):
    "Trac plugin."

    extendsDomainModel = True
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)

    def getRegister(self):
        domainClass = self.registry.getDomainClass('TracProject')
        return domainClass.createRegister(keyName='service')

    def checkDependencies(self):
        errors = []
        adminPath = self.dictionary[TRAC_ADMIN_SCRIPT]
        cmd = 'which %s' % adminPath
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't find Trac admin script '%s' on path." % adminPath)
        try:
            import trac
        except:
            errors.append("Couldn't import Trac Python library.")
        else:
            tracVersion = distutils.version.LooseVersion(trac.__version__)
            v0_9 = distutils.version.LooseVersion('0.9')
            v0_11 = distutils.version.LooseVersion('0.11')
            if tracVersion <= v0_11:
                if not self.dictionary[TRAC_TEMPLATES_PATH]:
                    errors.append("The path to Trac templates has not been set.")
                elif not os.path.exists(self.dictionary[TRAC_TEMPLATES_PATH]):
                    errors.append("Couldn't find Trac templates folder: %s" % (self.dictionary[TRAC_TEMPLATES_PATH]))
            if self.dictionary[TRAC_HTDOCS_PATH]:
                if not os.path.exists(self.dictionary[TRAC_HTDOCS_PATH]):
                    errors.append("Couldn't find Trac htdocs folder: %s" % (self.dictionary[TRAC_HTDOCS_PATH]))
        return errors

    def showDepends(self):
        (whichTracadminStatus, whichTracadminOutput) = commands.getstatusoutput('which %s' % self.dictionary[TRAC_ADMIN_SCRIPT])
        (whichTractemplatesStatus, whichTractemplatesOutput) = commands.getstatusoutput('which %s' % self.dictionary[TRAC_TEMPLATES_PATH])
        (whichTrachtdocsStatus, whichTrachtdocsOutput) = commands.getstatusoutput('which %s' % self.dictionary[TRAC_HTDOCS_PATH])
        (importTracStatus, importTracOutput) = commands.getstatusoutput('python -c "import trac; print trac.__path__[0]"')
        messages = [
            "Trac admin: %s" % (whichTracadminStatus and "Not found!" or ("Found OK. %s" % whichTracadminOutput)),
        ]
        msg = "Trac Python library: "
        if not importTracStatus:
            import trac
            tracVersion = distutils.version.LooseVersion(trac.__version__)
            msg += "Found OK. Trac %s in %s." % (tracVersion, importTracOutput)
            messages.append(msg)
            v0_9 = distutils.version.LooseVersion('0.9')
            v0_11 = distutils.version.LooseVersion('0.11')
            if tracVersion <= v0_11:
                msg = "Trac templates: "
                if not self.dictionary[TRAC_TEMPLATES_PATH]:
                    msg += "Not set."
                elif not os.path.exists(self.dictionary[TRAC_TEMPLATES_PATH]):
                    msg += "Not found!: %s" % self.dictionary[TRAC_TEMPLATES_PATH]
                else:
                    msg += "Found OK. %s" % self.dictionary[TRAC_TEMPLATES_PATH]
                messages.append(msg)
        else:
            msg += "Not found! %s" % importTracOutput
            messages.append(msg)
            if self.dictionary[TRAC_TEMPLATES_PATH]:
                msg = "Trac templates: "
                if not os.path.exists(self.dictionary[TRAC_TEMPLATES_PATH]):
                    msg += "Not found!: %s" % self.dictionary[TRAC_TEMPLATES_PATH]
                else:
                    msg += "Found OK. %s" % self.dictionary[TRAC_TEMPLATES_PATH]
                messages.append(msg)
        if self.dictionary[TRAC_HTDOCS_PATH]:
            msg = "Trac htdocs: "
            if not os.path.exists(self.dictionary[TRAC_HTDOCS_PATH]):
                msg += "Not found!: %s" % self.dictionary[TRAC_HTDOCS_PATH]
            else:
                msg += "Found OK. %s" % self.dictionary[TRAC_HTDOCS_PATH]
            messages.append(msg)
        return messages

    showDepends = classmethod(showDepends)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.paths.assertServiceFolder(service)
            self.register.create(service)
 
    def onServicePurge(self, service):
        try:
            if self.isOurs(service):
                if service in self.register:
                    tracProject = self.register[service]
                    # Todo: Delete the tracProject now? Or never?
                    tracProject.service = None
                    tracProject.svn = None
                    tracProject.save()
        finally:
            super(Plugin, self).onServicePurge(service)

    def onTracProjectUpdate(self, tracProject):
        if tracProject.service and tracProject.svn \
        and not tracProject.isEnvironmentInitialised:
            # Only creates the trac environment once an svn is selected.
            #  - afterwards, no other adjustments are made (currently)
            command = TracProjectEnvironmentCreate(tracProject)
            command.execute()
            # Todo: Move this to onMemberCreate() and onMemberDelete()?
            for member in tracProject.service.project.members:
                if member.role.name == 'Administrator':
                    cmd = AddAdminUserCommand(tracProject, member.person.name)
                    cmd.execute()
    
    # [[TODO: enable (uncomment) this code so that trac subsystem permissions
    # track project permissions.
    # disabled for the time being because not yet under test]]
#    def onMemberUpdate(self, member):
#        if member.role.name == 'Administrator':
#            for service in member.project.services:
#                if service.plugin.name == 'trac':
#                    tracRegister = self.getRegister()
#                    tracProject = tracRegister[service]
#                    # be lazy and don't check whether already an admin
#                    # (errors only result in logged warning)
#                    cmd = AddAdminUserCommand(tracProject, member.person.name)
#                    cmd.execute()
#        else: # not an administrator
#            for service in member.project.services:
#                if service.plugin.name == 'trac':
#                    tracRegister = self.getRegister()
#                    tracProject = tracRegister[service]
#                    # be lazy and don't check whether already an admin
#                    # (errors only result in logged warning)
#                    cmd = RemoveAdminUserCommand(tracProject, member.person.name)
#                    cmd.execute()
#        
#    def onMemberDelete(self, member):
#        for service in member.project.services:
#            if service.plugin.name == 'trac':
#                tracRegister = self.getRegister()
#                tracProject = tracRegister[service]
#                # be lazy and don't check whether already an admin
#                # (errors only result in logged warning)
#                cmd = RemoveAdminUserCommand(tracProject, member.person.name)
#                cmd.execute()
    
    def listDependencies(self):
        dependencies = super(Plugin, self).listDependencies()
        dependencies.append('svn')
        return dependencies
        
    listDependencies = classmethod(listDependencies)

    def getMetaDomainObject(self):
        return TracProject.meta

    def getStatusMessage(self, service):
        """Provide a service status message.
        """
        if service in self.register:
            tracProject = self.register[service]
            if tracProject.isEnvironmentInitialised:
                msg = super(Plugin, self).getStatusMessage(service)
            else:
                msg = "Waiting for repository, please update service."
        else:
            msg = "Error: No 'trac project' object in model."
        return msg

    def getApacheConfigCommon(self):
        return ""
    
    def buildWsgiFile(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[TRAC_WSGI_SCRIPT_PATH]
            wsgiScriptContent = self.createWsgiScriptContent()
            self.writeFile(wsgiScriptPath, wsgiScriptContent, 'Trac WSGI script')

    def createWsgiScriptBody(self, pythonPathActivation):
        wsgiScriptBody = """
# KForge auto-generated Trac WSGI File.

import os
import sys

"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"

        wsgiScriptBody += """
    if 'PYTHON_EGG_CACHE' in environ:
        os.environ['PYTHON_EGG_CACHE'] = environ['PYTHON_EGG_CACHE']
    elif 'trac.env_path' in environ:
        os.environ['PYTHON_EGG_CACHE'] = os.path.join(environ['trac.env_path'],
                                                      '.egg-cache')
    elif 'trac.env_path_parent_dir' in environ:
        os.environ['PYTHON_EGG_CACHE'] = os.path.join(environ['trac.env_path_parent_dir'],
                                                      '.egg-cache')
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    from trac.web.main import dispatch_request
    access_control = WsgiAccessControlHandler(dispatch_request)
    return access_control(environ, start_response)
"""    
        return wsgiScriptBody

    def getApacheConfig(self, service):
        # Todo: Don't include Apache config for Trac services that don't have an environment.
        if not service or not service.name:
            return ""
        import distutils
        # import inline so that access to docstring works
        import trac
        tracVersion = distutils.version.LooseVersion(trac.__version__)
        v0_9 = distutils.version.LooseVersion('0.9')
        tracHtdocsPath = self.dictionary[TRAC_HTDOCS_PATH] 
        result = '' 
        if tracHtdocsPath:
            result += """
Alias %(urlPath)s/chrome """ + tracHtdocsPath + """
"""
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[TRAC_WSGI_SCRIPT_PATH]
            result += """
WSGIScriptAlias %(urlPath)s """ + wsgiScriptPath + """
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup """ + self.dictionary[TRAC_WSGI_PROCESS_GROUP] + """
<Location %(urlPath)s>
SetEnv trac.env_path %(fileSystemPath)s
WSGIPassAuthorization On
</Location>
"""
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            if self.dictionary[VIRTUALENVBIN_PATH]:
                tracHandlerName = 'kforgevirtualenvhandlers::trachandler'
            else:
                if tracVersion < v0_9:
                    tracHandlerName = 'trac.ModPythonHandler'
                else:
                    tracHandlerName = 'trac.web.modpython_frontend'
            result += """
<Location %(urlPath)s>
<IfModule mod_python.c>
SetHandler mod_python
PythonHandler """
            result += tracHandlerName
            result += """
PythonInterpreter main_interpreter
PythonOption TracEnv %(fileSystemPath)s
PythonOption TracUriRoot %(urlPath)s

%(accessControl)s
</IfModule>
</Location>"""
        return result
    
    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        os.system('%s %s hotcopy %s' % (self.dictionary[TRAC_ADMIN_SCRIPT], service.getDirPath(), backupPath))
