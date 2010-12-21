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


"""Provides convenient access to all public core objects.

By providing this convenience in a separate module (:mod:`m4us.api`), instead
of in the package root (:mod:`m4us`), projects working under tight memory
constraints can reduce the memory footprint of this project by instead directly
importing only those modules they need.

.. seealso:: :doc:`/api/core/index` and the various core module documentation
    for details on the available objects in imported into this module.

"""


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

#---  Project imports
from . import utils

## pylint: disable=W0611
from .interfaces import (
  #---  Messages interfaces
  IMessage,
  IMessageFactory,
  IShutdown,
  IProducerFinished,
  #---  Coroutines interfaces
  ICoroutine,
  ICoroutineFactory,
  INotLazy,
  #---  Containers interfaces
  IContainer,
  IContainerFactory,
  #---  Postoffices interfaces
  IPostOffice,
  IPostOfficeFactory,
  #---  Schedulers interfaces
  IScheduler,
  ISchedulerFactory,
)
from .exceptions import (
  M4USException,
  #---  Postoffices exceptions
  LinkExistsError,
  NoLinkError,
  NotASinkError,
  #---  Schedulers exceptions
  DuplicateError,
  NeverRunError,
  NotAddedError,
  #---  Containers exceptions
  InvalidLinkError,
)
## pylint: enable=E0611
from .messages import (
  Message,
  Shutdown,
  ProducerFinished,
)
from .coroutines import (
  coroutine,
  sample_coroutine,
  null_sink,
)
from .components import (
  Component,
  SampleComponent,
)
from .containers import (
  Graphline,
  Pipeline,
)
from .postoffices import (
  PostOffice,
)
from .schedulers import (
  Scheduler,
)
from .utils import (
  easy_link,
  is_shutdown,
)
## pylint: enable=W0611


#---Globals--------------------------------------------------------------------

__all__ = []


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

## pylint: disable=W0212
__all__.extend(utils._public_object_names(globals()))
## pylint: enable=W0212


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
