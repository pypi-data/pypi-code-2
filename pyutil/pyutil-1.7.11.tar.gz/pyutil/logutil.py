# This little file makes it so that we can use "log.msg()" and the contents
# get logged to the Twisted logger if present, else to the Python Standard
# Library logger.

try:
    from twisted.python import log
    log # http://divmod.org/trac/ticket/1499
except ImportError:
    import logging
    class MinimalLogger:
        def msg(self, m):
            logging.log(0, m)
    log = MinimalLogger()

