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
_logger = logging.getLogger('pytilities.aop._advice')

from . import commands, AOPException
from inspect import isclass
from contextlib import contextmanager

class _Advice(object):

    _command_handlers = {
        commands.arguments : 
            lambda self, command: (self.args, self.kwargs),

        commands.advised_instance : 
            lambda self, command: self.advised_instance,

        commands.advised_attribute : 
            lambda self, command: (self.member_name, self.advised),

        commands.proceed : 
            lambda self, command: self._process_proceed(command),

        commands.suppress_aspect : 
            lambda self, command: self._suppress(),

        commands.return_ :
            lambda self, command: self._process_return(command)
    }

    def __init__(self, advised_instance, member_name, advised, aspect, 
                 advice_function, next_advice, suppressor):
        self.advised_instance = advised_instance
        self.member_name = member_name
        self.advised = advised
        self.aspect = aspect
        self.advice_function = advice_function
        self.next_advice = next_advice
        self.suppressor = suppressor

    def run(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.return_value = None
        generator = self.advice_function()
        try:
            command = next(generator)
            while True:
                command = generator.send(self._execute_command(command))
        except StopIteration:
            return self.return_value

    def _execute_command(self, command):
        cls = command if isclass(command) else command.__class__
        try:
            return _Advice._command_handlers[cls](self, command)
        except KeyError:
            raise AOPException('Unknown command was yielded: ' + str(command))

    def _process_proceed(self, command):
        if isclass(command):
            args = self.args
            kwargs = self.kwargs
        else:
            args = command.args
            kwargs = command.kwargs

        self.return_value = self._attempt_proceed(args, kwargs)
        return self.return_value

    def _process_return(self, command):
        if not isclass(command):
            self.return_value = command.retval
        raise StopIteration()

    def _suppress(self):
        @contextmanager
        def context_manager():
            self.suppressor.suppress(self.aspect, self.advised_instance)
            try:
                yield
            finally:
                self.suppressor.unsuppress(self.aspect, self.advised_instance)

        return context_manager()

    def _attempt_proceed(self, args, kwargs):
        if isinstance(self.next_advice, _Advice):
            return self.next_advice.run(args, kwargs)
        else:
            if self.next_advice is None:
                raise AttributeError("'" + self.advised_instance.__name__ + 
                                     "' has no attribute '" + self.member_name + 
                                     "'")
            return self.next_advice(*args, **kwargs)

