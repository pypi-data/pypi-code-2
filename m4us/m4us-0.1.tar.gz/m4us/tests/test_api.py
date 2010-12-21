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


"""Tests for m4us.api."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import functools

#---  Third-party imports

#---  Project imports
import m4us
from ..core.tests import support
## pylint: disable=E0611
from .. import api
## pylint: enable=E0611
from ..core import api as core_api, utils


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def test_api_should_include_all_public_non_core_objects():
    for test in support.check_module_should_include_all_public_objects(api,
      m4us):
        yield test


def test_api_should_include_all_public_core_objects():
    for name, object_ in vars(core_api).items():
        ## pylint: disable=W0212
        if utils._is_private_object(name, object_):
            ## pylint: enable=W0212
            continue
        # This is done only for output asthetics.
        asserter = functools.partial(support.assert_object_name_in_module, api)
        yield asserter, 'core.api.' + name


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
