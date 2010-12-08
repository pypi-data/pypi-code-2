import argparse

class CountAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current_count = getattr(namespace, self.dest, None)
        if current_count is None:
            setattr(namespace, self.dest, 1)
        else:
            setattr(namespace, self.dest, current_count + 1)

parser = argparse.ArgumentParser()

parser.add_argument(
    '-v', '--verbose',
    dest='verbosity',
    action=CountAction,
    nargs=0,
    help='set level of console verbosity (max = -vvv)')
parser.add_argument(
    '-q', '--quiet',
    dest='quiet',
    action='store_true',
    help='turn off console output')

subparsers = parser.add_subparsers(dest='subparser')
#parser.add_option(
#    '-c', '--config-file',
#    dest='config_files',
#    action='append',
#    help='Full or relative path to config file (can be specified more than once)')
#parser.add_option(
#    '-n', '--no-system-configs',
#    dest='use_system_configs',
#    action='store_false',
#    help='when set, system and user config files will not be loaded even if available')
#parser.add_option(
#    '--log',
#    dest='log',
#    metavar='FILENAME',
#    help='Log file where a complete (maximum verbosity) record will be kept')
#parser.add_option(
#    # Writes the log levels explicitely to the log'
#    '--log-explicit-levels',
#    dest='log_explicit_levels',
#    action='store_true',
#    default=False,
#    help=optparse.SUPPRESS_HELP)
#parser.add_option(
#    # The default log file
#    '--local-log', '--log-file',
#    dest='log_file',
#    metavar='FILENAME',
#    default=default_log_file,
#    help=optparse.SUPPRESS_HELP)
