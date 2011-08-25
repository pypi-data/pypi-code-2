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
    from cli.terminal import Terminal
    from optparse import OptionParser
    if issubclass(cls, Terminal):
        obj = cls(sys.stdin, sys.stdout, sys.stderr, **kwargs)
    elif issubclass(cls, OptionParser):
        obj = cls(*args, **kwargs)
        obj.disable_interspersed_args()
    else:
        obj = cls(*args, **kwargs)
    return obj
