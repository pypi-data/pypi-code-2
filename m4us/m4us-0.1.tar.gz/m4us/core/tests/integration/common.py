# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2010 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.


"""Common testing coroutines and components m4us.core integration tests."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

#---  Third-party imports
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611

#---  Project imports
## pylint: disable=E0611
from ... import coroutines, components, messages, utils, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def _plain_counter(max_count):
    yield
    for number in xrange(max_count):
        yield 'outbox', number
    yield 'signal', messages.ProducerFinished()


def _plain_doubler():
    inbox, message = (yield)
    while True:
        if utils.is_shutdown(inbox, message):
            yield 'signal', message
            break
        inbox, message = (yield 'outbox', message * 2)


def _plain_accumulator(results_list):
    while True:
        inbox, message = (yield)
        if utils.is_shutdown(inbox, message):
            yield 'signal', message
            break
        results_list.append(message)


@coroutines.coroutine(lazy=False)
def counter(max_count):
    return _plain_counter(max_count)


@coroutines.coroutine()
def doubler():
    return _plain_doubler()


@coroutines.coroutine()
def accumulator(results_list):
    return _plain_accumulator(results_list)


#---Classes--------------------------------------------------------------------

class Counter(components.Component):

    interface.implements(interfaces.INotLazy)

    def __init__(self, max_count, **kwargs):
        components.Component.__init__(self, max_count=max_count, **kwargs)

    def _main(self):
        return _plain_counter(self.max_count)


class Doubler(components.Component):

    def _main(self):
        return _plain_doubler()


class Accumulator(components.Component):

    def __init__(self, **kwargs):
        self.results_list = []
        components.Component.__init__(self, **kwargs)

    def _main(self):
        return _plain_accumulator(self.results_list)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
