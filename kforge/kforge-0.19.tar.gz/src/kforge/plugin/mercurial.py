"""
KForge mercurial (hg) plugin.

Enabling this plugin allows KForge project administrators to create Mercurial
services.

Platform dependencies:

   * Mercurial. The Mercurial software is used to create, access, and update service repositories. For example, on Debian, the mercurial package must be installed.

KForge configuration file:

   * You may wish to set the path to the Mercurial admin script.

[mercurial]
admin_script = hg

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable mercurial
  $ kforge-admin plugin show mercurial
  $ kforge-admin plugin disable mercurial

"""
# Todo: Fix the helpMessage so it's https when necessary.
import os
import commands
import shutil
from StringIO import StringIO
import tarfile

import kforge.plugin.base
import kforge.utils.backup
from kforge.dictionarywords import *

# The implementation of Apache configuration follows:
# http://www.selenic.com/mercurial/wiki/index.cgi/PublishingRepositories

class Plugin(kforge.plugin.base.ServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = MercurialUtils(self.dictionary[MERCURIAL_ADMIN_SCRIPT])

    def checkDependencies(self):
        errors = []
        hgPath = self.dictionary[MERCURIAL_ADMIN_SCRIPT]
        cmd = 'which %s' % hgPath
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't find Mercurial admin script '%s' on path." % hgPath)
        return errors

    def showDepends(self):
        hgPath = self.dictionary[MERCURIAL_ADMIN_SCRIPT]
        cmd = 'which %s' % hgPath
        (status, output) = commands.getstatusoutput(cmd)
        return [
            "Mercurial admin: %s" % (status and "Not found!" or ("Found OK. %s" % output)),
        ]

    showDepends = classmethod(showDepends)
    
    # From mercurial 0.9.5
    hgweb_cgi = \
'''#!/usr/bin/env python

# send python tracebacks to the browser if an error occurs:
import cgitb
cgitb.enable()

# If you'd like to serve pages with UTF-8 instead of your default
# locale charset, you can do so by uncommenting the following lines.
# Note that this will cause your .hgrc files to be interpreted in
# UTF-8 and all your repo files to be displayed using UTF-8.
#
import os
os.environ["HGENCODING"] = "UTF-8"

from mercurial.hgweb.hgweb_mod import hgweb
from mercurial.hgweb.request import wsgiapplication
import mercurial.hgweb.wsgicgi as wsgicgi

def make_web_app():
    return hgweb("/path/to/repo", "repository name")

wsgicgi.launch(wsgiapplication(make_web_app))
'''

    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            servicePath = service.getDirPath()
            self.assertNotFileForPath(servicePath)
            self.utils.createRepo(servicePath)
            self.assertFileForPath(servicePath)
            msg = 'MercurialPlugin: Created service %s on path: %s)' % (
                service, servicePath
            )
            self.log(msg)
    
    def assertNotFileForPath(self, path):
        if os.path.exists(path):
            message = "Mercurial service exists on path: %s" % path
            self.logger.error(message)
            raise Exception(message)

    def assertFileForPath(self, path):
        if not os.path.exists(path):
            message = "Mercurial service doesn't exist on path %s" % path
            self.logger.error(message)
            raise Exception(message)
    
    def getApacheConfig(self, service):
        serviceName = service.project.name + '-' + service.name
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[MERCURIAL_WSGI_SCRIPT_PATH]
            config = """
WSGIScriptAlias %(urlPath)s """ + wsgiScriptPath + """
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup """ + self.dictionary[MERCURIAL_WSGI_PROCESS_GROUP] + """
<Location %(urlPath)s>
SetEnv KFORGE_MERCURIAL_REPO_PATH %(fileSystemPath)s/repo
SetEnv KFORGE_MERCURIAL_REPO_NAME """ + serviceName + """
WSGIPassAuthorization On
</Location>
"""
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            cgiScriptPath = self.dictionary[MERCURIAL_CGI_SCRIPT_PATH]
            config = """
ScriptAlias %(urlPath)s """ + cgiScriptPath + """
<Location %(urlPath)s>
SetEnv KFORGE_MERCURIAL_REPO_PATH %(fileSystemPath)s/repo
SetEnv KFORGE_MERCURIAL_REPO_NAME """ + serviceName + """
%(accessControl)s
</Location>"""
        return config

    def buildWsgiFile(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[MERCURIAL_WSGI_SCRIPT_PATH]
            wsgiScriptContent = self.createWsgiScriptContent()
            self.writeFile(wsgiScriptPath, wsgiScriptContent, 'Mercurial WSGI script')

    def createWsgiScriptBody(self, pythonPathActivation):
        wsgiScriptBody = """
# KForge auto-generated Mercurial WSGI File.

import os
import sys

"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """

from mercurial.hgweb import hgweb
os.environ["HGENCODING"] = "UTF-8"

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"

        wsgiScriptBody += """
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    repositoryPath = environ.pop('KFORGE_MERCURIAL_REPO_PATH')
    repositoryName = environ.pop('KFORGE_MERCURIAL_REPO_NAME')
    accessapplication = WsgiAccessControlHandler(hgweb(repositoryPath, repositoryName))
    return accessapplication(environ, start_response)
"""    
        return wsgiScriptBody

    def buildCgiFile(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            cgiScriptPath = self.dictionary[MERCURIAL_CGI_SCRIPT_PATH]
            cgiScriptContent = self.createCgiScriptContent()
            self.writeFile(cgiScriptPath, cgiScriptContent, 'Mercurial CGI script')
            # Make CGI script executable.
            os.chmod(cgiScriptPath, 0755)

    def createCgiScriptContent(self):
        # Todo: Fixup so it uses virtualenv or PYTHONPATH, if they exist.
        cgiScriptContent = '''#!/usr/bin/env python

import os
os.environ["HGENCODING"] = "UTF-8"

from mercurial.hgweb.hgweb_mod import hgweb
from mercurial.hgweb.request import wsgiapplication
import mercurial.hgweb.wsgicgi as wsgicgi

def make_web_app():
    repositoryPath = os.environ.pop('KFORGE_MERCURIAL_REPO_PATH')
    repositoryName = os.environ.pop('KFORGE_MERCURIAL_REPO_NAME')
    return hgweb(repositoryPath, repositoryName)

wsgicgi.launch(wsgiapplication(make_web_app))
'''
        return cgiScriptContent

    def backup(self, service, backupPathBuilder):
        path = service.getDirPath()
        backupPath = backupPathBuilder.getServicePath(service)
        self.utils.backup(path, backupPath)

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
<p>This service provides a single Mercurial repository. To find out more about <a href="http://mercurial.selenic.com/">Mercurial</a> see the <a href="http://mercurial.selenic.com/guide/">Mercurial Guide</a>.</p>
<p>You can access the material in the repository the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the repository with your favorite Web browser.</li>
    <li>Access the repository with a suitable Mercurial client via HTTP.</li>'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
    <li>Access the repository with a suitable Mercurial client via SSH.</li>'''
        helpMessage += '''
</ul>

<p>See the <a href="http://mercurial.selenic.com/guide/">Mercurial Guide</a> for more information on the Mercurial command line client. Graphical user interfaces for Mercurial and Mercurial plugins for rapid development environments such as Eclipse are also available.

<h4>HTTP Access</h4>
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s

</pre></b></p>
<p>Configure HTTP authentication by adding the following to your <code>~/.hgrc</code> file. Create the <code>~/.hgrc</code> file if necessary:
<pre>
[ui]
username = FULLNAME <you@example.com>

[auth]
kforge.prefix = http://DOMAINNAME/
kforge.username = USERNAME
kforge.password = PASSWORD

</pre></p>
<p>If you are using the command line client, you would do:
<pre>$ hg clone %(httpUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:</p>
<pre>$ hg push

</pre>
'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
<h4>SSH Access</h4>
<p>The repository is available via SSH here:
<b><pre>%(sshUrl)s

</pre></b></p>
<p>If necessary, register your SSH public key with your account.</p>
<p>If you are using the command line client, you would do:
<pre>$ hg clone %(sshUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:
<pre>$ hg push

</pre></p>

'''
        msg = helpMessage % values
        return msg


class MercurialUtils(object):
   
    def __init__(self, adminScriptPath='hg'):
        self.adminScriptPath = adminScriptPath
 
    def createRepo(self, servicePath):
        repoPath = os.path.join(servicePath, 'repo')
        if not os.path.exists(repoPath):
            os.makedirs(repoPath)
        self.initRepo(repoPath)
        self.pushEnableRepo(repoPath)

    def initRepo(self, repoPath):
        cmd = '%s init %s' % (self.adminScriptPath, repoPath)
        s, o = commands.getstatusoutput(cmd)
        if s:
            msg = 'Could not create mercurial repository: %s: %s' % (cmd, o)
            raise Exception(msg)

    def pushEnableRepo(self, repoPath):
        hgrcFileContent = '''
[web]
allow_push = *
# allow pushing over http as well as https 
push_ssl = false
'''
        hgrcFilePath = os.path.join(repoPath, '.hg', 'hgrc')
        hgrcFile = open(hgrcFilePath, 'w')
        hgrcFile.write(hgrcFileContent)
        hgrcFile.close()

    def delete(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def backup(self, path, dest):
        dest = dest + '.tgz'
        tar = tarfile.open(dest, 'w:gz')
        tar.add(path)
        tar.close()

