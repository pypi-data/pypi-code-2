import sys
from optparse import OptionParser
from ConfigParser import ConfigParser

import ming

def configure(args=None):
    if args is None: args = sys.argv
    options, args = get_options(args)
    if options.verbose:
        for k,v in sorted(options.__dict__.items()):
            print '%s: %s' % (k,v)
    ming.configure(**{
            'ming.main.master':options.mongo_uri,
            'ming.main.database':options.mongo_database})
    return options, args

def get_options(args):
    defaults=dict(
        bind_address='0.0.0.0',
        port=6543,
        backdoor=None,
        password=None,
        mongo_uri='mongodb://127.0.0.1:27017',
        mongo_database='zarkov',
        verbose=False)
    optparser = get_parser(defaults)
    options, args = optparser.parse_args(args)
    if options.config_file:
        config = ConfigParser()
        config.read(options.config_file)
        defaults.update(
            (k, eval(v)) for k,v in config.items('zarkov'))
        optparser = get_parser(defaults)
        options, args = optparser.parse_args(args)
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
        help='URI for MongoDB database in which to store data')
    optparser.add_option(
        '-v', '--verbose', dest='verbose',
        action='store_true')
    optparser.add_option(
        '-b', '--backdoor', dest='backdoor',
        type='int')
    return optparser

