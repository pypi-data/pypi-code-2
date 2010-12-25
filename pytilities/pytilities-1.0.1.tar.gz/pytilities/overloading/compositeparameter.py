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

from . import Parameter

_logger = logging.getLogger("pytilities.overloading.compositeparameter")

class CompositeParameter(Parameter):

    """
    `Parameter` that consists of more parameters.

    This parameter matches lists, tuples and dicts, of which all elements match
    the list of child parameters.

    When this parameter is written to a dict, its child parameters are
    expanded. E.g. for a composite parameter with childs 'x' and 'y', a read
    value of (1, 3) and a dict d of {}; after writing to d, d will equal {x:1, y:3},
    and not {{x:1, y:3}}.
    """

    def __init__(self, name, params, matcher = (tuple, list, dict), *args, **kwargs):
        """
        Construct a `CompositeParameter`.

        :param name: name of the parameter, used for keyword arguments. Must be
                     unique.
        :type name: string

        :param params: the child parameters of the composite
        :type params: (Parameter...)

        :param matcher: Either of:
            
            - f(value) -> matched:bool
            - (type...) = (tuple, list, dict)
            - type

            the parameter will match only if this matcher matches the arg
            and its child args match the elements of the arg. It is
            unlikely you'll need a value other than the default.
        
        :param default: default value for the parameter, omit if param has no default
        """
        Parameter.__init__(self, name, matcher, *args, **kwargs)
        self.__params = params
        self.__arg_matcher = self._matcher
        self._matcher = self.__match

    def __match(self, value):
        # is list, whatever
        if not self.__arg_matcher(value):
            return False

        # check count
        if len(value) != len(self.__params):
            return False

        # match child params
        if isinstance(value, dict):
            for param in self.__params:
                if not param.read_kwargs(kwargs):
                    _logger.debug("Overload failed to match, failed at %s" %
                                  param)
                    return False
        else:
            for arg, param in zip(value, self.__params):
                if not param.read_arg(arg):
                    _logger.debug("Overload failed to match, failed at %s" %
                                  param)
                    return False

        return True

    def write(self, kwargs):
        assert self._matched, \
               "write() may only be called after a succesful read()"

        for param in self.__params:
            param.write(kwargs)

# a shortcut
CompositeParam = CompositeParameter

