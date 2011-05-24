import logging

from logging import handlers
used_logger = None

      
    
class GeneralLogger(object):
    
    LOGGING_MAP = {'critical': logging.CRITICAL,
                   'debug': logging.DEBUG,
                   'info': logging.INFO,
                   'warning': logging.WARNING,     
                   }
    LOGGING_DEFAULT_LEVEL = {
                             'file': logging.DEBUG,
                             'console': logging.INFO,
                             }
    DEFAULT_FILE_LOG = 'general.log'
    
    def info(self, msg):
        self.logger.info(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)
        
    def critical(self, msg):
        self.logger.critical(msg)
        
    def warning(self, msg):
        self.logger.warning(msg)

    def _get_logging_level(self, mode):
        if 'mode' in self.log and self.log['mode'][mode] in self.LOGGING_MAP:
            return self.LOGGING_MAP[self.log['mode'][mode]]
        else:
            return self.LOGGING_DEFAULT_LEVEL[mode]
        
    def _get_level_string(self, level):
        
        for (key, value) in self.LOGGING_MAP.iteritems():
            if value == level:
                return key
            
            
    def _register_handler(self, handler,  name):
        level = self._get_logging_level(name)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        return level
         
         
    def _set_file_log(self ):
        if ('mode' in self.log and 'file' in self.log['mode']) or 'mode' not in self.log:
            if 'file_name' not in self.log:
                self.log['file_name'] = self.DEFAULT_FILE_LOG
            handler = handlers.RotatingFileHandler(
                      self.log['file_name'], maxBytes=2048000, backupCount=5)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            return self._register_handler(handler, 'file'), "log_file_name=%s" % self.log['file_name']

        return None 
        
    def _set_console_log(self):
        
        if ('mode' in self.log and 'console' in self.log['mode']) or 'mode' not in self.log:
            sh = logging.StreamHandler()
            sformatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
            sh.setFormatter(sformatter)
            return self._register_handler(sh, 'console'), ""

        return None
    
    def _register_log(self, name, callable):
        logtuple = callable()
        if logtuple:
            level, logmsg = logtuple
            levelstring = self._get_level_string(level)
            self.levels[name] = {}
            self.levels[name]['level'] = levelstring
            self.levels[name]['logmsg'] = logmsg

    def _tor_set_logs(self):
        """
        You can register additional methods that set new logging methods (generally by using different handlers).
        Use self._register_log(name, callable) to do it.
        The callable should parse relevant options from self.log, add handler by using self._register_handler
        and return (used logging level, log message) or None if logging was not set. 
        """
        self._register_log('file', self._set_file_log)

        self._register_log('console', self._set_console_log)


    def _log_logs(self):

        for name, log in self.levels.iteritems():
            self.debug("Init: Logging_to_%s=ON, level=%s, %s" % (name, log['level'], log['logmsg']))
            

    def __init__(self, log, name='GeneralLogger'):

        
        self.log = log
        self.levels = {}
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._tor_set_logs()
        self._log_logs()
