from twisted.cred import portal
from twisted.python import components, log
from twisted.conch.ssh import session, factory, userauth, connection, keys
from twisted.internet import reactor
from server import (GrateSession, GrateAvatar, GrateRealm,
                    GratePublicKeyChecker)
import gflags

gflags.DEFINE_string('key', '/etc/grate/ssh_host_rsa_key',
                     'The private rsa key')
gflags.DEFINE_string('checker', 'mongo', 'The public key checker')
gflags.DEFINE_string('logfile', None, 'The path to the log file. If not '
    'supplied, logs to stderr.')
gflags.DEFINE_integer('port', 22, 'The port number.')
FLAGS = gflags.FLAGS


class GrateFactory(factory.SSHFactory):
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection,
    }

    def _get_key(self):
        return keys.Key.fromFile(FLAGS.key)

    def getPrivateKeys(self):
        return {
            'ssh-rsa': self._get_key(),
        }

    def getPublicKeys(self):
        return {
            'ssh-rsa': self._get_key().public(),
        }


def main():
    if not FLAGS.logfile:
        import sys
        log.startLogging(sys.stderr)
    else:
        log.startLogging(open(FLAGS.logfile, 'a'))
    # Creates session objects from the avatar.
    components.registerAdapter(GrateSession, GrateAvatar, session.ISession)
    # Create the portal and add the publickey checker.
    grate_portal = portal.Portal(GrateRealm())
    if FLAGS.checker == 'mongo':
        from grate import mongo
        mongo.initialize()
        grate_portal.registerChecker(mongo.PublicKeyChecker())
    else:
        log.err('Unrecognized checker "%s", exiting.' % FLAGS.checker)
        raise Exception
    GrateFactory.portal = grate_portal
    # Start running.
    reactor.listenTCP(FLAGS.port, GrateFactory())
    reactor.run()
