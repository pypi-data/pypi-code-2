#!/usr/bin/env python
from __future__ import division

__version__ = "$Revision: 1.5 $"

import inspect
import logging
import logging.config
from path import path
import sys

LOGGINGRC_PATH = path("~/.loggingrc").expand()

if LOGGINGRC_PATH.exists():
    logging.config.fileConfig(LOGGINGRC_PATH)
else:
    logging.basicConfig()

class autolog(object):
    def __init__(self):
        self._name = self._get_name()
        self._logger = logging.getLogger(self._name)

    def __getitem__(self, name):
        if name.startswith("."):
            name = self._name + name

        return logging.getLogger(name)

    def __getattr__(self, name):
        """
        call the default logger for anything other than item
        subscripting
        """
        return getattr(self._logger, name)

    @staticmethod
    def _get_name(stacklevel=2):
        res = inspect.stack()[stacklevel][0].f_globals["__name__"]

        if res == "__main__":
            res = path(sys.argv[0]).namebase

        if not res:
            res = "root"

        return res

    def die(self, msg, *args, **kwargs):
        self.critical(msg, *args, **kwargs)
        sys.exit(1)
