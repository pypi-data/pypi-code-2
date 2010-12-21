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


"""Integration tests for m4us.backplane."""


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
from ... import backplanes
## pylint: enable=E0611
from ...core.tests.integration import common


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def test_with_backplane_outstide_pipelines():
    backplane = backplanes.Backplane()
    publisher_1 = core.Pipeline(
      common.counter(5),
      common.doubler(),
      backplanes.Publisher(),
    )
    source_2 = common.counter(5)
    publisher_2 = backplanes.Publisher()
    subscriber_1 = common.Accumulator()
    subscriber_2 = common.Accumulator()
    post_office = core.PostOffice()
    all_links = [
      publisher_1.links,
      core.easy_link(publisher_1, backplane),
      core.easy_link(source_2, publisher_2, backplane),
      core.easy_link(backplane, subscriber_1),
      core.easy_link(backplane, subscriber_2),
    ]
    for links in all_links:
        post_office.link(*links)
    scheduler = core.Scheduler(post_office)
    scheduler.add(backplane, source_2, publisher_2, subscriber_1, subscriber_2,
      *publisher_1.coroutines)
    scheduler.run()
    tools.assert_equal([0, 0, 1, 2, 2, 3, 4, 4, 6, 8],
      sorted(subscriber_1.results_list))
    tools.assert_equal(subscriber_1.results_list, subscriber_2.results_list)


def test_with_backplane_inside_pipelines():
    post_office = core.PostOffice()
    scheduler = core.Scheduler(post_office, add_ignores_duplicates=True)
    backplane = backplanes.Backplane()
    publisher_1 = core.Pipeline(
      common.counter(5),
      common.doubler(),
      backplanes.publish_to(backplane),
    )
    post_office.link(*publisher_1.links)
    scheduler.add(*publisher_1.coroutines)
    publisher_2 = core.Pipeline(
      common.counter(5),
      backplanes.Publisher(),
      backplane,
      core.null_sink(),
    )
    post_office.link(*publisher_2.links)
    scheduler.add(*publisher_2.coroutines)
    sink_1 = common.Accumulator()
    subscriber_1 = core.Pipeline(
      backplane,
      sink_1,
    )
    post_office.link(*subscriber_1.links)
    scheduler.add(*subscriber_1.coroutines)
    sink_2 = common.Accumulator()
    subscriber_2 = core.Pipeline(
      backplane,
      sink_2,
    )
    post_office.link(*subscriber_2.links)
    scheduler.add(*subscriber_2.coroutines)
    scheduler.run()
    tools.assert_equal([0, 0, 2, 1, 4, 2, 6, 3, 8, 4], sink_1.results_list)
    tools.assert_equal(sink_1.results_list, sink_2.results_list)


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
