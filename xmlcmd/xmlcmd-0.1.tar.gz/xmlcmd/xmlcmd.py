#!/usr/bin/python
"""
xmlcmd.py - support for adding an --xml option to various commands

Ben Bass 2011. (Public Domain)
"""

import sys
import os
import which

def process_cmd(cmd_name, args, orig_cmd_path):
    """
    import and call the main() function from the module
    xmlcmd._{cmd}
    """
    module = __import__('xmlcmd._%s' % cmd_name,
                        fromlist=['_%s' % cmd_name])
    raise SystemExit(module.main(args, orig_cmd_path))

def main(args=None):
    """
    run system command from sys.argv[:], where sys.argv[0]
    implies the real command to run (e.g. via symlinks to us)
    """
    if args is None:
        args = sys.argv

    # args[0] will be a full path - we only want the command name
    cmd_name = os.path.basename(args[0])
    if cmd_name.startswith('xmlcmd'):
        raise SystemExit('xmlcmd should not be called directly')

    # get the command which would have run if we hadn't sneaked
    # ahead of it in the $PATH
    cmd_path_gen = which.whichgen(cmd_name)
    cmd_path_gen.next()   # skip first match (us)
    orig_cmd_path = cmd_path_gen.next()

    if '--xml' in args:
        args.remove('--xml')
        # forward to our xmlized version...
        process_cmd(cmd_name, args, orig_cmd_path)
    else:
        # execv *replaces* this process, so it has no idea it
        # wasn't called directly. Total transparency.
        os.execv(orig_cmd_path, args)

if __name__ == '__main__':
    main()
