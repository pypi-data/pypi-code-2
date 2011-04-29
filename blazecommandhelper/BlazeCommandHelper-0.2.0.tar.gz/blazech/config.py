from decimal import Decimal
import os
from os import path
from blazeutils.config import QuickSettings
from blazeutils.datastructures import OrderedDict
from blazeutils.helpers import tolist, csvtolist
from blazech.exceptions import ConfigError
from blazech.lib.ConfigParser import SafeConfigParser
import blazech.locations as locations

class DefaultConfig(QuickSettings):

    def __init__(self):
        QuickSettings.__init__(self)

        #######################################################################
        # LOGGING
        #######################################################################
        # the full path to the file that should contain log files
        self.logging.mainlog.path = None
        # see the logging section of the docs for a description of these levels
        self.logging.mainlog.verbosity = 'minimal'
        # the full path to the file that should contain log files
        self.logging.errorlog.path = None
        # maximum log file size is 50MB
        self.logging.rotation.max_bytes = 1024*1024*50
        # number of rotated log files to keep around
        self.logging.rotation.backup_count = 4
        # default verbosity for console
        self.console.verbosity = 'minimal'
        # include errors on console output
        self.console.inc_errors = False

def parse_config_files(include_system_configs, fpaths):
    """
        fpaths: an interable of file system paths to configuration files that
        need to be processed.  We start with the default config and add the
        configuration file settings in order.
    """
    config_paths = []
    if include_system_configs:
        if path.isfile(locations.system_config_file):
            config_paths.append(locations.system_config_file)
        if path.isfile(locations.user_config_file):
            config_paths.append(locations.user_config_file)
    config_paths.extend(tolist(fpaths))

    df = DefaultConfig()
    if config_paths:
        cp = SafeConfigParser(dict_type=OrderedDict)
        cp.read(config_paths)
        df.update(_config_obj_to_qs(cp))
    df.lock()
    return df

def _config_obj_to_qs(config):
    """
        converts a config parser object to a quick settings object
    """
    qs = QuickSettings()

    # do the defaults
    for n,v in config.defaults().iteritems():
        v = _auto_convert_str_to_numeric_type(v)
        qs.set_dotted(n, v)

    # sectin settings get attached to their sections, we assume section naming
    # will be appropriate, i.e. [bulk], [jobs.mysql5], etc.
    all_sections = config.sections()
    for section in all_sections:
        for n,v in config.items(section):
            v = _auto_convert_str_to_numeric_type(v)
            if n == '_include_':
                sec_to_update = qs.get_dotted(section)
                for incsection in csvtolist(v):
                    if incsection not in all_sections:
                        raise ConfigError('included section %s not found' % incsection)
                    qs.get_dotted(section).update(qs.get_dotted(incsection))
            else:
                qs.set_dotted('%s.%s' % (section, n), v)
    return qs

def _auto_convert_str_to_numeric_type(string):
    try:
        return int(string)
    except ValueError, e:
        if 'invalid literal for int()' not in str(e):
            raise
    try:
        return Decimal(string)
    except Exception, e:
        if 'Invalid literal for Decimal' not in str(e):
            raise
    return string
