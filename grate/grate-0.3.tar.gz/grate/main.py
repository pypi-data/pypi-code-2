import sys
from twisted.cred import portal
from twisted.python import components, log
from twisted.conch.ssh import session, factory, userauth, connection, keys
from twisted.conch.checkers import SSHProtocolChecker
from twisted.internet import reactor
from grate import mongo
from server import GrateSession, GrateAvatar, GrateRealm
from . import checkers
import gflags

gflags.DEFINE_string('key', None, 'The private rsa key')
gflags.DEFINE_multistring('checkers', 'pubkey', 'The listing of '
    'authentication mechanisms')
gflags.DEFINE_string('logfile', None, 'The path to the log file. If not '
    'supplied, logs to stderr.')
gflags.DEFINE_integer('port', None, 'The port number.')
FLAGS = gflags.FLAGS


class GrateFactory(factory.SSHFactory):
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection,
    }

    def __init__(self, keyfile, *args, **kwargs):
        self.keyfile = keyfile

    def _get_key(self):
        return keys.Key.fromFile(self.keyfile)

    def getPrivateKeys(self):
        return {
            'ssh-rsa': self._get_key(),
        }

    def getPublicKeys(self):
        return {
            'ssh-rsa': self._get_key().public(),
        }


def start_running(checkers, port, key):
    # Creates session objects from the avatar.
    components.registerAdapter(GrateSession, GrateAvatar, session.ISession)
    # Create the portal and add the checkers (pubkey, ldap, etc.).
    grate_portal = portal.Portal(GrateRealm())
    pchecker = SSHProtocolChecker()
    for c in checkers:
        pchecker.registerChecker(c)
    grate_portal.registerChecker(pchecker)
    GrateFactory.portal = grate_portal
    # Start running.
    reactor.listenTCP(port, GrateFactory(key))
    reactor.run()


def main():
    if not FLAGS.logfile:
        log.startLogging(sys.stderr)
    else:
        log.startLogging(open(FLAGS.logfile, 'a'))
    mongo.initialize()
    cfg = mongo.GrateConfig.get_config()
    # Create credential checkers
    log.msg('Auth %r' % FLAGS.checkers)
    auth_checkers = [checkers.get(name) for name in FLAGS.checkers]
    if not checkers:
        log.err('No checkers defined, exiting.')
        return -1
    #
    if FLAGS.port:
        port = FLAGS.port
        # XXX TODO FIXME Do I update the port in the configuration?
    elif cfg.port:
        port = cfg.port
    else:
        log.err('Please specify the port using --port <number>')
        return -2
    if FLAGS.key:
        key = FLAGS.key
    elif cfg.key:
        key = cfg.key
    else:
        log.err('Please specify the private key using --key <path>')
        return -3
    start_running(auth_checkers, port, key)
