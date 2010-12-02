import sys
import logging
import gflags
from grate import main
from grate.mongo import GrateConfig


gflags.DEFINE_string('root', None, 'The path where the git repositories '
    'should be stored.')
gflags.DEFINE_bool('overwrite', False, 'Set this flag to overwrite.')
FLAGS = gflags.FLAGS


def find_config():
    return GrateConfig.objects.first()


def _save(cfg):
    try:
        cfg.save(safe=True)
    except Exception, e:
        logging.error(e)
        raise


def create_config(root):
    cfg = GrateConfig(root=root)
    _save(cfg)


def overwrite_config(cfg, root):
    cfg.root = root
    _save(cfg)


def main():
    logging.basicConfig(level=logging.DEBUG)
    if not FLAGS.root:
        sys.stderr.write(FLAGS.GetHelp())
        sys.stderr.write('\n\n')
        sys.stderr.write('ERROR: Need --root\n\n')
        return
    if FLAGS.checker == 'mongo':
        from grate import mongo
        mongo.initialize()
    else:
        logging.error('Unrecognized checker "%s", exiting.', FLAGS.checker)
        raise Exception
    cfg = find_config()
    if not cfg:
        logging.info('Initializing at root: %s', FLAGS.root)
        create_config(FLAGS.root)
        logging.info('Done.')
    elif FLAGS.overwrite:
        logging.info('Overwriting config with root: %s', FLAGS.root)
        overwrite_config(cfg, FLAGS.root)
        logging.info('Done.')
    else:
        logging.warn('Already initialized root: %s', cfg.root)
