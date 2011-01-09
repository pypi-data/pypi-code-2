from ConfigParser import ConfigParser
import logging, sys

import baker

from .config import Config

logger = logging.getLogger('yoink.app')

logging.basicConfig(level=logging.DEBUG,
                    stream=sys.stdout,
                    format='%(message)s')

@baker.command(default=True)
def update(config_file='~/.yoink.conf', preview=False):
    with Config(config_file, preview) as config:
        for feed in config.feeds():
            feed.update()

def main():
    baker.run()
