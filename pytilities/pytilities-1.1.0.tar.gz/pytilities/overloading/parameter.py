# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import logging

from .matchers import matches_everything, matches_type

_logger = logging.getLogger("pytilities.overloading.parameter")

class Parameter(object):

    """
    A parameter of an operation.
    
    It can match arguments and provide default values for them.

    Note that an argument matches a parameter, if its matcher returns True on
    the argument value or the parameter has a default.
    """

    # support multiple types per param? Wait for a feature request first
    def __init__(self, name, *args, **kwargs):
        """
        Construct a `Parameter`.

        :param name: name of parameter as specified in keyword arguments
        :type name: string

        :param kwargs: Keyword parameters:

            - `type_` or `types` or `matcher`:
                type\_: type of the parameter
                types: iterable of possible types for the parameter
                matcher: a matcher function of type f(value) -> matched::bool

                If given as first positional arg, type\_ is assumed.
                If not given, will match any value.
            
            - `default`:
                default value for the parameter. Omit if param has no default
                
                Can also be given as second positional arg.

        :Preconditions: 1. `default` must match the specified matcher
        """
        assert name, "Name param musn't be empty or None"
        assert isinstance(name, str), "Name must be a string"
        assert len(args) <= 2, \
            "Unexpected trailing args: %s" % args
        assert not (args and "type_" in kwargs), (
            "type_ specified twice: by *args(%s) and **kwargs(%s)" %
            (args[0], kwargs["type_"]))
        assert not (len(args) > 1 and "default" in kwargs), (
            "default specified twice: by *args(%s) and **kwargs(%s)" %
            (args[1], kwargs["default"]))

        self.__name = name

        # look for a match thingy
        if args:
            self._matcher = matches_type(args[0])
        elif 'type_' in kwargs:
            self._matcher = matches_type(kwargs['type_'])
        elif 'types' in kwargs:
            self._matcher = matches_type(kwargs['types'])
        elif 'matcher' in kwargs:
            self._matcher = kwargs['matcher']
        else: # default match all
            self._matcher = matches_everything

        if len(args) > 1:
            self._default = args[1]
        elif "default" in kwargs:
            self._default = kwargs["default"]

        assert not hasattr(self, '_default') or \
                self._matcher(self._default), (
                "Default must match the given matcher as well. (Precondition 1) Default: %s" %
                    (self._default))

        # whether or not last read was a match
        self.__matched = False

    @property
    def name(self):
        return self.__name

    # Note: the two step (read all, then write) process is necessary to allow for
    # self validating parameters in the future. This allows them to return True at
    # read when they match, and throw errors at write when the overload apparantly
    # matched and their values will actually be used. (at time of read that is not
    # yet certain)
    def read_arg(self, arg):
        """
        Read/process the given arg.
        
        :param arg: the argument value to read

        :return: True if parameter matches `arg`
        :rtype: bool
        """
        self.__value = arg
        self.__matched = self._matcher(self.__value)
        return self.__matched

    def read_kwargs(self, kwargs):
        """
        Look in a dict for a matching arg and process its value.

        :param kwargs: frozen dictionary of arguments

        :return: True if a matching argument was found in `kwargs`
        :rtype: bool
        """

        if self.__name in kwargs:
            return self.read_arg(kwargs[self.__name])
        elif hasattr(self, '_default'):
            self.__matched = True
            self.__value = self._default
        else:
            self.__matched = False

        return self.__matched

    def write(self, kwargs):
        """
        Adds the last read argument value to a dictionary.

        :param kwargs: the dictionary to add the last value and the parameter name to

        :Preconditions: 1. the parameter matched on the last read
        """

        assert self.__matched, \
               "write() may only be called after a succesful read()"

        kwargs[self.__name] = self.__value

    @property
    def _matched(self):
        return self.__matched

    def __str__(self):
        if hasattr(self, '_default'):
            default = str(self._default)
        else:
            default = ''

        return 'Parameter(name=%s, default=%s)' % (self.__name, default)

# a shortcut
Param = Parameter

