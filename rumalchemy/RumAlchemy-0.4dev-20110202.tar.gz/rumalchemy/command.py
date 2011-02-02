#TODO: Move this to a separate egg... pyMyAdmin perhaps?
import logging
import sys
from optparse import OptionParser

from pkg_resources import require, DistributionNotFound
from paste.deploy import loadserver

from rum import RumApp

def rumalchemy(argv=None):
    opts, args = parser.parse_args(argv)
    try:
        url = args[0]
    except IndexError:
        if not opts.config:
            print >> sys.stderr, "Need to provide a database url "\
                                 "(eg: postgres:///somedatabase) or a config "\
                                 "file."
            parser.print_help(sys.stderr)
            return -1
        url = None
    logging.basicConfig(
        level=getattr(logging, opts.log_level.upper()),
        stream=sys.stderr
        )
    app = load_app(url, opts.config, opts.tables, opts.debug)
    server = loadserver(server_map[opts.server])
    try:
        server(app)
    except (KeyboardInterrupt, SystemExit):
        pass
    return 0

def load_app(url=None, config=None, tables=None, debug=False):
    if not config:
        assert url, "Must provide a DB url if no config dict is given"
    config = config or {
        'rum.repositoryfactory': {
            'use': 'sqlalchemy',
            'sqlalchemy.url': url,
            'sqlalchemy.convert_unicode': True,
            'reflect': tables or 'all',
        },
        'rum.viewfactory': {
            'use': 'toscawidgets',
        }
    }
    return RumApp(config, debug=debug)

#TODO: Add more servers, fcgi, etc...
server_map = {
    'cherrypy': 'egg:PasteScript#cherrypy',
    'paste': 'egg:Paste#http',
    }

#
# A parser for command line options
#
parser = OptionParser(usage="%prog [options] url")
parser.add_option('-d', '--debug',
                  dest='debug',
                  help='Turn on debug mode',
                  default=False,
                  action='store_true')
parser.add_option('-c', '--config',
                  dest='config',
                  help='An optional config file to fine-tune options',
                  default=None)
parser.add_option('-l', '--log-level',
                  dest='log_level',
                  help='Verbosity level (default: INFO)',
                  default='INFO')
parser.add_option('-s', '--server',
                  dest='server',
                  help='WSGI server (default: cherrypy, '\
                       'available=[%s])' % '|'.join(server_map.keys()),
                  default='cherrypy')
parser.add_option('-t', '--table',
                  dest='tables',
                  action='append',
                  help='Specify which tables to load. This option may be used '\
                       'several times to specify multiple tables. If none is '\
                       'specified then all tables will be loaded',
                  default=[])

if __name__ == '__main__':
    sys.exit(rumalchemy(sys.argv))
