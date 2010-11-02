import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('bookreader').addHandler(NullHandler())

import bookreader.settings
import bookreader.signals
