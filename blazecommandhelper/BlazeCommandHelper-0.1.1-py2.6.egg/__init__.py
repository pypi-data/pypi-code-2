import os
import logging
import sys

from blazeutils.error_handling import traceback_depth_in, traceback_depth
from blazeutils.importing import import_string
from blazeutils.strings import randchars, case_us2cw

from blazech.baseparser import parser, subparsers
from blazech.config import parse_config_files
from blazech.locations import set_paths
from blazech.log import setup_logging, VERBOSITY_FLAG_MAP
from blazech.utils import gather_commands

def run_batch(initial_args=None):
    if initial_args is None:
        initial_args = sys.argv[1:]
    options, args = parser.parse_args(initial_args)
    if not args:
        parser.error('You must give a job to run (use "bch --help" for usage)')
    settings = parse_config_files(options.use_system_configs, options.config_files)
    if options.quiet:
        settings.console.verbosity = 'none'
    if options.verbosity > 3:
        parser.error('verbosity too high, max is -vvv')
    if options.verbosity > 0:
        settings.console.verbosity = VERBOSITY_FLAG_MAP[options.verbosity]
        if options.verbosity >= 2:
            settings.console.inc_errors = True
    return Batch(settings, args).run()

def run_cmd(initial_args=None, load_test_plugins=False):
    # some environment setup
    load_test_plugins = os.environ.get('BCH_LOAD_TEST_PLUGINS', load_test_plugins)
    if load_test_plugins == '0':
        load_test_plugins = False
    use_test_config = os.environ.get('BCH_USE_TEST_CONFIG', None)
    if use_test_config:
        from blazech.tests.helpers import set_test_fpath_root
        set_test_fpath_root(use_test_config)

    # settings setup
    settings = parse_config_files(True, None)

    # where do the args come from?
    if initial_args is None:
        initial_args = sys.argv[1:]

    # add the sub-commands to the parser
    for cmd in gather_commands().values():
        if load_test_plugins or 'blazech' not in cmd.__module__:
            cmd(subparsers)

    # if there are no subparsers, then we need to exit
    if len(subparsers._get_subactions()) == 0:
        parser.error('Error: no command plugins registered')

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
main = run_cmd

class Batch(object):
    def __init__(self, settings, jobs):
        self.settings = settings
        self.jobs = jobs
        self.ident = randchars(5)

        self._setup_logging()

    def _setup_logging(self):
        setup_logging(self.settings)
        self.log = logging.getLogger('blazech.Batch(%s)' % self.ident)

    def run(self):
        self.log.minimal('batch started')
        for jname in self.jobs:
            try:
                jsettings = self.settings.job[jname]
                action_class_name = case_us2cw(jsettings._action_)
                self.log.vdebug('job %s is using action %s which maps to %s', jname, jsettings._action_, action_class_name)
                try:
                    aclass = import_string('blazech.actions:%s' % action_class_name)
                except AttributeError, e:
                    if not traceback_depth_in(1):
                        raise
                    aclass = None
                if aclass is None:
                    self.log.minimal('job %s could not be run: the action class %s can not be imported', jname, action_class_name)
                    continue
                try:
                    self.log.minimal('running job %s', jname)
                    aclass(self, jsettings).execute()
                except:
                    self.log.exception('job %s raised an exception', jname)
                    self.log.minimal('job %s raised an exception', jname)
            except KeyError, e:
                if jname not in str(e):
                    raise
                self.log.minimal('job %s could not be run: its settings were not found', jname)
            except AttributeError, e:
                if 'no attribute \'_action_\'' in str(e):
                    self.log.minimal('job %s could not be run: it did not have an _action_ setting', jname)
                elif 'no attribute \'job\'' in str(e):
                    self.log.minimal('job %s could not be run: no jobs have been configured', jname)
                else:
                    raise
        self.log.minimal('batch completed')
