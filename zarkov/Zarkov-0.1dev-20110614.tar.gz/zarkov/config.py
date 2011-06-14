import sys
import logging.config
from optparse import OptionParser
from ConfigParser import ConfigParser

import ming

log = logging.getLogger(__name__)

def configure(args=None):
    if args is None: args = sys.argv
    options, args = get_options(args)
    if options.verbose:
        log.info('Settings:')
        for k,v in sorted(options.__dict__.items()):
            log.info('  %s: %r', k, v)
    ming.configure(**{
            'ming.main.master':options.mongo_uri,
            'ming.main.database':options.mongo_database})
    return options, args

def get_options(argv):
    defaults=dict(
        bind_address='0.0.0.0',
        port=6543,
        backdoor=6544,
        password=None,
        mongo_uri='mongodb://127.0.0.1:27017',
        mongo_database='zarkov',
        journal='journal',
        verbose=False)
    optparser = get_parser(defaults)
    options, args = optparser.parse_args(argv)
    if options.config_file:
        config = ConfigParser()
        config.read(options.config_file)
        log.info('About to configure logging')
        logging.config.fileConfig(options.config_file, disable_existing_loggers=False)
        log.info('Configured logging')
        defaults.update(
            (k, eval(v)) for k,v in config.items('zarkov'))
        optparser = get_parser(defaults)
        options, args = optparser.parse_args(argv)
    return options, args

def get_parser(defaults):
    optparser = OptionParser(
        usage=('%prog [--options]')) 
    optparser.set_defaults(**defaults)

    optparser.add_option(
        '-c', '--config-file', dest='config_file',
        help='Load options from config file')
    optparser.add_option(
        '-l', '--listen', dest='bind_address',
        help='IP address on which to listen for connections')
    optparser.add_option(
        '-p', '--port', dest='port',
        type='int',
        help='Port to listen for connections')
    optparser.add_option(
        '--password', dest='password',
        help='Password to require for connection')
    optparser.add_option(
        '--mongo-uri', dest='mongo_uri',
        help='URI for MongoDB server in which to store data')
    optparser.add_option(
        '--mongo-database', dest='mongo_database',
        help='MongoDB database in which to store data')
    optparser.add_option(
        '--journal', dest='journal',
        help='Filename to use for journalling')
    optparser.add_option(
        '-v', '--verbose', dest='verbose',
        action='store_true')
    optparser.add_option(
        '-b', '--backdoor', dest='backdoor',
        type='int')
    return optparser

