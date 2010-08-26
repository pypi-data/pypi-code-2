#!/usr/bin/env python
"""
    Provides a single location for all logging configuration.
    Used to be in a logger config file, but grew too complicated.
"""
import logging
import logging.handlers
from os.path import join
import sys

from nonblockingloghandler import NonblockingLogHandler
from singleton import singleton

@singleton
class LoggingConfiguration():
    def __init__(self):
        
        log_path = "c:\\temp"
        
        #### Formatters
        
        # A common formatter
        self.formatter = logging.Formatter("%(asctime)s-%(name)s:%(levelname)s:%(threadName)s: %(message)s")
        
        #### Handlers
        
        # The following message destinations are defined:
        #    error_email: errors are sent to email.
        #    * error_console: errors are logged to the console.
        #    * error_error_file: errors are logged to the error file
        #
        #    * all_feed_file: all messages (from the feed) are sent to the feed file.
        #    * all_bot_file: messages (from the bot) are sent to the bot file
        #    * all_price_archiver_file: messages (from the price archiver) are sent to the price-archiver file.
        #
        #    all_email: info messages (for bounce) are sent to email.
        
        all_feed_file_handler = logging.FileHandler(join(log_path, "feed.log"), delay=True)
        all_bot_file_handler = logging.FileHandler(join(log_path, "bot.log"), delay=True)
        all_price_archiver_file_handler = logging.FileHandler(join(log_path, "pricearchiver.log"), delay=True)
        for handler in (all_feed_file_handler, all_bot_file_handler, all_price_archiver_file_handler):
            handler.setLevel(logging.NOTSET)
            handler.setFormatter(self.formatter)
        
        error_error_file_handler = logging.FileHandler(join(log_path, "error.log"))
        error_error_file_handler.setLevel(logging.ERROR)
        error_error_file_handler.setFormatter(self.formatter)

        error_console_handler = logging.StreamHandler(sys.stderr)
        error_console_handler.setLevel(logging.ERROR)
        error_console_handler.setFormatter(self.formatter)
        
        error_email_handler = NonblockingLogHandler(
            logging.handlers.SMTPHandler(
                mailhost='localhost',
                fromaddr='bot@vps13516.eukhost.com',
                toaddrs=['betbot-announcements@somethinkodd.com',],
                subject='Tennis BetBot Error Notification'
                )
            )
        error_email_handler.setLevel(logging.ERROR)
        error_email_handler.setFormatter(self.formatter)

        all_email_handler = NonblockingLogHandler(
            logging.handlers.SMTPHandler(
                mailhost='localhost',
                fromaddr='bot@vps13516.eukhost.com',
                toaddrs=['betbot-announcements@somethinkodd.com','Andrew.Orbach@somethinkodd.com'],
                subject='Tennis BetBot Bounce Notification'
                )
            )
        all_email_handler.setLevel(logging.NOTSET)
        all_email_handler.setFormatter(self.formatter)
        
        #### Loggers
        
        # The following loggers are defined:
        #    root - Shouldn't be used, but is a catch all.
        #    bot - top level for betbot - only for errors and above.
        #        match - special case, one logger per thread.
        #        threadpool - thread
        #        betbot - thread
        #        runtime - thread
        #        sleep - filtered to warnings only
        #        bounce - sends emails
        #    feed - oncourt feed for betbot (and price archiver?)
        #    pricearchiver
        #    
        # TODO! Move logger name of feed.py and oncourtfeed.py

        root_logger = logging.getLogger("")
        for handler in (
            error_email_handler,
            error_console_handler,
            error_error_file_handler,
            all_bot_file_handler, # Might not be bot-related, but just to be sure low-severity messages are caught somewhere.            
            ):
            root_logger.addHandler(handler)
        
        bot_logger = logging.getLogger("bot")
        for handler in (
            error_email_handler,
            error_console_handler,
            error_error_file_handler,
            ):
            bot_logger.addHandler(handler)
        bot_logger.propagate = False
        
        # Nothing required here for match_logger.
        
        feed_logger = logging.getLogger("scorefeed")
        feed_logger.addHandler(all_feed_file_handler)

        thread_logger = logging.getLogger("bot.threadpool")
        thread_logger.addHandler(all_bot_file_handler)

        betbot_logger = logging.getLogger("bot.betbot")
        betbot_logger.addHandler(all_bot_file_handler)

        runtime_logger = logging.getLogger("bot.runtime")
        runtime_logger.addHandler(all_bot_file_handler)
        
        sleep_logger = logging.getLogger("bot.betbot.SleepUntil")
        sleep_logger.setLevel(logging.WARNING)
        
        bounce_logger = logging.getLogger("bot.betbot.SleepUntil")
        bounce_logger.addHandler(all_email_handler)

        price_archiver_logger = logging.getLogger("pricearchiver")
        price_archiver_logger.propagate = False
        price_archiver_logger.setLevel(logging.INFO)
        price_archiver_logger.addHandler(all_price_archiver_file_handler)
        price_archiver_logger.addHandler(error_email_handler)
        price_archiver_logger.addHandler(error_error_file_handler)
        price_archiver_logger.addHandler(error_console_handler)
    
    def session_logger(self, session_name, base_logger_name):
        """ Create a session-specific logger, when a module-based-solution is inadequate """
        filename_friendly_name = session_name.replace(" ","_").replace("(","").replace(")","") # No spaces, parenthesis = easier command lines.
        filename = os.path.join("c:\\temp", filename_friendly_name)
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        logger_name = base_logger_name + "." + filename_friendly_name
        logger = logging.getLogger(logger_name)
        if not logger.handlers:
            # May have already been added, in generic case.
            handler = logging.FileHandler(filename)
            logger.addHandler(handler)
            handler.setFormatter(self.self.formatter)

        return logger
        
if __name__ == "__main__":
    LoggingConfiguration()