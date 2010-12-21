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


"""Integration tests for m4us.core.containers."""


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
from . import common
## pylint: disable=E0611
from ... import containers, postoffices, schedulers, utils
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def test_graphline_with_source_and_sink_inside():
    source = common.counter(5)
    filter_ = common.doubler()
    sink1 = common.Accumulator()
    sink2 = common.Accumulator()
    graphline = containers.Graphline(
      (source, 'outbox', sink1, 'inbox'),
      (source, 'signal', sink1, 'control'),
      (source, 'outbox', filter_, 'inbox'),
      (source, 'signal', filter_, 'control'),
      (filter_, 'outbox', sink2, 'inbox'),
      (filter_, 'signal', sink2, 'control'),
      (sink2, 'signal', 'self', 'signal'),
    )
    post_office = postoffices.PostOffice()
    post_office.link(*graphline.links)
    scheduler = schedulers.Scheduler(post_office)
    scheduler.add(*graphline.coroutines)
    scheduler.run()
    tools.assert_equal([0, 1, 2, 3, 4], sink1.results_list)
    tools.assert_equal([0, 2, 4, 6, 8], sink2.results_list)


def test_graphline_with_source_and_sink_outside():
    source = common.counter(5)
    filter1 = common.doubler()
    filter2 = common.doubler()
    filter3 = common.doubler()
    sink = common.Accumulator()
    graphline = containers.Graphline(
      ('self', 'inbox', filter1, 'inbox'),
      ('self', 'control', filter1, 'control'),
      ('self', 'inbox', filter2, 'inbox'),
      ('self', 'control', filter2, 'control'),
      (filter2, 'outbox', filter3, 'inbox'),
      (filter2, 'signal', filter3, 'control'),
      (filter1, 'outbox', 'self', 'outbox'),
      (filter1, 'signal', 'self', 'signal'),
      (filter3, 'outbox', 'self', 'outbox'),
      (filter3, 'signal', 'self', 'signal'),
    )
    post_office = postoffices.PostOffice()
    post_office.link(*graphline.links)
    post_office.link(*utils.easy_link(source, graphline, sink))
    scheduler = schedulers.Scheduler(post_office)
    scheduler.add(source, sink, *graphline.coroutines)
    scheduler.run()
    tools.assert_equal([0, 0, 2, 4, 4, 8, 6, 12, 8, 16], sink.results_list)


def test_pipeline_with_source_and_sink_outside():
    source = common.counter(5)
    filter1 = common.doubler()
    filter2 = common.doubler()
    sink = common.Accumulator()
    pipeline = containers.Pipeline(filter1, filter2)
    post_office = postoffices.PostOffice()
    post_office.link(*pipeline.links)
    post_office.link(*utils.easy_link(source, pipeline, sink))
    scheduler = schedulers.Scheduler(post_office)
    scheduler.add(source, sink, *pipeline.coroutines)
    scheduler.run()
    tools.assert_equal([0, 4, 8, 12, 16], sink.results_list)


def test_pipeline_with_source_and_sink_inside():
    sink = common.Accumulator()
    pipeline = containers.Pipeline(
      common.counter(5),
      common.doubler(),
      sink,
    )
    post_office = postoffices.PostOffice()
    post_office.link(*pipeline.links)
    scheduler = schedulers.Scheduler(post_office)
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
