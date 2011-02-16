import os
import sys
import socket
import logging
import gflags
import grate.main
from grate import mongo
from grate.mongo import GrateConfig


# Delete the port flag from main.
del gflags.FLAGS.port
del gflags.FLAGS.key
del gflags.FLAGS.logfile
gflags.DEFINE_string('root', None, 'The path where the git repositories '
    'should be stored.')
gflags.DEFINE_string('host', None, 'The hostname for git urls.')
gflags.DEFINE_boolean('auto-host', False, 'Automatically set the hostname.')
gflags.DEFINE_integer('port', None, 'The port for ssh.')
gflags.DEFINE_string('key', None, 'The private rsa key.')
gflags.DEFINE_string('logfile', None, 'The path to the log file. If not '
    'supplied, logs to stderr.')
gflags.DEFINE_boolean('print', False, 'Prints the current config.')
FLAGS = gflags.FLAGS


def print_config(cfg):
    import textwrap
    sys.stdout.write(textwrap.dedent('''\
        host = %(host)r
        port = %(port)r
        key = %(key)r
        root = %(root)r\n''' % (cfg._data)))


def set_config(cfg):
    normalize = lambda p: os.path.normpath(os.path.abspath(p))
    auto_host = getattr(FLAGS, 'auto-host')
    if FLAGS.root:
        root = normalize(FLAGS.root)
        logging.info('Setting repository root: %s', root)
        cfg.root = root
    if FLAGS.port:
        logging.info('Setting ssh port: %d', FLAGS.port)
        cfg.port = FLAGS.port
    if auto_host:
        logging.info('Automatically determining hostname.')
        hostname = socket.getfqdn()
        logging.info('Setting ssh hostname: %s', hostname)
        cfg.host = hostname
    if FLAGS.host:
        logging.info('Setting ssh hostname: %s', FLAGS.host)
        cfg.host = FLAGS.host
    if FLAGS.key:
        key = normalize(FLAGS.key)
        logging.info('Setting key file: %s', key)
        cfg.key = key


def main():
    logging.basicConfig(level=logging.DEBUG)
    if getattr(FLAGS, 'print'):
        mongo.initialize()
        print_config(GrateConfig.get_config())
        return 0
    root = FLAGS.root
    port = FLAGS.port
    host = FLAGS.host
    key = FLAGS.key
    auto_host = getattr(FLAGS, 'auto-host')
    if not (root or port or host or auto_host or key):
        sys.stderr.write(FLAGS.GetHelp())
        sys.stderr.write('\n\n')
        sys.stderr.write('''ERROR: Need one of:
        --root <path>
        --host <hostname>
        --[no]auto-host
        --port <number>
        --key <path>\n''')
        return -1
    mongo.initialize()
    try:
        cfg = GrateConfig.get_config()
        set_config(cfg)
        cfg.save(safe=True)
        logging.info('Done.')
    except Exception as e:
        logging.error(e)
        return -1
    return 0
