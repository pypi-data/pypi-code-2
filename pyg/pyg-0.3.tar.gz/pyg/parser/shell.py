import sys
import cmd
import difflib

from pyg.parser.parser import init_parser
from pyg.types import PygError, InstallationError, AlreadyInstalled


SUPPORTED_COMMANDS = ['install', 'uninstall', 'rm', 'list', 'freeze', 'link',
                      'unlink', 'search', 'download', 'check', 'update']

def command_hook(attr):
    def wrapper(*args, **kwargs):
        if attr == 'EOF':
            print '\n'
            return True
        print '*** Unknown command: {0}'.format(attr)
        close = difflib.get_close_matches(attr, SUPPORTED_COMMANDS, n=1, cutoff=0.5)
        if close:
            print 'Did you mean this?\n\t{0}'.format(close[0])
    return wrapper

def command(parser, cmd_name):
    def internal(args):
        try:
            return parser.dispatch([cmd_name] + args.split())
        except (SystemExit, AlreadyInstalled, PygError):
            pass
    return internal
    

class PygShell(cmd.Cmd, object):
    def __init__(self, *args, **kwargs):
        self.prompt = 'pyg> '
        self.parser = init_parser(__import__('pyg').__version__)
        super(PygShell, self).__init__(*args, **kwargs)

    def __getattr__(self, attr):
        if attr.startswith('do_'):
            attr = attr[3:]
            if not attr in SUPPORTED_COMMANDS:
                return command_hook(attr)
            return command(self.parser, attr)
        else:
            return object.__getattr__(self, attr)