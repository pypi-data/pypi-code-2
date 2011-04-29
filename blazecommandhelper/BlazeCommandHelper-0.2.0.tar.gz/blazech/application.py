import imp
import os
import sys

import pkg_resources

from blazech.baseparser import parser, subparsers
from blazech.commands import BaseCommand
from blazech.config import parse_config_files
import blazech.locations as locs
from blazech.locations import set_paths
from blazech.log import setup_logging, VERBOSITY_FLAG_MAP

class Application(object):
    """
        A class that represents a command line application
    """
    def __init__(self, name, cmd_entry_point=None, cmd_file_prefix=None,
                 use_test_config=None):
        self.name = name
        self.cmd_entry_point = cmd_entry_point or '%s.commands' % self.name
        self.cmd_file_prefix = cmd_file_prefix or '%s_cmd_' % self.name

        # some environment setup
        self.use_test_config = os.environ.get('BCH_USE_TEST_CONFIG', None)
        if self.use_test_config:
            from blazech.tests.helpers import set_test_fpath_root
            set_test_fpath_root(self.use_test_config)

        # initilize commands
        self._commands = {}
        self._gather_commands()

    def _gather_commands(self):
        # from installed python packages
        for p in pkg_resources.iter_entry_points(self.cmd_entry_point):
            cmd = p.load()
            self._commands[cmd.name] = cmd

        # from the system path
        self._load_path_commands(locs.system_commands_dir)

        # from the user path
        self._load_path_commands(locs.user_commands_dir)

    def _load_path_commands(self, dpath):
        if not os.path.isdir(dpath):
            return
        for fname in os.listdir(dpath):
            full_path = os.path.join(dpath, fname)
            basename, ext = os.path.splitext(fname)
            if os.path.isfile(full_path) and basename.startswith(self.cmd_file_prefix) and ext == '.py':
                mod = imp.load_source(basename, full_path)
                self._commands[mod.Command.name] = mod.Command

    def load_commands(self, load_from):
        """
            ``load_from`` can be a module or dictionary (usually from globals()
            or locals())
        """
        if not isinstance(load_from, dict):
            try:
                load_from = vars(load_from)
            except TypeError, e:
                if 'vars() argument' not in str(e):
                    raise
                raise TypeError('Expected "load_from" to be a dictionary or module')

        for obj in load_from.values():
            try:
                if issubclass(obj, BaseCommand) and obj is not BaseCommand and obj.name is not None:
                    self._commands[obj.name] = obj
            except TypeError, e:
                if 'issubclass() arg 1 must be a class' not in str(e):
                    raise

    def run_cmd(self, initial_args=None):
        # settings setup
        settings = parse_config_files(True, None)

        # where do the args come from?
        if initial_args is None:
            initial_args = sys.argv[1:]

        # add the sub-commands to the parser
        commands = self._commands.values()
        commands.sort(key=lambda x:x.name)
        for cmd in commands:
            cmd(subparsers)

        # if there are no subparsers, then we need to exit
        if len(subparsers._get_subactions()) == 0:
            parser.error('Error: no commands found or registered')

        # parse the arguments
        args = parser.parse_args()

        # verbosity and quite sanity checks
        if args.verbosity > 3:
            parser.error('verbosity too high, max is -vvv')
        if args.quiet and args.verbosity:
            parser.error('can not set quiet and verbose options')

        # verbosity log setup
        if args.quiet:
            settings.console.verbosity = 'none'
        if args.verbosity > 0:
            settings.console.verbosity = VERBOSITY_FLAG_MAP[args.verbosity]
            if args.verbosity >= 2:
                settings.console.inc_errors = True

        # log setup
        setup_logging(settings)

        # call the function the command told us to call
        args.func(parser, args)

class _BCHApp(Application):
    def __init__(self):
        Application.__init__(self, 'blazech', cmd_file_prefix='command_')
