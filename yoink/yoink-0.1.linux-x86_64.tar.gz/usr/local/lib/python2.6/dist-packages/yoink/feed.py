import ConfigParser, datetime, logging, os, time, urllib, urlparse

import feedparser

from .util import catching

logger = logging.getLogger('yoink.feed')

class Feed(object):
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self,
                 url,
                 folder,
                 timestamp,
                 config):
        self.url = url
        self.folder = folder
        self.timestamp = timestamp
        self.config = config

    @catching(handler=lambda e: logger.error('Error processing feed: {1}'.format(e)))
    def update(self):
        def entry_sort(x, y):
            if x['updated_parsed'] < y['updated_parsed']:
                return -1
            elif x['updated_parsed'] > y['updated_parsed']:
                return 1
            else:
                return 0

        logger.info('reading feed: {0}'.format(self.url))
              
        # read the feed
        parsed = feedparser.parse(self.url)

        # grab the entries
        entries = parsed['entries']

        # filter out entries older than the feed timestamp
        filter(lambda e: e['updated_parsed'] > self.timestamp.timetuple(), 
               entries)

        # sort entries in ascending timestamp order
        entries.sort(entry_sort)

        # process each entry (in timestamp order)
        map(self.process_entry, parsed['entries'])

    @catching(exception_type=KeyError, handler=lambda e: logger.error('Entry is missing a field: {0}'.format(e)))
    def process_entry(self, entry):
        # Download the entry if it's timestamp is greater than the
        # feed's
        if entry['updated_parsed'][:8] > self.timestamp.timetuple()[:8]:
            for enc in entry['enclosures']:
                if enc['type'].startswith('audio/'):

                    if self.config.preview:
                        logger.info('[PREVIEW] Downloading {0}'.format(enc['href']))

                    else:
                        self.download(enc['href'])
                    
                        # update the feed's timestamp with the entry's
                        self.timestamp = datetime.datetime.strptime(
                            time.strftime(
                                Feed.TIME_FORMAT, 
                                entry['updated_parsed']),
                            Feed.TIME_FORMAT)

    def download(self, url):
        try:
            os.makedirs(self.folder)
        except OSError:
            pass

        filename = os.path.split(
            urlparse.urlparse(url).path)[1]

        dest = os.path.join(self.folder, filename)

        logger.info('Downloading {0} to {1}'.format(url, dest))
        try:
            urllib.urlretrieve(url, dest)

        except Exception as e:
            logger.error('Error downloading entry {0}: {1}'.format(url, e))
