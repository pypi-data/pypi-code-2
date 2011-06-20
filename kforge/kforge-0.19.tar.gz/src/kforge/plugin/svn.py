"""KForge Subversion Plugin

Enabling this plugin allows KForge project administrators to create Subversion version control system services.

Creating services with this plugin requires:

  * Subversion. The 'svnadmin' command is used to create repositories.

Providing access to this plugin's services requires:

  * Apache. The mod_python, mod_dav, mod_dav_fs, and mod_dav_svn Apache modules are used to provide access to Subversion through Apache. For example, on Debian the libapache2-mod-python and libapache2-svn packages must be installed and enabled.

You do not need to add anything to the KForge config file.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable svn
  $ kforge-admin plugin show svn
  $ kforge-admin plugin disable svn
"""
import os
import commands
import shutil

import kforge.plugin.base
import kforge.utils.backup
from kforge.dictionary import *

class Plugin(kforge.plugin.base.ServicePlugin):
    "Subversion plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = SvnUtils()
   
    def checkDependencies(self):
        errors = []
        svnadminPath = self.dictionary[SVN_ADMIN_SCRIPT]
        cmd = 'which %s' % svnadminPath
        (status, output) = commands.getstatusoutput(cmd) 
        if status:
            errors.append("Couldn't find Subversion admin script '%s' on path." % svnadminPath)
        if not os.path.isdir(self.dictionary[SVN_VIEWVC_LIB_PATH]):
            errors.append("Couldn't find ViewVC library: %s" % self.dictionary[SVN_VIEWVC_LIB_PATH])
        if not os.path.isdir(self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]):
            errors.append("Couldn't find ViewVC templates: %s" % self.dictionary[SVN_VIEWVC_TEMPLATE_PATH])
        if not os.path.isdir(self.dictionary[SVN_VIEWVC_MEDIA_PATH]):
            errors.append("Couldn't find ViewVC static media: %s" % self.dictionary[SVN_VIEWVC_MEDIA_PATH])
        return errors

    def showDepends(self):
        svnadminPath = self.dictionary[SVN_ADMIN_SCRIPT]
        cmd = 'which %s' % svnadminPath
        (statusWhichSvnadmin, outputWhichSvnadmin) = commands.getstatusoutput(cmd) 

        hasViewvcLibrary= os.path.isdir(self.dictionary[SVN_VIEWVC_LIB_PATH])
        hasViewvcTemplate = os.path.isdir(self.dictionary[SVN_VIEWVC_TEMPLATE_PATH])
        hasViewvcMedia = os.path.isdir(self.dictionary[SVN_VIEWVC_MEDIA_PATH])
        return [
            "Subversion admin: %s" % (statusWhichSvnadmin and "Not found!" or ("Found OK. %s" % outputWhichSvnadmin)),
            "ViewVC library: %s" % (hasViewvcLibrary and ("Found OK. %s" % self.dictionary[SVN_VIEWVC_LIB_PATH]) or "Not found!"),
            "ViewVC template: %s" % (hasViewvcTemplate and ("Found OK. %s" % self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]) or "Not found!"),
            "ViewVC media: %s" % (hasViewvcMedia and ("Found OK. %s" % self.dictionary[SVN_VIEWVC_MEDIA_PATH]) or "Not found!"),
            "Apache dav module: %s" % "Please check this module is enabled.",
            "Apache dav_fs module: %s" % "Please check this module is enabled.",
            "Apache dav_svn module: %s" % "Please check this module is enabled.",
        ]
    showDepends = classmethod(showDepends)
 
    def onServiceCreate(self, service):
        if self.isOurs(service):
            servicePath = self.paths.getServicePath(service)
            msg = 'SvnPlugin: Creating new Subversion repository for %s: %s' % (
                service, servicePath
            )
            self.logger.info(msg)
            self.paths.assertServiceFolder(service)
            self.utils.createRepository(servicePath)

    def getApacheConfig(self, service):
        viewvcServicePathParent =  "%%(uriPrefix)s/%s/viewvc" % service.project.name
        viewvcServicePath =  "%s/%s" % (viewvcServicePathParent, service.name)
        viewvcMediaFolder = '/usr/share/viewvc/docroot'
        viewvcMediaFolder = self.dictionary[SVN_VIEWVC_MEDIA_PATH]
        # Only need this Alias directive once per project, but are generating
        # it for each service. So use AliasMatch so that Apache does not print warnings.
        # Same goes for the WSGIScript Alias, but Apache doesn't print warnings about that.
        # Todo: Fixup ViewVC static file configuration (perhaps make it common config,
        # and somehow setup the service environment to point to a common resource).

        viewvcRedirect = """

AliasMatch ^%(uriPrefix)s/"""+service.project.name+"/viewvc\/\*docroot\*((?!"+service.name+").*) "+viewvcMediaFolder+"""$1
<IfModule mod_rewrite.c>
RewriteEngine on
RewriteCond %%{HTTP_USER_AGENT}  Lynx               [OR]
RewriteCond %%{HTTP_USER_AGENT}  Mozilla            [OR]
RewriteCond %%{HTTP_USER_AGENT}  Links              [OR]
RewriteCond %%{HTTP_USER_AGENT}  w3m
RewriteRule ^%(urlPath)s$       """+viewvcServicePath+"""/  [R,L]
</IfModule>"""
        # Want to do: <LocationMatch ^%(urlPath)s(!?viewvc)> but mod_dav_svn gets the paths wrong.
        if self.dictionary[SVN_DAV_MOD_PYTHON_ACCESS_CONTROL]:
            accessControl = '%(modPythonAccessControl)s'
        else:
            accessControl = '%(accessControl)s'
        davsvnLocation = """
<Location %(urlPath)s>
<IfModule mod_dav.c>
DAV svn 
SVNPath %(fileSystemPath)s
"""+accessControl+"""
</IfModule>
</Location>"""
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[SVN_WSGI_SCRIPT_PATH]
            viewvcScriptAlias = """
WSGIScriptAlias """+viewvcServicePathParent+" "+wsgiScriptPath+"""
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup """ + self.dictionary[SVN_WSGI_PROCESS_GROUP]
            viewvcLocation = """
<Location """+viewvcServicePath+""">
SetEnv KFORGE_SVN_REPO_PATH %(fileSystemPath)s
SetEnv KFORGE_SVN_SERVICE_NAME """+service.name+"""
WSGIPassAuthorization On
</Location>"""
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            cgiScriptPath = self.dictionary[SVN_CGI_SCRIPT_PATH]
            viewvcScriptAlias = """
ScriptAlias """+viewvcServicePath+" "+cgiScriptPath
            viewvcLocation = """
<Location """+viewvcServicePath+""">
SetEnv KFORGE_SVN_REPO_PATH %(fileSystemPath)s
SetEnv KFORGE_SVN_SERVICE_NAME """+service.name+"""
%(accessControl)s
</Location>"""
        config = viewvcScriptAlias + viewvcRedirect + viewvcLocation + davsvnLocation
        return config

    helpMessage = '''
<p>This service provides a <a href="http://subversion.tigris.org/">Subversion</a> repository located at:</p>
<p style="text-align: center"><a href="%(url)s">%(url)s</a></p>
<p>A Subversion repository is a sharable versioned filesystem. To find out more about them see the <a href="http://svnbook.red-bean.com/">Subversion book</a>. You can access the material in the repository in one of the following ways (provided you have read permissions):</p>
<ul>
    <li>Browse the material online by following the link to the Subversion repository in your browser.</li>
    <li>'Check out' the repository with a suitable Subversion client. For example, if you are using the command line client, you would do:<br />
    <code>$ svn checkout %(url)s --username username</code><br /></li>
</ul>
<p>For more information on the command line client see the Subversion book (chapter 3). Alternatively there is <a href="http://tortoisesvn.tigris.org/">Tortoise SVN</a>, a GUI client that integrates with Windows explorer. It has a <a href="http://tortoisesvn.net/doc_release">detailed manual</a> with chapter 5 covering 'daily use' -- checking out, committing etc.</p>
<p>Note that if you wish to 'commit' work to the repository you must have a role on the project that includes 'write' permissions on Subversion services.</p>
'''

    def buildWsgiFile(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[SVN_WSGI_SCRIPT_PATH]
            wsgiScriptContent = self.createWsgiScriptContent()
            self.writeFile(wsgiScriptPath, wsgiScriptContent, 'Subversion WSGI script')

    def createWsgiScriptBody(self, pythonPathActivation):
        viewvcLibPath = self.dictionary[SVN_VIEWVC_LIB_PATH]
        viewvcTemplatePath = self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]
        wsgiScriptBody = """
# KForge auto-generated Svn (ViewVC) WSGI File.

import os
import sys

import sys, os

LIBRARY_DIR = r'""" + viewvcLibPath + """'
CONF_PATHNAME = None

sys.path.insert(0, LIBRARY_DIR)

import sapi
import viewvc


""" + pythonPathActivation + """

os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + """'

from kforge.handlers.modwsgi import WsgiAccessControlHandler

def dispatch_viewvc_request(environ, start_response):
    server = sapi.WsgiServer(environ, start_response)
    cfg = viewvc.load_config(CONF_PATHNAME, server)
    cfg.options.template_dir = r'"""+viewvcTemplatePath+"""'
    repositoryPath = environ.pop('KFORGE_SVN_REPO_PATH')
    serviceName = environ.pop('KFORGE_SVN_SERVICE_NAME')
    cfg.general.svn_roots = {serviceName: repositoryPath}
    cfg.options.svn_roots = {serviceName: repositoryPath}

    #cfg.conf_path = ' ' # Stops the viewvc's "hack_..." method failing. :-)
    cfg.options.hide_cvs_root = 1
    viewvc.main(server, cfg)
    return []

def application(environ, start_response):
    access_control = WsgiAccessControlHandler(dispatch_viewvc_request)
    return access_control(environ, start_response)
"""
        return wsgiScriptBody

    def buildCgiFile(self):
        cgiScriptPath = self.dictionary[SVN_CGI_SCRIPT_PATH]
        cgiScriptContent = self.createCgiScriptContent()
        self.writeFile(cgiScriptPath, cgiScriptContent, 'Subversion CGI script')
        # Make CGI script executable.
        os.chmod(cgiScriptPath, 0755)

    def createCgiScriptContent(self):
        # Todo: Fixup so it uses virtualenv or PYTHONPATH, if they exist.
        viewvcLibPath = self.dictionary[SVN_VIEWVC_LIB_PATH]
        viewvcTemplatePath = self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]
        cgiScriptContent = '''#!/usr/bin/env python

LIBRARY_DIR = r"'''+viewvcLibPath+'''"

#########################################################################
#
# Adjust sys.path to include our library directory
#

import sys
import os

if LIBRARY_DIR:
    sys.path.insert(0, LIBRARY_DIR)


repositoryPath = os.environ.pop('KFORGE_SVN_REPO_PATH')
serviceName = os.environ.pop('KFORGE_SVN_SERVICE_NAME')

import sapi
import viewvc

server = sapi.CgiServer()
cfg = viewvc.load_config(None, server)
cfg.options.template_dir = r"'''+viewvcTemplatePath+'''"
cfg.general.svn_roots = {serviceName: repositoryPath}
cfg.options.svn_roots = {serviceName: repositoryPath}
cfg.options.hide_cvs_root = 1
viewvc.main(server, cfg)

'''
        return cgiScriptContent

    def getUserHelp(self, service, serviceLocation):
        values = { 'url' : serviceLocation }
        msg = self.helpMessage % values
        return msg
    
    def getUserHelp(self, service, serviceLocation):
        values = {'httpUrl' : serviceLocation}
        if 'ssh' in self.registry.plugins:
            import getpass
            sshUrl = 'svn+ssh://%(sshUser)s@%(sshHost)s/%(project)s/%(service)s'
            sshUrl %= {
                'sshUser': self.dictionary[SSH_USER_NAME] or getpass.getuser(),
                'sshHost': self.dictionary[SSH_HOST_NAME],
                'project': service.project.name,
                'service': service.name
            }
            values['sshUrl'] = sshUrl
        helpMessage = '''
<p>This service provides a single Subversion repository. To find out more about <a href="http://subversion.tigris.org/">Subversion</a> see the <a href="http://svnbook.red-bean.com/">Subversion book</a>.</p>
<p>You can access the material in the repository the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the repository with your favorite Web browser.</li>
    <li>Access the repository with a suitable Subversion client via HTTP.</li>'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
    <li>Access the repository with a suitable Subversion client via SSH.</li>'''
        helpMessage += '''
</ul>

<p>For more information on the command line client see the Subversion book (chapter 3). Alternatively there is <a href="http://tortoisesvn.tigris.org/">Tortoise SVN</a>, a GUI client that integrates with Windows explorer. It has a <a href="http://tortoisesvn.net/doc_release">detailed manual</a> with chapter 5 covering 'daily use' -- checking out, committing etc.</p>

<h4>HTTP Access</h4>
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s

</pre></b></p>
<p>If you are using the command line client, you would do:
<pre>$ svn checkout %(httpUrl)s --username username

</pre></p>

'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
<h4>SSH Access</h4>
<p>The repository is available via SSH here:
<b><pre>%(sshUrl)s

</pre></b></p>
<p>Firstly, register your SSH public key with your account.</p>
<p>If you are using the command line client, you would do:
<pre>$ svn checkout %(sshUrl)s

</pre>
</p>

'''
        msg = helpMessage % values
        return msg


    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        backupItem = kforge.utils.backup.BackupItemSvn(
            backupPath, '', service.getDirPath()
        )
        backupItem.doBackup()


class SvnUtils(object):
    
    def __init__(self, parentPath=''):
        """
        @parentPath: string representing parent path to use when creating
                     repositories. If not defined then defaults to empty string
                     (so repositories must be specified with their path)
        """
        # NB: Only used in svntest.py.
        # Todo: Either move test path switching to dictionary manipulations, or create subclass in test unit and test that.
        self.parentPath = parentPath  
   
    def createRepository(self, path):
        """
        Creates repository with correct permissions.
        @path: a path to use for repository creation. If absolute it is used on 
               its own and if relative it is joined to parentPath defined at
               creation of class.
        """
        path = self.getRepositoryPath(path)
        type = 'fsfs'
        cmd = 'svnadmin create %s --fs-type %s' % (path, type)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Subversion command error: %s: %s' % (cmd, output))
        # Make the rep-cache.db file group writable since svnadmin doesn't ensure this.
        repCachePath = '%s/db/rep-cache.db' % (path)
        if os.path.exists(repCachePath):
            os.chmod(repCachePath, 436)

    def deleteRepository(self, path):
        """
        Destroys Subversion repository file system.
        @path: see definition of path for createRepository
        """
        fullPath = self.getRepositoryPath(path)
        if os.path.exists(fullPath):
            shutil.rmtree(fullPath)

    # NB: Only used when parentPath != '' in test.
    # Todo: Remove this function, it's distracting. :-)
    def getRepositoryPath(self, name):
        "Returns file system path from repository name."
        path = os.path.join(self.parentPath, name)
        return path
    

