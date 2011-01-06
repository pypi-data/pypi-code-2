#!/usr/bin/python
from hashdb_output import log, VERBOSE, QUIET, DEBUG, DEFAULT

def parse_config(settings=None):
    settings_args     = settings
    settings_config   = {}
    settings_updatedb = {}
    settings_final    = {}

    if settings_args == None:
        import hashdb_config_cmdline
        settings_args = hashdb_config_cmdline.parse_config_commandline()

    filename = settings_args.get('config', '/etc/hashdb.conf')
    if filename != None:
        import hashdb_config_file
        settings_config = hashdb_config_file.parse_config_file(filename) or settings_config

    updatedb = settings_args.get('updatedb', None)
    if updatedb == None:
        updatedb = settings_config.get('updatedb', True)
    if updatedb:
        import hashdb_config_updatedb
        settings_updatedb = hashdb_config_updatedb.parse_config_updatedb() or settings_updatedb


    # merge settings
    stack = [settings_args, settings_config, settings_updatedb]

    # flatten
    for name, default in [
            ('verbosity', DEFAULT),
            ('database', '/var/lib/hashdb/hashdb.db'),
            ('skip_binds', False),
            ('targets', ['']),
            ('cmd', 'hash'),
            ('hash_definitive', False),
            ('hash_force', False),
            ('match_check', True),
            ('match_any', True),
            ('walk_depth', True)
            ]:
        for source in stack:
            if name in source:
                settings_final[name] = source[name]
                break
        else:
            settings_final[name] = default

    # merge
    for name in ['skip_fstypes', 'skip_paths', 'skip_names', 'skip_dirnames', 'skip_filenames', 'combine']:
        settings_final[name] = []
        for source in stack:
            settings_final[name].extend(source.get(name, []))

    return settings_final

def display_settings(settings, fprint=log.debug):
    keys = list(settings.keys())
    keys.sort()
    padd = max(map(len, keys))

    for k in keys:
        fprint('%-*s:%r' % (padd, k, settings[k]))

if __name__ == '__main__':
    settings = parse_config()
    display_settings(settings)
