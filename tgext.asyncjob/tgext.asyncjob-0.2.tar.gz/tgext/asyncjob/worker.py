import threading, transaction, logging
from tg import config, app_globals

log = logging.getLogger('tgext.asyncjob')

running_status = threading.local()

class AsyncWorkerThread(threading.Thread):
    def __init__(self, queue):
        super(AsyncWorkerThread, self).__init__()
        self.queue = queue

    def run(self):
        log.info('Worker thread is running.')

        while True:
            msg = self.queue.get()

            func = msg.get('callable')
            args = msg.get('args')
            params = msg.get('params')
            uid = msg.get('uid')

            if not args:
                args = []

            if not params:
                params = {}

            if func:
                transaction.begin()
                try:
                    running_status.entry = uid
                    func(*args, **params)
                    transaction.commit()
                except Exception, e:
                    log.exception('Exception in async job %s', uid)
                    transaction.abort()

            running_status.entry = None
            self.queue.done(uid)
            config.DBSession.remove()

def asyncjob_running_uid():
    return running_status.entry
    
