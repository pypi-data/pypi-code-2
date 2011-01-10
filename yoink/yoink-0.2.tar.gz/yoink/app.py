from ConfigParser import ConfigParser
import logging, sys

import baker

from .config import Config
from .work_queue import work_queue

logger = logging.getLogger('yoink.app')

logging.basicConfig(level=logging.DEBUG,
                    stream=sys.stdout,
                    format='%(message)s')

@baker.command(default=True)
def update(config_file='~/.yoink.conf', preview=False):
    '''Update all feeds, downloading new files as available, and
    updating the config file's timestamps appropriately.
    '''
    with Config(config_file, preview) as config:
        # Queue up the feeds
        [work_queue.add_job(feed.update) for feed in config.feeds.values()]

        # Wait for everything to finish
        work_queue.wait()

def main():
    baker.run()
