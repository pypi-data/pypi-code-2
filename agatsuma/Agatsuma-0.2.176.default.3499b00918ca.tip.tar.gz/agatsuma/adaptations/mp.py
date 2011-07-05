import logging
import Queue
from multiprocessing import Queue as MPQueue

from agatsuma.commons.types import Singleton

"""
# Another MP idea:
#http://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python
"""

class MPLogHandler(logging.Handler):
    """
    Base class, not for direct usage, only for subclassing with singletons.
    Client code must call MPLogHandlerChild().processLog() periodically.
    """
    def __init__(self, handler):
        logging.Handler.__init__(self)
        self.queue = MPQueue()
        self.realHandler = handler
        self.__use_queue = False
        
    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self.realHandler.setFormatter(fmt)

    def _format_record(self, record):
        ei = record.exc_info
        if ei:
            self.format(record) # just to get traceback text into record.exc_text
            record.exc_info = None  # to avoid Unpickleable error
        return record

    def send(self, s):
        if self.__use_queue:
            self.queue.put(s)
        else:
            self.emit_real(s)

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        #except (KeyboardInterrupt, SystemExit): # is it needed ?
        #    raise
        except:
            self.handleError(record)

    def emit_real(self, message):
        self.realHandler.emit(message)
        
    def enable_queue(self):
        self.__use_queue = True
        
    def process_log_queue(self):
        while not self.queue.empty():
            try:
                message = self.queue.get_nowait()
                self.emit_real(message)
            except Queue.Empty:
                self.realHandler.emit("log: raised Queue.Empty")


class MPStreamHandler(MPLogHandler, Singleton):
    def __init__(self):
        MPLogHandler.__init__(self, logging.StreamHandler())
