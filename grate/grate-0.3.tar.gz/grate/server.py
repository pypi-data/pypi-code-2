from twisted.conch import avatar
from twisted.conch.ssh import userauth, connection, session, factory
from twisted.cred import portal
from twisted.python import log
from twisted.internet import reactor
from zope.interface import implements
from grate.githandle import GitHandler


class GrateSession(object):
    implements(session.ISession)

    def __init__(self, avatar):
        self.avatar = avatar
        self.user = avatar.user
        self.proc = None

    def getPty(self, term, windowSize, attrs):
        raise Exception('No PTY.')

    def execCommand(self, proto, cmd):
        log.msg('%s : execCommand : %s' % (self.user, cmd))
        # Enforce access control, check that the command requested is kosher.
        safecmd = GitHandler.get_command(self.user, cmd)
        log.msg('%s : execCommand : Running >%s<' % (self.user, safecmd))
        # XXX config for path to git.
        self.proc = reactor.spawnProcess(proto, 'git',
            ['git', 'shell', '-c', str(safecmd)])

    def openShell(self, trans):
        raise Exception('No shell.')

    def eofReceived(self):
        log.msg('%s : eofReceived' % self.user)
        # self.killProcess()

    def dataReceived(self, data):
        log.err('%s : dataReceived : %s' % (self.user, data))
        self.killProcess()

    def closed(self):
        log.msg('%s : closed' % self.user)
        self.killProcess()

    def killProcess(self):
        if self.proc:
            self.proc.loseConnection()


class GrateAvatar(avatar.ConchUser):

    def __init__(self, user):
        self.user = user
        log.msg('GrateAvatar(%r)' % user)
        avatar.ConchUser.__init__(self)
        self.channelLookup['session'] = session.SSHSession


class GrateRealm(object):
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        log.msg('requestAvatar %s %s' % (avatarId, mind))
        return interfaces[0], GrateAvatar(avatarId), lambda: None
