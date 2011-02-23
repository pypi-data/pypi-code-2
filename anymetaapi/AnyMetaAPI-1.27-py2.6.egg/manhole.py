# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

"""
Common manhole service for anymeta applications.

This provides a factory to set up a manhole. A typical use is:

    manholeFactory = manhole.getFactory(namespace, admin='admin')
    manholeService = strports.service('tcp:2222:interface=127.0.0.1',
                                      manholeFactory)

It is highly recommended to only allow access from the loopback interface.
"""

from twisted.cred import portal, checkers
from twisted.conch.insults import insults
from twisted.conch import manhole, manhole_ssh

def getFactory(namespace, **passwords):
    """
    Return a protocol factory to set up an ssh manhole.

    @param namespace: The initial global variables accessible in the
        interactive shell.
    @param passwords: This allows for providing username and password
        combinations as keyword arguments.
    """
    class chainedProtocolFactory:
        def __init__(self, namespace):
            self.namespace = namespace

        def __call__(self):
            return insults.ServerProtocol(manhole.ColoredManhole,
                                          self.namespace)

    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords)
    sshRealm = manhole_ssh.TerminalRealm()
    sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)

    sshPortal = portal.Portal(sshRealm, [checker])
    return manhole_ssh.ConchFactory(sshPortal)
