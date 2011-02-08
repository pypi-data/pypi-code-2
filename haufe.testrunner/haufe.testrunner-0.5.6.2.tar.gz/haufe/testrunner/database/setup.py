##########################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
##########################################################################


import os
from config import WRAPPER_NAME
from model import getModel

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url


def setup(dsn=None, echo=False):

    dsn = os.environ.get('TESTING_DSN', dsn)
    if not dsn:
        raise ValueError('$TESTING_DSN undefined or the [default]/dsn option of your '
                         'configuration file is not configured properly.')

    engine = create_engine(dsn)
    engine.url = make_url(dsn)
    return engine
