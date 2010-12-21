##
## logger.py
## Login : <uli@pu.smp.net>
## Started on  Fri Dec 11 01:10:03 2009 Uli Fouquet
## $Id$
## 
## Copyright (C) 2009 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Logging for ODLS client.
"""
import logging
import logging.handlers
from logging.config import fileConfig

LEVELS = (logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR,
          logging.CRITICAL, logging.FATAL )

def init_logger(conf):
    """Initalize main logger.
    """
    loglevel = conf.loglevel
    if loglevel > 2:
        # NOTICE == INFO
        loglevel -= 1
    if loglevel == 6:
        # EMERGENCY == FATAL
        loglevel = 5
    loglevel = LEVELS[loglevel]

    max_size = conf.max_file_size
    logname = conf.logname
    do_syslog = conf.do_syslog

    logfile = conf.logfile
    logger = logging.getLogger(logname)
    logger.setLevel(loglevel)
    logger.propagate = False
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s")

    # Create a logfile handler (not activated)...
    logfilehandler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=max_size)
    logfilehandler.setFormatter(formatter)

    # Create a syslog handler (not activated)...
    # XXX: Unix only!
    sysloghandler = logging.handlers.SysLogHandler()
    sysloghandler.setFormatter(formatter)

    if logfile is not None:
        # activate logfilehandler...
        logger.addHandler(logfilehandler)

    if do_syslog:
        logger.addHandler(sysloghandler)

    logger.debug('Initialized logger')
    return logger

def get_component_logger(config, name):
    logname_base = config.options.logname
    component_logname = '%s.%s' % (logname_base, name)
    return logging.getLogger(component_logname)
