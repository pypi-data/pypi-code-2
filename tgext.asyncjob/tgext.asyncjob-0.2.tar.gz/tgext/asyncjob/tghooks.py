import logging, inspect
from queue import AsyncJobQueue
from worker import AsyncWorkerThread

log = logging.getLogger('tgext.asyncjob')

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
 
