import os
import imp

from blazeutils.datastructures import OrderedDict
import pkg_resources

import blazech.locations as locs

def gather_commands():
    found = OrderedDict()
    # from installed python packages
    for p in pkg_resources.iter_entry_points('blazech.commands'):
        cmd = p.load()
        found[cmd.name] = cmd

    # from the system path
    found.update(find_path_commands(locs.system_commands_dir))

    # from the user path
    found.update(find_path_commands(locs.user_commands_dir))

    return found

def find_path_commands(dpath):
    found = OrderedDict()
    if not os.path.isdir(dpath):
        return found
    for fname in os.listdir(dpath):
        full_path = os.path.join(dpath, fname)
        basename, ext = os.path.splitext(fname)
        if os.path.isfile(full_path) and basename.startswith('command_') and ext == '.py':
            mod = imp.load_source(basename, full_path)
            found[mod.Command.name] = mod.Command
    return found
