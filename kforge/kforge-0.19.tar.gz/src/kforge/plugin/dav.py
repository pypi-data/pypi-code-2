"""
KForge dav Plugin.

Enabling this plugin gives dav access to the project directory and all
subdirectories.

## Installation ##

1. Dependencies. To create services using this plugin you must have installed
   the following external applications:

   * Apache dav module (mod_dav). Note that on many systems this will be
     installed by default.

2. KForge config file. You do not need to add anything to the KForge config
   file.
"""
import os
import shutil

import kforge.plugin.base
from dm.strategy import FindProtectionObject
from kforge.dictionarywords import *

class Plugin(kforge.plugin.base.SingleServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.paths.assertProjectFolder(service.project)

    def getApacheConfig(self, service):
        projectPath = self.paths.getProjectPath(service.project)
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            config = """
WSGIScriptAlias %(urlPath)s """ + self.dictionary[DAV_WSGI_SCRIPT_PATH] + """
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup """ + self.dictionary[DAV_WSGI_PROCESS_GROUP] + """
<Location %(urlPath)s>
SetEnv KFORGE_DAV_FILESYSTEM_PATH """ + projectPath + """
SetEnv KFORGE_DAV_MOUNT_PATH %(urlPath)s
WSGIPassAuthorization On
</Location>
"""
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            config = 'Alias %(urlPath)s ' + projectPath
            # 'ForceType text/plain' so DAV interprets all file types as text.
            config += """
    <Location %(urlPath)s>
    DAV On
    Options +Indexes
# Remove use DirectoryIndex
    DirectoryIndex none.none.none
    ForceType text/plain

    %(accessControl)s
    </Location>"""
        return config
    
    def onCreate(self):
        # Todo: Pull various bits of access controller setup together under the name 'setupAccessControl'.
        super(Plugin, self).onCreate()
        protectionObject = FindProtectionObject(self.domainObject).find()
        # Don't allow Friends to read the DAV plugin, as it gives access to all project data.
        permission = protectionObject.permissions[self.registry.actions['Read']]
        friend = self.registry.roles['Friend']
        if permission in friend.grants:
            grant = friend.grants[permission]
            grant.delete()
        # Don't allow Developers to write to the DAV plugin, as it gives access to all project data.
        permission = protectionObject.permissions[self.registry.actions['Update']]
        friend = self.registry.roles['Developer']
        if permission in friend.grants:
            grant = friend.grants[permission]
            grant.delete()

    def buildWsgiFile(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[DAV_WSGI_SCRIPT_PATH]
            wsgiScriptContent = self.createWsgiScriptContent()
            self.writeFile(wsgiScriptPath, wsgiScriptContent, 'DAV WSGI script')

    def createWsgiScriptBody(self, pythonPathActivation):
        wsgiScriptBody = """
# KForge auto-generated DAV WSGI File.

import os
import sys

"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """

from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"

        wsgiScriptBody += """
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    davConfig = DEFAULT_CONFIG.copy()
    davConfig.update({
        'provider_mapping': {
            '/': environ.pop('KFORGE_DAV_FILESYSTEM_PATH'),
        },
        'mount_path': environ.pop('KFORGE_DAV_MOUNT_PATH'),
    })
    accessapplication = WsgiAccessControlHandler(WsgiDAVApp(davConfig))
    return accessapplication(environ, start_response)
"""    
        return wsgiScriptBody

    def getUserHelp(self, service, serviceLocation):
        values = {'httpUrl' : serviceLocation}
        if 'ssh' in self.registry.plugins:
            import getpass
            sshUrl = 'ssh://%(sshUser)s@%(sshHost)s/%(project)s/%(service)s'
            sshUrl %= {
                'sshUser': self.dictionary[SSH_USER_NAME] or getpass.getuser(),
                'sshHost': self.dictionary[SSH_HOST_NAME],
                'project': service.project.name,
                'service': service.name
            }
            values['sshUrl'] = sshUrl
        helpMessage = '''
<p>This service provides a WebDAV filesystem. To find out more about <a href="http://www.webdav.org/">WebDAV</a> see the <a href="http://www.webdav.org/other/faq.html">WebDAV FAQ</a>.</p>
<p>You can access the material in the filesystem in the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the material online by following the link to the WebDAV filesystem in your browser.</li>
    <li>Update the material online by opening the WebDAV filesystem in a WebDAV enabled application such as Internet Explorer, Konqueror and Nautilus.</li>
    <li>Mount the WebDAV filesystem within your local filesystem from the command line.</li>
</ul>

<h4>HTTP Access</h4>
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s/

</pre></b>

</p>
<h4>Mounting the Filesystem</h4>
<p>If you wish to mount the WebDAV filesystem within your local filesystem from the command line client, you would do:
<pre>$ mkdir mydavfs
$ sudo mount -t davfs %(httpUrl)s mydavfs -o uid=$USER
Please enter the username to authenticate with server
%(httpUrl)s or hit enter for none.
  Username: KFORGEUSER
Please enter the password to authenticate user KFORGEUSER with server
%(httpUrl)s or hit enter for none.
  Password: </pre>
</p>
<p>To unmount the filesystem, you would do:
<pre>$ sudo umount mydavfs </pre>
</p>
'''
        msg = helpMessage % values
        return msg

