
import datetime
import time
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json
from ..gearman import GearmanClient, GearmanWorker

class GearmanLogger(object):
    def __init__(self, servers):
        if isinstance(servers, GearmanClient):
            self.conn = servers
        else:
            self.conn = GearmanClient(servers)

    def write(self, event, timestamp, attributes):
        attributes = dict((k, self._encode(v)) for k, v in attributes.iteritems())
        record = json.dumps(dict(event=event, timestamp=timestamp, attributes=attributes))
        self.conn.dispatch_background_task("analytics", record)

    def _encode(self, value):
        if isinstance(value, (basestring, bool, int, long, float, list, tuple)):
            pass
        elif isinstance(value, datetime.timedelta):
            value = str(int(value.days*24*60*60 + value.seconds))
        elif isinstance(value, datetime.datetime):
            value = str(int(time.mktime(value.timetuple())))
        else:
            raise TypeError("Unsupported attribute value of type %s" % type(value))

        return value

class WorkerHooks(object):
    def start(self, job):
        pass

    def fail(self, job, exc):
        import traceback
        traceback.print_exc(exc)

    def complete(self, job, result):
        pass

class GearmanLoggerWorker(object):
    def __init__(self, logger, servers, prefix=None):
        self.worker = GearmanWorker(job_servers=servers, prefix=prefix)
        self.worker.register_function("analytics", self.analytics)
        if hasattr(logger, '__iter__'):
            self.loggers = logger
        else:
            self.loggers = [logger]

    def analytics(self, job):
        record = json.loads(job.arg)
        record = dict((str(k), v) for k, v in record.iteritems())
        for logger in self.loggers:
            logger.write(**record)

    def work(self):
        self.worker.work(hooks=WorkerHooks())
