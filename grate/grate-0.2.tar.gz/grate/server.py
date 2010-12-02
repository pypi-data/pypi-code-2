from twisted.conch import avatar
from twisted.conch.ssh import keys, userauth, connection, session, factory
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.cred import portal
from twisted.python import log
from twisted.python.failure import Failure
from twisted.internet import reactor
from zope.interface import implements
from grate.githandle import GitHandler


class GratePublicKeyChecker(SSHPublicKeyDatabase):

    def checkKey(self, creds):
        """
        Defined in SSHPublicKeyDatabase.

        :param creds: The credential object. This should be
            :class:`twisted.cred.credentials.ISSHPrivateKey`.
        :rtype: `string`
        :return: The authenticated user.
        """
        pubkey = keys.Key.fromString(data=creds.blob)
        log.msg('Checking key: %s' % pubkey.fingerprint())
        return self.matchKey(pubkey)

    def _cbRequestAvatarId(self, user, creds):
        """
        Defined in SSHPublicKeyDatabase. This method is called after checkKey.

        :param validKey: This is the result from the call to checkKey.
        :param creds: The credentials. Same one from checkKey.
        :rtype: `string` or :class:`twisted.python.failure.Failure`
        :return: The user or a `Failure` object.
        """
        # the second argument signifies a valid key
        ret = SSHPublicKeyDatabase._cbRequestAvatarId(self, user, creds)
        if isinstance(ret, Failure):
            return ret
        return user

    def matchKey(self, key):
        """
        :param key: The public key.
        :rtype: `string`
        :return: The user that is bound to the public key.
        """
        raise NotImplementedError


class GrateSession(object):
    implements(session.ISession)

    def __init__(self, avatar):
        self.avatar = avatar

    def getPty(self, term, windowSize, attrs):
        raise Exception('No PTY.')

    def execCommand(self, proto, cmd):
        log.msg('%s %s %r' % (proto, cmd, self.avatar.user))
        # Enforce access control, check that the command requested is kosher.
        safecmd = GitHandler.get_command(self.avatar.user, cmd)
        log.msg('Running: %s' % safecmd)
        reactor.spawnProcess(proto, 'git', ['git', 'shell', '-c', safecmd])

    def openShell(self, trans):
        raise Exception('No shell.')

    def eofReceived(self):
        log.msg('eofReceived')

    def dataReceived(self, data):
        log.err('dataReceived %s' % data)

    def closed(self):
        log.msg('closed')


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
