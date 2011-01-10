import ConfigParser
import datetime, logging, os

from .feed import Feed
from .util import fullpath

logger = logging.getLogger('yoink.config')

def _make_feed(config, section):
    '''Construct a Feed object from the data in a feed: section of the
    config.
    '''
    assert section.startswith('feed:')

    # If the timestamp is not stored in the config file, then We
    # construct the earliest timestamp that datetime.datetime.strftime
    # will work with (for some reason it doesn't like years before
    # 1900.)
    try:
        timestamp = config.get(section, 'timestamp')
        timestamp = datetime.datetime.strptime(
            config.get(section, 'timestamp'),
            Feed.TIME_FORMAT)
        
        if timestamp.year < 1900:
            timestamp = datetime.datetime(1900, 1, 1)
            
    except ConfigParser.NoOptionError:
        timestamp = datetime.datetime(1900, 1, 1)

    return Feed(
        url=config.get(section, 'url'),
        folder=fullpath(
            os.path.join(
                config.get('config', 'folder'),
                config.get(section, 'folder'))),
        timestamp=timestamp,
        config=config)

class Config(object):
    '''Represents set of feeds to read and the parameters used to
    manage their reading.

    Args:
      * config_file: The file containing the config information.
      * preview: Whether operations should be performed in "preview"
          mode (i.e. nothing is actually done.)
    '''

    def __init__(self, config_file, preview=False):
        self.config_file = fullpath(config_file)
        self.cp = ConfigParser.ConfigParser()

        logger.info('loading config file: {0}'.format(config_file))
        self.cp.read(self.config_file)

        self.preview = preview

        # Make one Feed instance for each feed: section
        self.feeds = dict([(section, _make_feed(self, section)) for section in self.cp.sections() if section.startswith('feed:')])

    def close(self):
        '''Update the stored timestamps for each feed and then write
        out the configuration.

        This is called by __exit__ when no exception is thrown, so you
        can use Config naturally in a with clause.
        '''
        for section, feed in self.feeds.items():
            self.cp.set(section, 'timestamp', 
                        feed.timestamp.strftime(Feed.TIME_FORMAT))

        # Save the config.
        with open(self.config_file, 'w') as f:
            logger.info('writing config file: {0}'.format(self.config_file))
            self.cp.write(f)

    def get(self, section, option):
        return self.cp.get(section, option)

    def set(self, section, option, value):
        self.cp.set(section, option, value)

    def has_section(self, section):
        return self.cp.has_section(section)

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        if t is None:
            self.close()
