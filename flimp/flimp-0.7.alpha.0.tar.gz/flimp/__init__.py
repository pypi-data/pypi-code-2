# -*- coding: utf-8 -*-
import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("flimp").addHandler(NullHandler())

VERSION = "0.7.alpha.0"

NAMESPACE_DESC = "%s namespace derived from %s.\n\n%s"
TAG_DESC = "%s tag derived from %s.\n\n%s"
