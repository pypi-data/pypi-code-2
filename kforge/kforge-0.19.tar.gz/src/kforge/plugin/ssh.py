"""KForge SSH Plugin

Enabling the 'ssh' plugin means that project developers will be able to access
Subversion, Git and Mercurial version control system services via SSH.

When the 'ssh' plugin is enabled, registered users will be able to upload SSH
public keys, see a list of SSH keys they have uploaded, and delete keys
invidually. An 'authorized_keys' file will be rewritten as public keys are
registered and deleted (if necessary, use a cron job to copy this file to SSH
user's authorized_keys file). The resulting 'authorized_keys' file entries will
all have the KForge SSH handler as the SSH "command". The KForge SSH handler
resolves, authorizes and executes SSH requests, and will not operate unless the
'ssh' plugin is enabled.

Instructions for accessing repositories with SSH is presented on Git and
Mercurial service pages.

Platform dependencies:

  * SSH server. The SSH server is used to authenticate users by public-private
    key, and then to pass on the authenticated SSH request to the KForge SSH
    handler. For example, on Debian the openssh-server package must be installed
    and enabled.

KForge configuration file:

  * You may wish to set the path to the SSH authorized_keys file, the username
    of the SSH account, and the hostname of the SSH server.

[ssh]
authorized_keys_file = ~/.ssh/authorized_keys
user_name = %(user_name)s
host_name = %(domain_name)s

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable ssh
  $ kforge-admin plugin show ssh
  $ kforge-admin plugin disable ssh

"""
import os
import commands
import shutil

import kforge.plugin.base
from kforge.dictionary import *

class Plugin(kforge.plugin.base.NonServicePlugin):
    "SSH plugin."
    
    def getAuthorizedKeysPath(self):
        path = self.dictionary[SSH_AUTHORIZED_KEYS_PATH]
        return os.path.expanduser(path)
    getAuthorizedKeysPath = classmethod(getAuthorizedKeysPath)

    def isFileWritable(self, path):
        return os.path.isfile(path) and os.access(path, os.W_OK)
    isFileWritable = classmethod(isFileWritable)

    def checkDependencies(self):
        errors = []
        authorizedKeysPath = self.getAuthorizedKeysPath()

        if not os.path.exists(authorizedKeysPath):
            errors.append("Authorized keys file not found on path: %s" % authorizedKeysPath)
        return errors

    def showDepends(self):
        authorizedKeysPath = self.getAuthorizedKeysPath()
        isWritable = self.isFileWritable(authorizedKeysPath)
        return [
            "Authorized keys file: %s" % (isWritable and "OK" or ("Error: Unwritable file: %s" % authorizedKeysPath)),
        ]
    showDepends = classmethod(showDepends)
 
    def onSshKeyCreate(self, sshKey):
        self.writeAuthorizedKeysFile()

    def onSshKeyDelete(self, sshKey):
        self.writeAuthorizedKeysFile(excludeSshKey=sshKey)

    def writeAuthorizedKeysFile(self, excludeSshKey=None):
        # Todo: Improve this simple implementation: probably want to delegate 
        # to a script which can be run by configured command, possibly with 
        # sudo if SSH user != Apache user, but which can alternatively be run
        # as a cron job?

        handlerPath = os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'kforge-ssh-handler')
        configPath = os.path.join(self.dictionary[SYSTEM_CONFIG_PATH])
        sshOptions = ',no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty'
        sshCommands = ''
        for sshKey in self.registry.sshKeys:
            if sshKey == excludeSshKey:
                continue
            keyId = sshKey.id
            keyString = sshKey.keyString
            sshCommand = 'command="%s %s %s"%s %s\n'
            sshCommand %= (handlerPath, configPath, keyId, sshOptions, keyString)
            sshCommands += sshCommand
        authorizedKeysPath = self.getAuthorizedKeysPath()
        self.logger.info("Writing SSH keys to file: %s" % authorizedKeysPath)
        try:
            f = open(authorizedKeysPath, 'w')
            f.write(sshCommands)
            f.close()
        except Exception, inst:
            msg = "Couldn't write SSH keys to file: %s" % inst
            self.logger.error(msg)

