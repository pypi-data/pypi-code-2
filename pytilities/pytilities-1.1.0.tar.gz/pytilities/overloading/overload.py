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

_logger = logging.getLogger("pytilities.overloading.overload")

class Overload(object):
    """
    A list of parameters that when matched, call an associated operation.

    You can think of it as part of an operation signature

    Methods:

        - `process_call`: Call overload's operation if args match.
        - `insert_params`: Insert parameters
    """

    def __init__(self, operation, *params):
        """
        Construct an Overload

        Parameters:
            
            `function`
                the operation to call when a call's args match the params

            `params` :: (Parameter...)
                sequence of parameters that args of calls should match. The
                overload will only match when all params are satisfied and no
                args are left.
        """
        self.__function = operation
        self.__params = []
        self.insert_params(0, *params)

    def process_args(self, *args, kwargs={}):
        """
        Process args and kwargs

        :return: (processed args, operation) if matched, None otherwise
        :rtype: ({string: object, callable}
        :param args: positional arguments
        :type args: (object, ...)
        :param kwargs: keyword arguments
        :type kwargs: {string: object}
        """

        # check for the right amount of args (the rest of the algorithm depends
        # on this). Note: this assumes there are no overlaps, so the debug
        # message may dictate the wrong reason, but this will do
        param_count = len(self.__params)
        arg_count = len(args) + len(kwargs)
        if param_count < arg_count:
            _logger.debug('Overload did not match: too many args:' \
                          + ' expected %s, got %s' % (param_count, arg_count))
            return

        # match args
        for arg, param in zip(args, self.__params):
            if not param.read_arg(arg):
                _logger.debug("Overload did not match: unsatisfied param: %s" %
                              param)
                return

        # match kwargs
        read_args = set()
        for param in self.__params[len(args):]:
            if not param.read_kwargs(kwargs):
                _logger.debug("Overload did not match: unsatisfied param: %s" %
                              param)
                return
            read_args.add(param.name)

        unused_args = (set(kwargs.keys()) - read_args)
        if unused_args:
            _logger.debug("Overload did not match: left-over args: %s" %
                          ', '.join(unused_args))
            return

        # we have a match
        # construct a list of arguments for the call
        call_args = {}
        for param in self.__params:
            param.write(call_args)

        # return args and func
        return (call_args, self.__function)

    def insert_params(self, index, *params):
        """
        Insert parameters into the current list of parameters at index

        Parameters:
            
            `index` :: number
                index of where to insert

            `params` :: (Parameter...)
                the parameters to insert
        """
        self.__params[index:index] = params

