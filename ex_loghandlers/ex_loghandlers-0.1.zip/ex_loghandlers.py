import getpass
import socket
import traceback
import logging.handlers
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

class ExHTTPHandler(logging.handlers.HTTPHandler):
    """Extended HTTPHandler supports dumping trackback as string, add hostname,
    username values in record
    
    """
    
    def __init__(self, host, url, method="GET", prefix='_ex_'):
        logging.handlers.HTTPHandler.__init__(self, host, url, method)
        self.prefix = prefix

    def mapLogRecord(self, record):
        """
        Default implementation of mapping the log record into a dict
        that is sent as the CGI data. Overwrite in your class.
        Contributed by Franz  Glasner.
        """
        d = record.__dict__
        if record.exc_info is not None:
            dump = StringIO.StringIO()
            traceback.print_exception(*record.exc_info, file=dump)
            d[self.prefix + 'traceback'] = dump.getvalue()
        d[self.prefix + 'hostname'] = socket.gethostname()
        d[self.prefix + 'username'] = getpass.getuser()
        return d