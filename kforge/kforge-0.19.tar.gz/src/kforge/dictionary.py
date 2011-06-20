"""
Dictionary of system attributes.

"""

import os
import sys
import dm.dictionary
import kforge
import kforge.dictionarywords
from kforge.dictionarywords import *

class SystemDictionary(dm.dictionary.SystemDictionary):

    words = kforge.dictionarywords

    def getSystemName(self):
        return 'kforge'

    def getSystemTitle(self):
        return 'KForge'

    def getSystemServiceName(self):
        return 'KForge'

    def getSystemVersion(self):
        return kforge.__version__
 
    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[MEMBER_ROLE_NAME] = 'Friend'
        self[PLUGIN_PACKAGE_NAME] = 'kforge.plugin'
        self[SVN_ADMIN_SCRIPT] = 'svnadmin'
        self[SVN_CGI_SCRIPT_PATH] = ''
        self[SVN_WSGI_SCRIPT_PATH] = ''
        self[SVN_WSGI_PROCESS_GROUP] = ''
        self[SVN_VIEWVC_LIB_PATH] = '/usr/lib/viewvc/lib'
        self[SVN_VIEWVC_TEMPLATE_PATH] = '/etc/viewvc/templates'
        self[SVN_VIEWVC_MEDIA_PATH] = '/usr/share/viewvc/docroot'
        self[SSH_AUTHORIZED_KEYS_PATH] = '~/.ssh/authorized_keys'
        self[SVN_DAV_MOD_PYTHON_ACCESS_CONTROL] = ''
        self[SSH_USER_NAME] = ''
        self[SSH_HOST_NAME] = ''
        self[TRAC_ADMIN_SCRIPT] = 'trac-admin'
        self[TRAC_TEMPLATES_PATH] = ''
        self[TRAC_HTDOCS_PATH] = ''
        self[TRAC_WSGI_SCRIPT_PATH] = ''
        self[TRAC_WSGI_PROCESS_GROUP] = ''
        self[PROJECTS_PATH] = ''
        self[DAV_WSGI_SCRIPT_PATH] = ''
        self[DAV_WSGI_PROCESS_GROUP] = ''
        self[MERCURIAL_ADMIN_SCRIPT] = 'hg'
        self[MERCURIAL_WSGI_SCRIPT_PATH] = ''
        self[MERCURIAL_WSGI_PROCESS_GROUP] = ''
        self[MERCURIAL_CGI_SCRIPT_PATH] = ''
        self[GIT_ADMIN_SCRIPT] = 'git'
        self[GIT_HTTP_BACKEND_SCRIPT] = '/usr/lib/git-core/git-http-backend'
        self[GIT_GITWEB_SCRIPT] = '/usr/lib/cgi-bin/gitweb.cgi'
        self[GIT_GITWEB_STATIC] = '/usr/share/gitweb/static'
        self[GIT_WSGI_SCRIPT_PATH] = ''
        self[GIT_WSGI_PROCESS_GROUP] = ''
        self[DAV_LOCK_PATH] = ''
        self[FEED_SUMMARY_LENGTH] = '25'
        self[FEED_LENGTH] = '100'
        self[MAILMAN_LIST_ADMIN_PASSWORD] = ''
        self[MAILMAN_NEWLIST] = 'sudo newlist'
        self[MAILMAN_RMLIST] = 'sudo rmlist'
        self[MAILMAN_DOMAIN] = ''
        self[MOIN_SYSTEM_PATH] = '/usr/share/moin'
        self[MOIN_VERSION] = '193'
        self[MOIN_WSGI_PROCESS_GROUP] = ''
        self[WORDPRESS_MASTER_PATH] = '/usr/share/wordpress'
        self[WORDPRESS_BACKUP_COMMAND] = ''

    def setWordsFromWords(self):
        super(SystemDictionary, self).setWordsFromWords()
        if self[SSH_USER_NAME] == '':
            self[SSH_USER_NAME] = self[SYSTEM_USER_NAME]
        if self[SSH_HOST_NAME] == '':
            self[SSH_HOST_NAME] = self[DOMAIN_NAME]
        if not self[PROJECTS_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'var', 'project')
            self[PROJECTS_PATH] = path
        if not self[SVN_CGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'cgi', 'svn.cgi')
            self[SVN_CGI_SCRIPT_PATH] = path
        if not self[SVN_WSGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'wsgi', 'svn.wsgi')
            self[SVN_WSGI_SCRIPT_PATH] = path
        if not self[GIT_WSGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'wsgi', 'git.wsgi')
            self[GIT_WSGI_SCRIPT_PATH] = path
        if not self[DAV_WSGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'wsgi', 'dav.wsgi')
            self[DAV_WSGI_SCRIPT_PATH] = path
        if not self[TRAC_WSGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'wsgi', 'trac.wsgi')
            self[TRAC_WSGI_SCRIPT_PATH] = path
        if not self[MERCURIAL_WSGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'wsgi', 'mercurial.wsgi')
            self[MERCURIAL_WSGI_SCRIPT_PATH] = path
        if not self[MERCURIAL_CGI_SCRIPT_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'cgi', 'mercurial.cgi')
            self[MERCURIAL_CGI_SCRIPT_PATH] = path
        if not self[DAV_WSGI_PROCESS_GROUP]:
            self[DAV_WSGI_PROCESS_GROUP] = self[WSGI_PROCESS_GROUP]
        if not self[GIT_WSGI_PROCESS_GROUP]:
            self[GIT_WSGI_PROCESS_GROUP] = self[WSGI_PROCESS_GROUP]
        if not self[MERCURIAL_WSGI_PROCESS_GROUP]:
            self[MERCURIAL_WSGI_PROCESS_GROUP] = self[WSGI_PROCESS_GROUP]
        if not self[SVN_WSGI_PROCESS_GROUP]:
            self[SVN_WSGI_PROCESS_GROUP] = self[WSGI_PROCESS_GROUP]
        if not self[TRAC_WSGI_PROCESS_GROUP]:
            self[TRAC_WSGI_PROCESS_GROUP] = self[WSGI_PROCESS_GROUP]
        if not self[MOIN_WSGI_PROCESS_GROUP]:
            self[MOIN_WSGI_PROCESS_GROUP] = self[WSGI_PROCESS_GROUP]

    def setNewWordsFromOld(self):
        super(SystemDictionary, self).setNewWordsFromOld()
        self.setNewWordFromOld(MAILMAN_DOMAIN, OLD_MAILMAN_DOMAIN)
        self.setNewWordFromOld(DAV_LOCK_PATH, OLD_DAV_LOCK_PATH)

