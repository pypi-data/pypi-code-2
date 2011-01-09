import ConfigParser
import datetime, logging, os

from .feed import Feed
from .util import fullpath

logger = logging.getLogger('yoink.config')

class Config(object):
    def __init__(self, config_file, preview=False):
        self.config_file = fullpath(config_file)
        self.cp = ConfigParser.ConfigParser()

        logger.info('loading config file: {0}'.format(config_file))
        self.cp.read(self.config_file)

        self.preview = preview

    def close(self):
        with open(self.config_file, 'w') as f:
            logger.info('writing config file: {0}'.format(self.config_file))
            self.cp.write(f)

    def get(self, section, option):
        return self.cp.get(section, option)

    def set(self, section, option, value):
        self.cp.set(section, option, value)

    def has_section(self, section):
        return self.cp.has_section(section)

    def feeds(self):
        for section in self.cp.sections():
            if section.startswith('feed:'):
                yield FeedProxy(self, section)

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        if t is None:
            self.close()

class FeedProxy(object):
    def __init__(self,
                 config,
                 section):
        assert config.has_section(section)

        self.config = config
        self.section = section

    def __get_timestamp(self):
        try:
            timestamp = self.config.get(self.section, 'timestamp')
            timestamp = datetime.datetime.strptime(
                self.config.get(self.section, 'timestamp'),
                Feed.TIME_FORMAT)

            if timestamp.year < 1900:
                timestamp = datetime.datetime(1900, 1, 1)

        except ConfigParser.NoOptionError:
            timestamp = datetime.datetime(1900, 1, 1)
            
        return timestamp

    def __set_timestamp(self, timestamp):
        self.config.set(
            self.section,
            'timestamp',
            timestamp.strftime(Feed.TIME_FORMAT))

    url = property(lambda self: self.config.get(self.section, 'url'),
                   lambda self, val: self.config.set(self.section, 'url', val))
    folder = property(lambda self: self.config.get(self.section, 'folder'),
                      lambda self, val: self.config.set(self.section, 'folder', val))
    timestamp = property(__get_timestamp,
                         __set_timestamp)

    def update(self):
        feed = Feed(
            url=self.url,
            folder=fullpath(os.path.join(self.config.get('config', 'folder'), self.folder)),
            timestamp=self.timestamp,
            config=self.config)

        feed.update()

        self.timestamp = feed.timestamp
        
