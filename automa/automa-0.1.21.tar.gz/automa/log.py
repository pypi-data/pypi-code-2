#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2010-2011 Marco Pantaleoni. All rights reserved.
# Marco Pantaleoni <marco.pantaleoni@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2010-2011 Marco Pantaleoni"
__license__   = "GPL v2"

from automa.tasks import TaskContext, get_active_context

def debug(*args, **kwargs):
    ctxt = TaskContext.Active()
    if ctxt:
        return ctxt.debug(*args, **kwargs)
    return None
def info(*args, **kwargs):
    ctxt = TaskContext.Active()
    if ctxt:
        return ctxt.info(*args, **kwargs)
    return None
def notify(*args, **kwargs):
    ctxt = TaskContext.Active()
    if ctxt:
        return ctxt.notify(*args, **kwargs)
    return None
def warn(*args, **kwargs):
    ctxt = TaskContext.Active()
    if ctxt:
        return ctxt.warn(*args, **kwargs)
    return None
def error(*args, **kwargs):
    ctxt = TaskContext.Active()
    if ctxt:
        return ctxt.error(*args, **kwargs)
    import cmdutils, sys
    logger = cmdutils.log.Logger([(cmdutils.log.Logger.NOTIFY, sys.stderr)])
    logger.error("ERROR: " + args[0], color='bold red')
    sys.exit(1)
    return None
def fatal(*args, **kwargs):
    ctxt = TaskContext.Active()
    if ctxt:
        return ctxt.fatal(*args, **kwargs)
    import cmdutils, sys
    logger = cmdutils.log.Logger([(cmdutils.log.Logger.NOTIFY, sys.stderr)])
    logger.error("\n\nFATAL: " + args[0] + '\n\n', color='bold red_bg')
    sys.exit(1)
    return None
