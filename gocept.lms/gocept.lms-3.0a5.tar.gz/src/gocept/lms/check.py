# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.lms.filter
import gocept.lms.interfaces
import grok
import logging
import pytz
import threading
import urllib
import zc.queue.interfaces
import zope.component
import zope.event
import zope.interface
import zope.lifecycleevent

log = logging.getLogger(__name__)

URL_INTERVAL = datetime.timedelta(seconds=60*60)
CLASS_INTERVAL = datetime.timedelta(seconds=1)

class_last = {}


def check_and_process():
    # Process first, so that the mainloop's sleep comes *after* spawning new
    # threads.
    process_finished()
    check()

    # Update statistical information. 
    # XXX This could probably be componentized using events.
    thread_pool = zope.component.getUtility(gocept.lms.interfaces.IThreadPool)
    statistics = zope.component.getUtility(gocept.lms.interfaces.IStatistics)
    statistics.thread_pool = len(thread_pool.active)


def check():
    """Pull URLs from the check queue and have them checked.

    Does so as long as there are threads available.

    """
    check_queue = zope.component.getUtility(zc.queue.interfaces.IQueue,
                                            name='check')
    thread_pool = zope.component.getUtility(gocept.lms.interfaces.IThreadPool)

    if not check_queue:
        # Shortcut. Also avoids logging.
        return

    log.info('checker: pulling urls from queue (%s entries)' % len(check_queue))

    now = datetime.datetime.now(pytz.UTC)
    mindate = datetime.datetime.min.replace(tzinfo=pytz.UTC)

    reschedule = set()

    i = 1000
    while i:
        # Process at most 1000 items from the queue: otherwise rescheduling
        # etc. consume too much latency until we process the results again.
        i -= 1
        if not thread_pool.available:
            break
        if not check_queue:
            break

        url = check_queue.pull()
        handler = gocept.lms.interfaces.ISchemeHandler(url.url, None)

        if url.last_check > now - URL_INTERVAL:
            log.info('%s: ignored due to high frequency scheduling' % url.url)
            continue

        if handler is None:
            url.update_check(gocept.lms.interfaces.STATE_CANT_CHECK,
                             now, "No handler registered for URL")
            log.info('%s: ignored due to missing handler' % url.url)
            continue

        if not handler.allow(url.url):
            url.update_check(gocept.lms.interfaces.STATE_CANT_CHECK,
                             now, "Ignored due to LMS policy.")
            log.info('%s: ignored due to policy' % url.url)
            continue

        url_class = handler.classify(url.url)
        if class_last.get(url_class, mindate) > now - CLASS_INTERVAL:
            reschedule.add(url)
            continue

        log.info('%s: checking', url.url)
        class_last[url_class] = now
        thread = CheckerThread(url.url)
        thread.start()
        thread_pool.active.add(thread)

    for url in reschedule:
        check_queue.put(url)


def process_finished():
    thread_pool = zope.component.getUtility(gocept.lms.interfaces.IThreadPool)
    # Retrieve all finished threads and remove them from the active thread
    # list.
    finished = []
    for thread in list(thread_pool.active):
        if thread.isAlive():
            continue
        finished.append(thread)
        thread_pool.active.discard(thread)

    # Process all finished threads and write the status information back to
    # the URL objects.
    now = datetime.datetime.now(pytz.UTC)
    urls = zope.component.getUtility(gocept.lms.interfaces.IURLProvider)
    for thread in finished:
        url = urls.get_url(thread.url)
        log.info('%s: processing result' % url.url)
        log.info('%s: state %s -> %s' % (url.url, url.state, thread.state))
        url.update_check(thread.state, now, thread.reason)


class ThreadPool(grok.GlobalUtility):

    zope.interface.implements(gocept.lms.interfaces.IThreadPool)

    limit = 20

    def __init__(self):
        self.active = set()

    @property
    def available(self):
        remaining = self.limit - len(self.active)
        if remaining < 0:
            return 0
        return remaining


class CheckerThread(threading.Thread):

    zope.interface.implements(gocept.lms.interfaces.ICheckerThread)

    state = None
    reason = None

    def __init__(self, url):
        super(CheckerThread, self).__init__()
        self.url = url

    def run(self):
        type, remain = urllib.splittype(self.url)
        handler = zope.component.queryUtility(
            gocept.lms.interfaces.ISchemeHandler, name=type)
        if handler is None:
            self.state = gocept.lms.interfaces.STATE_CANT_CHECK
            self.reason = 'Can not check URLs for scheme: %s' % type
            return
        self.state, self.reason = handler.check(self.url)
