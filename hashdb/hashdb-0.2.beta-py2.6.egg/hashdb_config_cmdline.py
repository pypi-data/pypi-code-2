#!/usr/bin/python

from hashdb_output import log, VERBOSE, QUIET, DEBUG, DEFAULT
from hashdb_config_base import *
import argparse

def parse_commandline(fparse):
    def func(text):
        try:
            return fparse(text)
        except ValueError, ex:
            raise argparse.ArgumentTypeError('%s' % ex.message)
    return func

def parse_config_commandline():
    parser = argparse.ArgumentParser(prog='hashdb')

    # verbosity
    ##verbosity = parser.add_argument_group('verbosity')
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.set_defaults(verbosity=None)
    verbosity.add_argument('-v', '--verbose', action='store_const', const=VERBOSE, dest='verbosity', help='provide verbose output')
    verbosity.add_argument('-q', '--quiet', action='store_const', const=QUIET, dest='verbosity', help='supress output')
    verbosity.add_argument('--debug', action='store_const', const=DEBUG, dest='verbosity', help='provide debugging output')
    verbosity.add_argument('--normal', action='store_const', const=DEFAULT, dest='verbosity', help='provide normal output')

    # config (hashdb)
    ##config = parser.add_argument_group('config')
    config = parser.add_mutually_exclusive_group()
    config.set_defaults(config='/etc/hashdb.conf')
    config.add_argument('--no-config', dest='config', action='store_const', const=None, help='do not use (any) config file')
    config.add_argument('--config', dest='config', type=parse_commandline(parse_text__filename), help='extract options from specified config file (commandline arguments take precedence)')

    # config (updatedb)
    ##updatedb = parser.add_argument_group('updatedb')
    updatedb = parser.add_mutually_exclusive_group()
    updatedb.set_defaults(updatedb=None)
    updatedb.add_argument('--no-updatedb', dest='updatedb', action='store_false', help='do not import settings from updatedb config file')
    updatedb.add_argument('--use-updatedb', dest='updatedb', action='store_true', help='import settings from updatedb config file')

    # config (walking)
    ##walk = parser.add_argument_group('walk')
    walk = parser.add_mutually_exclusive_group()
    walk.set_defaults(
        walk_depth=None
        )
    walk.add_argument('--depth', dest='walk_depth', action='store_true',
        help='Perform depth-first walking of the directory tree (default)')
    walk.add_argument('--breadth', dest='walk_depth', action='store_false',
        help='Perform breadth-first walking of the directory tree')

    # config (database/s)
    database = parser.add_argument_group('database/s')
    database.set_defaults(
        database=None,
        combine=[]
    )
    database.add_argument('--database', type=parse_commandline(parse_text__filename), dest='database', help='specify the primary database to operate on/with')
    database.add_argument('--combine', metavar="LOCAL:DB:REMOTE", type=parse_commandline(parse_text__database_combine), dest='combine', action='append', help=\
        "Combine the specified database with the primary database, including only the subtree specified by REMOTE and grafting it into position LOCAL.\n" +
        "The format for this option is\n" +
        " \"local-path:database-path:remote-path\"\n" +
        "  eg.\n"+
        "  /mnt/remoteserver/home/user/data:/mnt/remoteserver/var/lib/hashdb/hashdb.db:/home/user/data"
    )

    # config (skipers)
    skip = parser.add_argument_group('skip')
    skip.set_defaults(
        skip_fstypes=[],
        skip_paths=[],
        skip_names=[],
        skip_dirnames=[],
        skip_filenames=[],
        skip_binds=None
    )
    skip.add_argument('--skip-fstype', dest='skip_fstypes', action='append', metavar='FSTYPE',
        help='Do not index files from disks with the specified file system (unless specified as a starting point)')
    skip.add_argument('--skip-path', dest='skip_paths', action='append', metavar='PATH',
        help='Do not index files contained within the given path')
    skip.add_argument('--skip-name', dest='skip_names', action='append', metavar='PATH',
        help='Do not index files with the given (base) name. (may contain globbing characters)')
    skip.add_argument('--skip-dirname', dest='skip_dirnames', action='append', metavar='PATH',
        help='Do not index directories with the given (base) name. (may contain globbing characters)')
    skip.add_argument('--skip-filename', dest='skip_filenames', action='append', metavar='PATH',
        help='Do not index files with the given (base) name. (may contain globbing characters)')
    skip.add_argument('--skip-binds', dest='skip_binds', action='store_true',
        help='Do not index files contained within a bind mount (default unless overridden in config)')
    skip.add_argument('--keep-binds', dest='skip_binds', action='store_false',
        help='Allow indexing of files contained within a bind mount')

    # commands
    subparser = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands')

    # command 'hash'
    cmd_hash = subparser.add_parser('hash',
        help='Perform a hash on all specified TARGETs (default)')
    cmd_hash.set_defaults(
        cmd='hash',
        hash_definitive=None,
        hash_force=None)

    group = cmd_hash.add_mutually_exclusive_group()
    group.add_argument('--not-definitive', dest='hash_definitive', action='store_false',
        help='TARGETs are only updated, no targets are removed (default)')
    group.add_argument('--definitive', dest='hash_definitive', action='store_true',
        help='Any targets stored in the database which are not accessible via TARGETs will be discarded')

    group = cmd_hash.add_mutually_exclusive_group()
    group.add_argument('--no-force', dest='hash_force', action='store_false',
        help='Only rehash TARGETs as required')
    group.add_argument('--force', dest='hash_force', action='store_true',
        help='Force re-hash of all TARGETs')

    # command 'match'
    cmd_match = subparser.add_parser('match',
        help='Find duplicates of any files specifed via TARGETs')
    cmd_match.set_defaults(
        cmd='match',
        match_check=None,
        match_any=None)

    group = cmd_match.add_mutually_exclusive_group()
    group.add_argument('--check', dest='match_check', action='store_true',
        help='Check to see if duplicate files are still accesssible on the system (default)')
    group.add_argument('--no-check', dest='match_check', action='store_false',
        help='Do not check to see if duplicate files are still accesssible on the system')

    group = cmd_match.add_mutually_exclusive_group()
    group.add_argument('--any', dest='match_any', action='store_true',
        help='Match against files anywhere on the system (that have been previously hashed) (default)')
    group.add_argument('--only-targets', dest='match_any', action='store_false',
        help='Match against files only within the TARGET specification')

    # command 'view'
    cmd_view = subparser.add_parser('view',
        help='Display everything in the database matching TARGETs')
    cmd_view.set_defaults(
        cmd='view')

    # targets
    parser.set_defaults(targets=[])
    for p in [cmd_hash, cmd_match, cmd_view]:
        p.add_argument('targets', metavar='TARGET', nargs='*',
            help='List of target files and folders to hash')

    # parse args
    args = parser.parse_args()

    #print args

    # extract final settings
    settings = {}
    if args.verbosity != None:
        settings['verbosity'] = args.verbosity
    if args.config != None:
        settings['config'] = args.config
    if args.updatedb != None:
        settings['updatedb'] = args.updatedb
    if args.database != None:
        settings['database'] = args.database
    if args.walk_depth != None:
        settings['walk_depth'] = args.walk_depth
    if (args.targets != None) and len(args.targets) != 0:
        settings['targets'] = args.targets
    settings.update({
        'combine'       : args.combine,
        'skip_fstypes'  : args.skip_fstypes,
        'skip_paths'    : args.skip_paths,
        'skip_names'    : args.skip_names,
        'skip_dirnames' : args.skip_dirnames,
        'skip_filenames': args.skip_filenames,
    })
    if args.skip_binds != None:
        settings['skip_binds'] = args.skip_binds

    if args.cmd == 'hash':
        settings['cmd'] = 'hash'
        if args.hash_definitive != None:
            settings['hash_definitive'] = args.hash_definitive
        elif ('targets' in settings):
            settings['hash_definitive'] = False
        if args.hash_force != None:
            settings['hash_force'] = args.hash_force
        elif ('targets' in settings):
            settings['hash_force'] = False
    elif args.cmd == 'match':
        settings['cmd'] = 'match'
        if args.match_check != None:
            settings['match_check'] = args.match_check
        if args.match_any != None:
            settings['match_any'] = args.match_any
    elif args.cmd == 'view':
        settings['cmd'] = 'view'

    return settings

if __name__ == '__main__':
    print parse_config_commandline()