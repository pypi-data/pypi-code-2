from hashdb_output import log
from hashdb_config_base import *
import re

def parse_config_updatedb(filename='/etc/updatedb.conf'):
    re_namevalue = re.compile(
        r'''
        ^                 # begining of line
        \s*               # whitespace
        (?P<n>[a-zA-Z_]+) # name
        \s*               # whitespace
        =                 # =
        \s*               # whitespace
        "(?P<v>.*?)"      # quoted value
        .*                # whitespace/garbage/ignored
        $                 # end of string
        ''',
        re.VERBOSE
    )

    parse_mappings = {
        'prunefs'           : ('skip_fstypes'    , parse_text__filenames),
        'prunenames'        : ('skip_names'      , parse_text__filenames),
        'prunepaths'        : ('skip_paths'      , parse_text__filenames),
        'prune_bind_mounts' : ('skip_binds'      , parse_text__boolean),
    }

    try:
        settings = {}
        with open(filename, "rt") as f:
            for name, value in [(m.group('n').lower(), m.group('v')) for m in [re_namevalue.match(line) for line in f.readlines()] if m != None]:
                if name not in parse_mappings:
                    log.warning('warning: unknown setting (%s) in updatedb config (%s)' % (name, filename))
                else:
                    target, fparse = parse_mappings[name]
                    settings[target] = fparse(value)
        return settings
    except IOError, ex:
        log.warning('warning: unable to open updatedb config file (%s): %s' % (filename, ex))
        print >> stderr, 'warning: %s' % ex
        return {}
