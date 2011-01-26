#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from fnmatch import fnmatch
from cli.error import ParseError, CommandError


class Command(object):
    """Base class for all commands."""

    name = None
    aliases = ()
    usage = '%command'
    description = None
    helptext = None

    nargs = 0
    allowed_options = [
        ('--help', None)
    ]

    def __init__(self, args, opts):
        self.options = self.parse_opts(opts)
        self.args = self.parse_args(args)

    def parse_args(self, args):
        if '--help' in self.options:
            return
        if isinstance(self.nargs, int):
            nargs = (self.nargs,)
        else:
            nargs = self.nargs
        if len(args) not in nargs:
            # Some hackery to get a nice error message. Not sure if this can
            # be localized properly in all languages.
            nargs = [ str(n) for n in nargs ]
            nargs = filter(None, [', '.join(nargs[:-1])] + [nargs[-1]])
            nargs = ' or '.join(nargs)
            if nargs == '1':
                noun = 'argument'
            else:
                noun = 'arguments'
            self.error('expecting %s %s (got: %s)' % (nargs, noun, len(args)))
        return args

    def parse_opts(self, opts):
        validated = {}
        for key,value in opts:
            for name,validator in self.allowed_options:
                if not fnmatch(key, name):
                    continue
                if validator is None:
                    if value is not None:
                        self.error('option %s takes no argument (provided: %s)' %
                                   (key, value))
                else:
                    try:
                        value = validator(opts[opt])
                    except ValueError:
                        self.error('could not validate option %s (provided: %s)' %
                                   (key, value))
                validated[key] = value 
                break
            else:
                self.error('unknown option: %s' % key)
        return validated

    def show_help(self):
        usage = self.usage.replace('%command', self.name) \
                          .replace('\n', '\n       ')
        stdout = self.context.terminal.stdout
        stdout.write('usage: %s\n' % usage)
        if self.helptext:
            stdout.write('%s\n' % self.helptext)

    def run(self):
        raise NotImplementedError

    def execute(self, context):
        self.context = context
        if '--help' in self.options:
            self.show_help()
        else:
            self.run()

    def error(self, message, status=None):
        if status is None:
            from cli.context import ExecutionContext
            status = ExecutionContext.STATUS_ERR_COMMAND
        raise CommandError(message, status=status, command=self.name)
