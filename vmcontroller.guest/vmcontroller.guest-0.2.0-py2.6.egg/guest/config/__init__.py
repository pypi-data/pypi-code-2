"""
Configuration support functionality.
"""

try:
    import os
    import logging
    import inject

    from ConfigParser import SafeConfigParser
    from pkg_resources import resource_stream
except ImportError as e:
    print "Import Error: %s" % e
    exit()

logger = logging.getLogger(__name__)

@inject.param('config')
def init_config_file(config_file, config):
    """
    Initializes config from a specfied cfg file.
    @param config_file: Path to the config file.
    @param config: Config object.
    """
    if config_file and os.path.exists(config_file):
        read = config.read([config_file])
        if not read:
            raise ValueError("Could not read configuration from file: %s" % config_file)

def init_config():
    """
    Initializes config from the default cfg file.
    @return: The config object.
    """
    config = SafeConfigParser()
    config.readfp(resource_stream(__name__, 'default.cfg'))
    return config

def debug_config(config):
    """
    Debugs config object by printing out all the options, values pairs.
    @param config: The config object to be debugged.
    """
    for section in config.sections():
        for option in config.options(section):
            logger.debug("[%s] %s=%s" % (section, option, config.get(section, option)))
