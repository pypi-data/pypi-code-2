
import time

from scuttle.version import VERSION as __version__

class Scuttle(object):
    def __init__(self, loggers, global_attributes=None):
        self.global_attributes = global_attributes or {}
        self.loggers = loggers if isinstance(loggers, (list, tuple)) else [loggers]

    def clear_global_attributes(self):
        self.global_attributes = {}

    def set_global_attributes(self, **attributes):
        self.global_attributes.update(attributes)

    def add_logger(self, logger):
        self.loggers.append(logger)

    def record(self, event, attributes=None, timestamp=None):
        attributes = attributes or {}

        if self.global_attributes:
            attrs = self.global_attributes.copy()
            attrs.update(attributes)
        else:
            attrs = attributes
        attrs = dict((k, v) for k, v in attrs.iteritems() if v is not None)
        for log in self.loggers:
            log.write(
                event = event,
                timestamp = timestamp or time.time(),
                attributes = attrs,
            )
