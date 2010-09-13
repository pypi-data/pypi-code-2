# -*- coding: utf-8 -*-

import logging

from issues.plugin import Plugin


class TrackerPlugin(Plugin):

    def __init__(self):
        self._log = logging.getLogger("%s.%s" % (__name__,
                                                 self.__class__.__name__))

    def load(self):
        self._log.debug("Loading")

    def sync(self, tracker):
        """Start the synchronisation process for a single tracker.

        :param tracker: Instance of :class:`System`
        """
        raise NotImplementedError

    def unload(self):
        self._log.debug("Unloading")
