# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""General utility functions."""

from djangode.utils.config import get_config_value, set_config_value
from djangode.utils.runner import Runner, RunnerError, RunnerStopped
from djangode.utils.set_proxy import set_proxy


# Make the logging module display useful error messages.
import logging
import traceback

def handleError(self, record):
    traceback.print_stack()
logging.Handler.handleError = handleError

del logging
