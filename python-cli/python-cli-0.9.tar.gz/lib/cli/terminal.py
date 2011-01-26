#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.


class Terminal(object):
    """Base class for terminal objects."""

    width = None
    height = None

    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def clear(self):
        raise NotImplementedError

    def set_echo(self, echo):
        raise NotImplementedError
