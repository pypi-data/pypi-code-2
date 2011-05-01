import threading, transaction, logging, inspect
from tg import config, app_globals
from queue import AsyncJobQueue

log = logging.getLogger('tgext.asyncjob')

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

            if func and args is not None and params is not None:
                transaction.begin()
                try:
                    func(*args, **params)
                    transaction.commit()
                except Exception, e:
                    log.exception('Exception in async job')
                    transaction.abort()

            self.queue.done()
            config.DBSession.remove()

def start_async_worker(app_globals=None):
    if not app_globals:
        try:
            app_globals = inspect.currentframe().f_back.f_locals['self']
            log.info('App globals autodetected: %s', app_globals)
        except:
            log.error('Failed app globals autodetection, explicitly pass it to start_async_worker')
            return

    app_globals.asyncjob_queue = AsyncJobQueue()
    worker = AsyncWorkerThread(app_globals.asyncjob_queue)
    worker.start()
    
