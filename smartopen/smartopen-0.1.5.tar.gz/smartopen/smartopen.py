#!/usr/bin/env python

""" smart open the data passed in """

import os
import sys

from optparse import OptionParser
from pkg_resources import iter_entry_points
from ConfigParser import ConfigParser

def locations(names=None, config=None):
    """
    list of 2-tuples of location handlers;
    * names: order names of handlers
    * config: nested dictionary of configuration from names
    """

    _handlers = {}
    _names = []
    if config is None:
        config = {}
    
    for i in iter_entry_points('smartopen.locations'):
        try:
            handler = i.load()
        except:
            continue # TODO: warn/debug with --verbose flag
        _handlers[i.name] = handler
        if not names:
            _names.append(i.name)

    if not names:
        names = _names
    handlers = []
    for name in names:
        if ':' in name:
            _name, section = name.split(':', 1)
        else:
            _name = name
        if _name in _handlers:
            try:
                handler = _handlers[_name](**config.get(name, {}))
            except:
                continue
            handlers.append((name, handler))
    return handlers

def urls(query, handlers=None):
    if handlers is None:
        handlers = locations()
    urls = []
    for name, handler in handlers:
        if handler.test(query):
            urls.append((name, handler.url(query)))
    return urls

def url(query, handlers=None):
    if handlers is None:
        handlers = locations()
    for name, handler in handlers:
        if handler.test(query):
            return handler.url(query)

def main(args=sys.argv[1:]):

    # parse command line optioins
    parser = OptionParser()
    parser.add_option('-c', '--config', dest="config",
                      help="config file to read")
    parser.add_option('-u', '--url', dest="url", 
                      action='store_true', default=False,
                      help="print the first url handled")
    parser.add_option('-a', '--all', dest="all", 
                      action='store_true', default=False,
                      help="print all handlers that match the query")
    parser.add_option('-H', '--handler', dest="handlers",
                      action='append',
                      help="name of the handler to use, in order")
    parser.add_option('--print-handlers', dest="print_handlers",
                      action='store_true',
                      help="print all handlers in order they would be tried")
    options, args = parser.parse_args(args)

    # sanity check
    assert not (options.url and options.all)
    if not options.handlers:
        options.handlers = None

    # config
    config = ConfigParser()
    if not options.config:
        options.config = os.path.join(os.environ.get('HOME', ''), '.smartopen.ini')
    if os.path.exists(options.config):
        config.read(options.config)
        if not options.handlers and config.has_option('DEFAULTS', 'handlers'):
            options.handlers = [ i.strip() for i in config.get('DEFAULTS', 'handlers').split(',') ]
    _config = {}
    for section in config.sections():
        _config[section] = dict(config.items(section))

    # get the handlers
    _locations = locations(options.handlers, _config)

    # print the handlers
    if options.print_handlers:
        for name, loc in _locations:
            print name
        sys.exit(0)

    # get data to be operated on
    if args:
        data = ' '.join(args)
    else:
        data = sys.stdin.read()

    # print the URLs
    if options.all:
        _urls = urls(data, _locations)
        for name, _url in _urls:
            print '%s: %s' % (name, _url)
        sys.exit(0)

    _url = url(data, _locations)

    # print a URL
    if options.url:
        print _url
        sys.exit(0)

    # open the URL in a browser
    os.system("firefox '%s'" % _url)
    sys.exit(0)


if __name__ == '__main__':
    main()
