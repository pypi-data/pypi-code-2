from time import time
import datetime
from logging import getLogger
from zc.async import dispatcher
from zc.async.interfaces import KEY
from Products.Five.browser import BrowserView

log = getLogger('munin.async')


def timer(fn):

    def decorator(*args, **kw):
        start = time()
        value = fn(*args, **kw)
        elapsed = time() - start
        if elapsed > 0.1:   # only log when execution took more than 100ms
            log.info('calling %s took %.3fs', fn.__name__, elapsed)
        return value
    decorator.__doc__ = fn.__doc__
    decorator.__name__ = fn.__name__
    return decorator


class Munin(BrowserView):

    @timer
    def zcasyncqueuesize(self):
        """zc.async job queue size"""
        dispatcher_object = dispatcher.get()
        queues = dispatcher_object.conn.root().get(KEY)
        if queues is None:
            return 0
        total = sum(len(queue) for queue in queues.values())
        return 'queuesize:%.1f' % total

    @timer
    def zcasyncjobstatistics(self):
        """zc.async statistics"""
        result = []
        now = datetime.datetime.utcnow()
        since = now - datetime.timedelta(minutes=5)
        dispatcher_object = dispatcher.get()
        stats = dispatcher_object.getStatistics(at=now, since=since)
        result.append('started:%.1f' % stats['started'])
        result.append('successful:%.1f' % stats['successful'])
        result.append('failed:%.1f' % stats['failed'])
        result.append('unknown:%.1f' % stats['unknown'])
        return '\n'.join(result)

    @timer
    def zcasynctimestatistics(self):
        """zc.async statistics"""

        def calc_dt(job_info):
            timedelta = job_info['completed'] - job_info['started']
            dt = timedelta.seconds + timedelta.microseconds * 1e-6
            return dt

        result = []
        now = datetime.datetime.utcnow()
        since = now - datetime.timedelta(minutes=5)
        dispatcher_object = dispatcher.get()
        stats = dispatcher_object.getStatistics(at=now, since=since)

        longest_successful = stats['longest successful']
        if longest_successful:
            job_info = dispatcher_object.getJobInfo(longest_successful[0])
            result.append('longest_successful:%.3f' % calc_dt(job_info))
        else:
            result.append('longest_successful:0.0')

        shortest_successful = stats['shortest successful']
        if shortest_successful:
            job_info = dispatcher_object.getJobInfo(shortest_successful[0])
            result.append('shortest_successful:%.3f' % calc_dt(job_info))
        else:
            result.append('shortest_successful:0.0')

        longest_failed = stats['longest failed']
        if longest_failed:
            job_info = dispatcher_object.getJobInfo(longest_failed[0])
            result.append('longest_failed:%.3f' % calc_dt(job_info))
        else:
            result.append('longest_failed:0.0')

        shortest_failed = stats['shortest failed']
        if shortest_failed:
            job_info = dispatcher_object.getJobInfo(shortest_failed[0])
            result.append('shortest_failed:%.3f' % calc_dt(job_info))
        else:
            result.append('shortest_failed:0.0')

        return '\n'.join(result)
