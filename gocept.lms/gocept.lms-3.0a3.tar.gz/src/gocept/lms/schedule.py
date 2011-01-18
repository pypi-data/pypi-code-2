# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import logging
import pytz

import hurry.query
import hurry.query.interfaces
import zc.queue.interfaces
import zope.component

import gocept.lms.interfaces

log = logging.getLogger(__name__)

INTERVAL = datetime.timedelta(seconds=24*3600) # XXX make state-dependent
QUEUE_LIMIT = 1000
BACKOFF_TIME = 5*60


def schedule():
    check_queue = zope.component.getUtility(zc.queue.interfaces.IQueue,
                                            name='check')
    queue_len = len(check_queue)
    if queue_len > 1000:
        log.warn(
            'Scheduler found %s items in queue. Backing off for %s seconds'
            % (queue_len, BACKOFF_TIME))
        return BACKOFF_TIME
    url_query = zope.component.getUtility(hurry.query.interfaces.IQuery)
    reference_time = datetime.datetime.now(pytz.UTC) - INTERVAL
    urls = url_query.searchResults(
        hurry.query.Le(('urls', 'last_check'), reference_time))
    for url in urls:
        log.info('%s: scheduling' % url.url)
        check_queue.put(url)
    return
