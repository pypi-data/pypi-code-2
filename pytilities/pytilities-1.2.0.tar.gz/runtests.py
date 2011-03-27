#
# Runs all unit tests
#

import logging
from project import run_tests

# Set up logging
# Note that this has to happen before we import stuff (as things may already go
# wrong by importing things)
logger = logging.getLogger("pytilities")
handler = logging.StreamHandler()  # defaults to stderr
logger.addHandler(handler)

# Uncomment to see log output
logging.getLogger("pytilities.testing").setLevel(logging.DEBUG)
#logging.getLogger("pytilities.aop").setLevel(logging.DEBUG)

if __name__ == '__main__':
    run_tests('pytilities.test')
