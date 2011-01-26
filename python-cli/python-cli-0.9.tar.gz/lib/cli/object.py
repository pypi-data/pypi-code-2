#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import sys


def create(cls, *args, **kwargs):
    """This is our default constructor. It takes care of instantiating the
    right subclass, and configuring it in the right way."""
    from cli.settings import Settings
    from cli.terminal import Terminal
    if issubclass(cls, Settings):
        obj = cls(ignore_unknown=True)
        obj.load_config_file()
        obj.update(**kwargs)
        obj.ignore_unknown = False
    elif issubclass(cls, Terminal):
        obj = cls(sys.stdin, sys.stdout, sys.stderr, **kwargs)
    else:
        obj = cls(*args, **kwargs)
    return obj
