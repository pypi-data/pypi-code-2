from ConfigParser import SafeConfigParser as SCP
import logging
import os
import re

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.clip2zeus')

try:
    os.makedirs(CONFIG_DIR)
except:
    pass # directory already exists

CONFIG_FILE = os.path.join(CONFIG_DIR, 'clip2zeus.conf')

class Clip2ZeusConfig(object):

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.parser = SCP()
        self.parser.read([self.conf_file])

    def get(self, section, option, default=None):
        """Allows default values to be returned if necessary"""

        if self.parser.has_section(section) and self.parser.has_option(section, option):
            return self.parser.get(section, option)
        else:
            return default

    def getint(self, section, option, default=''):
        """Returns an integer"""

        return int(self.get(section, option, default))

    def getfloat(self, section, option, default=''):
        """Returns a float"""

        return float(self.get(section, option, default))

    def getboolean(self, section, option, default=''):
        """Returns a boolean"""

        return bool(self.get(section, option, default))

    def set(self, section, option, value):
        """Sets some configuration value and persists to disk"""

        if not self.parser.has_section(section):
            self.parser.add_section(section)

        self.parser.set(section, option, str(value))
        self.parser.write(open(self.conf_file, 'w'))

config = Clip2ZeusConfig(CONFIG_FILE)

DELIM = ' \n\r<>"\''
URL_RE = re.compile('((\w+)://([^/%%%s]+)(/?[^%s]*))' % (DELIM, DELIM), re.I | re.M)
INVALID_DOMAINS = ('2ze.us', 'bit.ly', 'tinyurl.com', 'tr.im', 'is.gd')

# Interval to ensure we have a connection to 2ze.us (seconds)
HEARTBEAT_INT = config.getint('main', 'heartbeat', 30)
# Number of seconds to wait on 2ze.us before giving up
TIMEOUT_SEC = config.getint('main', 'timeout', 10)
DEFAULT_PORT = config.getint('main', 'port', 14694)

#
# Logging
#

LOG_FILE = os.path.join(CONFIG_DIR, 'clip2zeus.log')
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(levelname)-8s %(asctime)s [%(process)d]%(module)s:%(lineno)d %(message)s'

