from commandtool import Cmd

class BaseServeCmd(Cmd):

    arg_spec = [
      # ('IP_AND_PORT', 'The IP and port to serve on, eg `127.0.0.1:8000\'')#('architecture', "can be `wsgi' or `tornado'"),
    ]
    # The option_spec specifies which options are associated with 
    # each internal variable
    option_spec = {
        'help': dict(
            options = ['-h', '--help'],
            help = 'display this message'
        ),
        'profile': dict(
            options = ['--profile'],
            help = 'enable profiling'
        ),
        'port': dict(
            options = ['-p', '--port'],
            help = 'set the port, default 8000',
            metavar='PORT'
        ),
        'host': dict(
            options = ['-H', '--host'],
            help = 'set the host, default 127.0.0.1. Use 0.0.0.0 for production',
            metavar='HOST',
        )
    }
    help = {
        # If you leave start and end as None, values will be 
        # automatically generated
        'start': None,
        'end': None,
        # Used in the main command help to describe this command
    }

    def __init__(
        self, 
        handler, 
        help_summary='Serve the application'
    ):
        self.handler = handler
        self.help['summary'] = help_summary

    def on_run(self, site, args, opts):
        self.handler(
            site,
            'server',
            site.default_pipeline,
            host = opts.get('host', '127.0.0.1'),
            port = int(opts.get('port', '8000')),
            profile = opts.profile,
        )
        return 0

