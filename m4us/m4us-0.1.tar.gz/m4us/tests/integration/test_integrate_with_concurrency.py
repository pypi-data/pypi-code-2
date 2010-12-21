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


"""Integration tests for m4us.concurrency."""


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
from nose import tools

#---  Project imports
from ...core import api as core
## pylint: disable=E0611
from ... import concurrency
## pylint: enable=E0611
from ...core.tests.integration import common


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def test_with_coroutines():
    results_list = []
    pipeline = core.Pipeline(
      concurrency.ThreadedCoroutine(common.counter(5)),
      concurrency.ThreadedCoroutine(common.doubler()),
      concurrency.ThreadedCoroutine(common.accumulator(results_list)),
    )
    post_office = core.PostOffice()
    post_office.link(*pipeline.links)
    scheduler = core.Scheduler(post_office)
    scheduler.add(*pipeline.coroutines)
    scheduler.run()
    tools.assert_equal([0, 2, 4, 6, 8], results_list)


def test_with_components():
    sink = common.Accumulator()
    pipeline = core.Pipeline(
      concurrency.ThreadedCoroutine(common.Counter(5)),
      concurrency.ThreadedCoroutine(common.Doubler()),
      concurrency.ThreadedCoroutine(sink),
    )
    post_office = core.PostOffice()
    post_office.link(*pipeline.links)
    scheduler = core.Scheduler(post_office)
    scheduler.add(*pipeline.coroutines)
    scheduler.run()
    tools.assert_equal([0, 2, 4, 6, 8], sink.results_list)


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
