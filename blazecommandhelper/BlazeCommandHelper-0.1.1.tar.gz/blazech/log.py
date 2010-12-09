import sys
import logging
import logging.handlers
from blazeutils.log import clear_handlers_by_attr
from exceptions import ConfigError

MINIMAL = (logging.INFO+logging.WARN)/2
VDEBUG = logging.DEBUG - 1
HANDLER_TAG = '__from_blazech__'

SETTINGS_MAP = {
    'minimal': MINIMAL,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'vdebug': VDEBUG
}

VERBOSITY_FLAG_MAP = (
    'minimal',
    'info',
    'debug',
    'vdebug',
)

CONSOLE_STREAM = None

class Logger(logging.Logger):

    def minimal(self, msg, *args, **kwargs):
        return self.log(MINIMAL, msg, *args, **kwargs)

    def vdebug(self, msg, *args, **kwargs):
        return self.log(VDEBUG, msg, *args, **kwargs)

logging.setLoggerClass(Logger)
logging.addLevelName(MINIMAL, 'MINIMAL')
logging.addLevelName(VDEBUG, 'VDEBUG')

def setup_logging(settings):
    # clear any previously setup handlers
    clear_handlers()

    # have to set the root logger lower than WARN (the default) or our
    # many of our logs will never be seen
    logging.root.setLevel(VDEBUG)

    class InfoOnly(logging.Filter):
        def filter(self, record):
             return record.levelno <= MINIMAL

    format_str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    if settings.logging.errorlog.path:
        formatter = logging.Formatter(format_str)

        error_handler = logging.handlers.RotatingFileHandler(
              settings.logging.errorlog.path,
              maxBytes=settings.logging.rotation.max_bytes,
              backupCount=settings.logging.rotation.backup_count,
        )
        setattr(error_handler, HANDLER_TAG, True)
        error_handler.setLevel(logging.WARN)
        error_handler.setFormatter(formatter)
        logging.root.addHandler(error_handler)

    mlverb = settings.logging.mainlog.verbosity
    if mlverb != 'none':
        log_verbosity = SETTINGS_MAP.get(mlverb, None)
        if log_verbosity is None:
            raise ConfigError('unrecognized value for logging.mainlog.verbosity: %s' % mlverb)

    if settings.logging.mainlog.path:
        formatter = logging.Formatter(format_str)

        ml_handler = logging.handlers.RotatingFileHandler(
              settings.logging.mainlog.path,
              maxBytes=settings.logging.rotation.max_bytes,
              backupCount=settings.logging.rotation.backup_count,
        )
        setattr(ml_handler, HANDLER_TAG, True)
        ml_handler.setLevel(log_verbosity)
        ml_handler.setFormatter(formatter)
        ml_handler.addFilter(InfoOnly())
        logging.root.addHandler(ml_handler)

    converb = settings.console.verbosity
    if converb != 'none':
        console_verbosity = SETTINGS_MAP.get(converb, None)
        if console_verbosity is None:
            raise ConfigError('unrecognized value for console.verbosity: %s', mlverb)

        formatter = logging.Formatter("%(message)s")
        con_handler = logging.StreamHandler(CONSOLE_STREAM or sys.stdout)
        setattr(con_handler, HANDLER_TAG, True)
        con_handler.setLevel(console_verbosity)
        con_handler.setFormatter(formatter)
        if not settings.console.inc_errors:
            con_handler.addFilter(InfoOnly())
        logging.root.addHandler(con_handler)

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    setattr(NullHandler, HANDLER_TAG, True)
    logging.root.addHandler(NullHandler())

def clear_handlers():
    clear_handlers_by_attr(HANDLER_TAG)
