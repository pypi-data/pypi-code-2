from hashdb_output import log
from hashdb_config_base import *
import re

def parse_config_file(filename='/etc/hashdb.conf'):
    re_namevalue = re.compile(
        r'''
        ^                 # begining of line
        \s*               # whitespace
        (?P<n>[a-zA-Z_]+) # name
        \s*               # whitespace
        =                 # =
        \s*               # whitespace
        (?P<v>.*?)        # value
        \s*               # whitespace
        $                 # end of string
        ''',
        re.VERBOSE
    )
    re_skip = re.compile(
        r'''
        ^
        (?:
            \s*  |
            (?: ; | \# | // ) .*
        )
        $
        ''',
        re.VERBOSE
    )

    # name: (target, parser, default, fcombine)
    parse_mappings = {
        'verbosity'      : ('verbosity'      , parse_text__verbosity,        None, lambda x,y: y),
        'use_updatedb'   : ('updatedb'       , parse_text__boolean,          None, lambda x,y: y),
        'database'       : ('database'       , parse_text__filename,         None, lambda x,y: y),
        'combine'        : ('combine'        , parse_text__database_combine, [],   lambda x,y: x + [y]),
        'walk_depth'     : ('walk_depth'     , parse_text__boolean,          None, lambda x,y: y),
        'targets'        : ('targets'        , parse_text__filenames,        [],   lambda x,y: x + y),
        'hash_definitive': ('hash_definitive', parse_text__boolean,          None, lambda x,y: y),
        'hash_force'     : ('hash_force',      parse_text__boolean,          None, lambda x,y: y),
        'match_check'    : ('match_check',     parse_text__boolean,          None, lambda x,y: y),
        'match_any'      : ('match_any',       parse_text__boolean,          None, lambda x,y: y),
        'skip_fstypes'   : ('skip_fstypes'   , parse_text__filenames,        [],   lambda x,y: x + y),
        'skip_paths'     : ('skip_paths'     , parse_text__filenames,        [],   lambda x,y: x + y),
        'skip_names'     : ('skip_names'     , parse_text__filenames,        [],   lambda x,y: x + y),
        'skip_dirnames'  : ('skip_names'     , parse_text__filenames,        [],   lambda x,y: x + y),
        'skip_filenames' : ('skip_filenames' , parse_text__filenames,        [],   lambda x,y: x + y),
        'target'         : ('targets'        , parse_text__filename,         [],   lambda x,y: x + [y]),
        'skip_fstype'    : ('skip_fstypes'   , parse_text__filename,         [],   lambda x,y: x + [y]),
        'skip_path'      : ('skip_paths'     , parse_text__filename,         [],   lambda x,y: x + [y]),
        'skip_name'      : ('skip_names'     , parse_text__filename,         [],   lambda x,y: x + [y]),
        'skip_dirname'   : ('skip_names'     , parse_text__filename,         [],   lambda x,y: x + [y]),
        'skip_filename'  : ('skip_filenames' , parse_text__filename,         [],   lambda x,y: x + [y]),
        'skip_binds'     : ('skip_binds'     , parse_text__boolean,          None, lambda x,y: y),
    }

    try:
        settings = {}
        with open(filename, 'rt') as f:
            for lineno, line in enumerate(f):
                match = re_namevalue.match(line)
                if not match:
                    match = re_skip.match(line)
                    if not match:
                        log.warning('warning: invalid line in config file (lineno: %d)' % lineno)
                    continue

                name  = match.group('name').lower()
                value = match.group('value')

                if name not in parse_mappings:
                    log.warning('warning: unknown setting (%s) in config file (%s)' % (name, filename))
                else:
                    target, fparse, default, fcombine = parse_mappings[name]

                    try:
                        value = fparse(value)
                    except Exception, ex:
                        log.warning('warning: invalid setting (%s) for (%s) in config file (%s)' % (value, name, filename))

                    settings[target] = fcombine(settings.get(target, default), value)
        return settings
    except IOError, ex:
        log.warning('warning: unable to open config file (%s): %s' % (filename, ex))
        return {}