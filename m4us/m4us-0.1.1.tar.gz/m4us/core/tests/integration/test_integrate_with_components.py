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


"""Integration tests for m4us.core.components."""


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
from ... import schedulers, postoffices, utils
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

#---  Test functions

def test_pipeline_pattern():
    source = common.Counter(5)
    filter_ = common.Doubler()
    sink = common.Accumulator()
    post_office = postoffices.PostOffice()
    post_office.link(*utils.easy_link(source, filter_, sink))
    scheduler = schedulers.Scheduler(post_office)
    scheduler.add(source, filter_, sink)
    scheduler.run()
    tools.assert_equal([0, 2, 4, 6, 8], sink.results_list)


def test_graphline_pattern():
    source = common.Counter(5)
    filter_ = common.Doubler()
    sink1 = common.Accumulator()
    sink2 = common.Accumulator()
    post_office = postoffices.PostOffice()
    post_office.link(
        (source, 'outbox', sink1, 'inbox'),
        (source, 'signal', sink1, 'control'),
        (source, 'outbox', filter_, 'inbox'),
        (source, 'signal', filter_, 'control'),
        (filter_, 'outbox', sink2, 'inbox'),
        (filter_, 'signal', sink2, 'control'),
    )
    scheduler = schedulers.Scheduler(post_office)
    scheduler.add(source, filter_, sink1, sink2)
    scheduler.run()
    tools.assert_equal([0, 1, 2, 3, 4], sink1.results_list)
    tools.assert_equal([0, 2, 4, 6, 8], sink2.results_list)


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
