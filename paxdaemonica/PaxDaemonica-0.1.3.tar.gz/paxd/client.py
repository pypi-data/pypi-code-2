from redis import Redis
from functools import wraps
from paxd.app.msg import PRequest

redis = Redis()

class task(object):
    def __init__(self, queue):
        self.queue = queue
    
    def __call__(self, fun):
        @wraps(fun)
        def delay(*args, **kwargs):
            if 'paxd_timeout' in kwargs:
                paxd_timeout = kwargs['paxd_timeout']
                del kwargs['paxd_timeout']
            else:
                paxd_timeout = None
            return PRequest(redis, self.queue, args=args, kwds=kwargs, timeout=paxd_timeout).send()
        fun.delay = delay
        fun.paxd_task = True
        fun.paxd_queue = self.queue
        return fun