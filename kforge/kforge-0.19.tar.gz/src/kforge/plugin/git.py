"""KForge Git plugin.

Enabling this plugin allows KForge project administrators to create Git
services.

Creating services with this plugin requires:

  * Git. The 'git' command is used to create repositories (supplied by the 'git-core' package on Debian).

Providing access to this plugin's services requires:

  * Apache. The mod_python, and mod_dav Apache modules are used to provide access to Git through Apache. For example, on Debian the libapache2-mod-python and libapache2-svn packages must be installed and enabled.

Using Git repositories with Trac projects (optional) requires:

  * Trac's Git plugin. For example, on Debian the trac-git package can be installed.

You do not need to add anything to the KForge config file.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable git
  $ kforge-admin plugin show git
  $ kforge-admin plugin disable git
"""
# Todo: Fix the helpMessage so it's https when necessary.
from kforge.dictionarywords import *
from kforge.dictionary import *  # Is this necessary?
import kforge.plugin.base
import os
import commands

class Plugin(kforge.plugin.base.ServicePlugin):
    
    def checkDependencies(self):
        errors = []
        path = self.dictionary[GIT_ADMIN_SCRIPT]
        cmd = 'which %s' % path
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't find Git admin script '%s' on path." % path)
        if not os.path.isfile(self.dictionary[GIT_GITWEB_SCRIPT]):
            errors.append("Couldn't find Git web script: %s" % self.dictionary[GIT_GITWEB_SCRIPT])
        if not os.path.isfile(self.dictionary[GIT_HTTP_BACKEND_SCRIPT]):
            errors.append("Couldn't find Git HTTP backend script: %s" % self.dictionary[GIT_HTTP_BACKEND_SCRIPT])
        return errors

    def showDepends(self):
        path = self.dictionary[GIT_ADMIN_SCRIPT]
        cmd = 'which %s' % path
        (status, output) = commands.getstatusoutput(cmd)
        return [
            "Admin script: %s" % (status and "Not found!" or ("Found OK. %s" % output)),
            "HTTP backend: %s" % (os.path.isfile(self.dictionary[GIT_HTTP_BACKEND_SCRIPT]) and "Found OK. %s" % self.dictionary[GIT_HTTP_BACKEND_SCRIPT] or "Not Found"),
            "Gitweb: %s" % (os.path.isfile(self.dictionary[GIT_GITWEB_SCRIPT]) and "Found OK. %s" % self.dictionary[GIT_GITWEB_SCRIPT] or "Not Found"),
            "Apache cgi module: %s" % "Please check this module is enabled.",
            "Apache alias module: %s" % "Please check this module is enabled.",
            "Apache env module: %s" % "Please check this module is enabled.",
            "Trac Git: %s" % "Please check this package is installed (optional).",
        ]
    showDepends = classmethod(showDepends)

    def onServiceCreate(self, service):
        if self.isOurs(service):
            servicePath = self.paths.getServicePath(service)
            msg = 'GitPlugin: Creating new Git repository for %s: %s' % (
                service, servicePath
            )
            self.logger.info(msg)
            self.paths.assertServiceFolder(service)
            self.createRepository(servicePath, self.dictionary[GIT_ADMIN_SCRIPT])
            self.createGitwebConfig(servicePath, service.project.name, service.name)

    def createRepository(self, path, gitCmd='git'):
        if not os.path.exists(path):
            os.makedirs(path)
        # Create bare repository.
        cmd = 'cd %s; %s --bare init; git update-server-info; if [ -e hooks/post-commit ]; then chmod +x hooks/post-commit; fi' % (path, gitCmd)
        msg = 'GitPlugin: Initializing bare repository: %s' % cmd
        self.logger.info(msg)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('git create error on %s: %s' % (cmd, output))
        # Adjust the description file.
        cmd = 'echo "Git repository" > %s/description' % path
        msg = 'GitPlugin: Changing project description: %s' % cmd
        self.logger.info(msg)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('error changing git description file %s: %s' % (cmd, output))

    def createGitwebConfig(self, servicePath, projectName, serviceName):
        msg = 'GitPlugin: Configuring new repository for Gitweb.'
        self.logger.info(msg)
        cmd = 'mkdir %(servicePath)s/gitwebprojectroot' % {'servicePath': servicePath}
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Unable to create Gitweb project root: %s: %s' % (cmd, output))
        cmd = 'ln -s %(servicePath)s %(servicePath)s/gitwebprojectroot/%(serviceName)s' % {'servicePath': servicePath, 'serviceName': serviceName}
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Unable to symlink repository for gitweb: %s: %s' % (cmd, output))
        listFileContent = '%s Administrator\n' % serviceName
        listFilePath = os.path.join(servicePath, 'gitweb.list')
        listFile = open(listFilePath, 'w')
        listFile.write(listFileContent)
        listFile.close()
        configFileContent = '''# Gitweb configuration (generated by KForge).
$projectroot = "%(servicePath)s/gitwebprojectroot";
$projects_list = "%(servicePath)s/gitweb.list";
$git_temp = "/tmp";
#$home_link = $my_uri || "/";
$home_link_str = "%(projectName)s";
#$home_text = "indextext.html";
@stylesheets = ("/gitweb_static/gitweb.css");
$javascript = "/gitweb_static/gitweb.js";
$logo = "/gitweb_static/git-logo.png";
$favicon = "/gitweb_static/git-favicon.png";
#@diff_opts = ("-M");
@diff_opts = ();
''' % {'servicePath': servicePath, 'projectName': projectName}
        configFilePath = os.path.join(servicePath, 'gitweb.conf')
        configFile = open(configFilePath, 'w')
        configFile.write(configFileContent)
        configFile.close()

    def getApacheConfigCommon(self):
        kwds = {
            'staticPath': self.dictionary[GIT_GITWEB_STATIC],
        }
        return """
Alias /gitweb_static %(staticPath)s
""" % kwds

    def getApacheConfig(self, service):
        # Todo: Change all service URLs to have trailing slash (so config knows where they end
        # and they aren't at risk of shorter patterns matching longer names - current order is critical).
        # Todo: Support static file configuration, see "Accelerated static Apache 2.x" on this
        # page: http://www.kernel.org/pub/software/scm/git/docs/git-http-backend.html
        # - will need dictionary word, default value in dictionary, 
        servicePath = self.paths.getServicePath(service)
        backendPath = self.dictionary[GIT_HTTP_BACKEND_SCRIPT]
        gitwebPath = self.dictionary[GIT_GITWEB_SCRIPT]
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[GIT_WSGI_SCRIPT_PATH]
            config = """
WSGIScriptAlias %(urlPath)s """ + wsgiScriptPath + """
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup """ + self.dictionary[GIT_WSGI_PROCESS_GROUP] + """
<Location %(urlPath)s>
SetEnv GIT_PROJECT_ROOT """+servicePath+"""
SetEnv GIT_HTTP_EXPORT_ALL
SetEnv GITWEB_CONFIG """+servicePath+"""/gitweb.conf
WSGIPassAuthorization On
</Location>
"""
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            config = """
<Location %(urlPath)s>
SetEnv GIT_PROJECT_ROOT """+servicePath+"""
SetEnv GIT_HTTP_EXPORT_ALL
SetEnv GITWEB_CONFIG """+servicePath+"""/gitweb.conf
%(accessControl)s
</Location>
ScriptAliasMatch "(?x)^%(urlPath)s(.*/(HEAD|info/refs|objects/(info/[^/]+|[0-9a-f]{2}/[0-9a-f]{38}|pack/pack-[0-9a-f]{40}\.(pack|idx))|git-(upload|receive)-pack))$" """+backendPath+"""/$1
ScriptAlias %(urlPath)s """+gitwebPath+"""
"""
        return config

    def buildWsgiFile(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            wsgiScriptPath = self.dictionary[GIT_WSGI_SCRIPT_PATH]
            wsgiScriptContent = self.createWsgiScriptContent()
            self.writeFile(wsgiScriptPath, wsgiScriptContent, 'Git WSGI script')

    def createWsgiScriptBody(self, pythonPathActivation):
        gitwebScriptPath = self.dictionary[GIT_GITWEB_SCRIPT]
        httpBackendScriptPath = self.dictionary[GIT_HTTP_BACKEND_SCRIPT]
        wsgiScriptBody = """
# KForge auto-generated Git WSGI File.

import os
import sys

"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """

from subprocess import Popen, PIPE
import shlex
import re

gitwebScriptPath = '""" + gitwebScriptPath + """'
httpBackendScriptPath = '""" + httpBackendScriptPath + """'
backend = re.compile(".*/(HEAD|info/refs|objects/(info/[^/]+|[0-9a-f]{2}/[0-9a-f]{38}|pack/pack-[0-9a-f]{40}\.(pack|idx))|git-(upload|receive)-pack)$")

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"

        wsgiScriptBody += """
    from kforge.handlers.modwsgi import GitWsgiAccessControlHandler
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    if backend.search(environ['PATH_INFO']):
        AccessControlHandler = GitWsgiAccessControlHandler
        cgiScriptPath = httpBackendScriptPath
    else:
        AccessControlHandler = WsgiAccessControlHandler
        cgiScriptPath = gitwebScriptPath

    def dispatch_cgi_request(environ, start_response):
        # Prepare environment.
        env = os.environ.copy()
        stdindata = environ.pop('wsgi.input').read()
        for k,v in environ.items():
            if k.startswith('wsgi') or k.startswith('mod_wsgi'):
                continue
            try:
                env[k] = v
            except:
                raise Exception, "Couldn't set %s = %s in new env." % (k, v)
        # Run the CGI script.
        p = Popen(shlex.split(cgiScriptPath), stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
        stdoutdata, stderrdata = p.communicate(stdindata)
        if p.wait(): 
            os.stderr.write(stderrdata)
            os.stderr.flush()
        else:
            headers, body = stdoutdata.split('\\r\\n\\r\\n', 1)
            headers = headers.split('\\r\\n')
            headers = [tuple(h.split(': ', 1)) for h in headers]
            start_response('200 OK', headers)
            return [body]
    
    access_control = AccessControlHandler(dispatch_cgi_request)
    return access_control(environ, start_response)
"""    
        return wsgiScriptBody



#    def getApacheConfigCommon(self):
#        path = self.paths.getDavLockPath()
#        return """
#        # Follows
#        # <http://www.kernel.org/pub/software/scm/git/docs/howto/setup-git-server-over-http.txt>
#        DAVLockDB "%(davLockPath)s"
#""" % {'davLockPath': path}
#
#    def getApacheConfig(self, service):
#        fsPath = self.paths.getServicePath(service)
#        return """
#        # Follows
#        # <http://www.kernel.org/pub/software/scm/git/docs/howto/setup-git-server-over-http.txt>
#        <Location %(urlPath)s>
#            DAV On
##            Options +Indexes +FollowSymLinks
##            Allow from all
##            Order allow,deny
#            %(accessControl)s
#        </Location>
#        Alias %(urlPath)s """ + fsPath + """
#"""


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
<p>This service provides a single Git repository. To find out more about <a href="http://git-scm.com/">Git</a> see the <a href="http://git-scm.com/documentation">Git documentation</a>.</p>
<p>You can access the material in the repository the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the repository with your favorite Web browser.</li>
    <li>Access the repository with a suitable Git client via HTTP.</li>'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
    <li>Access the repository with a suitable Git client via SSH.</li>'''
        helpMessage += '''
</ul>

<p>See the <a href="http://www.kernel.org/pub/software/scm/git/docs/user-manual.html">Git Manual</a> for more information on the Git command line client. Graphical user interfaces for Git and Git plugins for rapid development environments such as Eclipse are also available.

<h4>HTTP Access</h4>    
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s

</pre></b></p>
<p>Configure HTTP authentication for Git by adding the following to the <code>~/.netrc</code> file. Create the <code>~/.netrc</code> file if necessary:
<pre>machine DOMAINNAME
login USERNAME
password PASSWORD

</pre></p>
<p>check the permissions are set correctly:
<pre>$ chmod 600 ~/.netrc

</pre></p>
<p>If you are using the command line client, you would do:
<pre>$ git clone %(httpUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:
<pre>$ git push origin master

</pre></p>
'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
<h4>SSH Access</h4>
<p>The repository is available via SSH here:
<b><pre>%(sshUrl)s

</pre></b></p>
<p>If necessary, register your SSH public key with your account.</p>
<p>If you are using the command line client, you would do:
<pre>$ git clone %(sshUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:
<pre>$ git push origin master

</pre></p>

'''
        msg = helpMessage % values
        return msg

