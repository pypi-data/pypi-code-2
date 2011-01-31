#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.


class Error(Exception):
    """Base class for python-cli errors."""

    def __init__(self, message=None, **kwargs):
        if message is None:
            message = self.__doc___
        super(Error, self).__init__(message)
        for key in kwargs:
            setattr(self, key, kwargs[key])


class ParseError(Error):
    """Error parsing command line."""


class CommandError(Error):
    """Illegal command."""
