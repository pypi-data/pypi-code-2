##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Leonardo Rochael Almeida <leonardo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import sys
from logging import getLogger
from Products.LongRequestLogger.monitor import Monitor

log = getLogger(__name__)

def wrapper(*args, **kw):
    m = Monitor()
    try:
        result = wrapper.original(*args, **kw)
        return result
    finally:
        m.stop()

def do_patch():
    from ZPublisher.Publish import publish_module_standard as original
    wrapper.original = original
    log.info('patching %s.%s' % (wrapper.original.__module__, 
                                 wrapper.original.__name__))
    setattr(sys.modules[wrapper.original.__module__],
            wrapper.original.__name__,
            wrapper)

def do_unpatch():
    setattr(sys.modules[wrapper.original.__module__],
            wrapper.original.__name__,
            wrapper.original)
