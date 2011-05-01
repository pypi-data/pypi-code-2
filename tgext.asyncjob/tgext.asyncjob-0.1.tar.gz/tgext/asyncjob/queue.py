import Queue, tg

class AsyncJobQueue(object):
    def __init__(self):
        super(AsyncJobQueue, self).__init__()
        self.queue = Queue.Queue()

    def get(self):
        return self.queue.get()

    def done(self):
        self.queue.task_done()

    def perform(self, what, args, params):
        self.queue.put({'callable':what,
                        'args':args,
                        'params':params})

def asyncjob_get():
    return tg.app_globals.asyncjob_queue.get()

def asyncjob_done():
    tg.app_globals.asyncjob_queue.done()

def asyncjob_perform(what, *args, **params):
    tg.app_globals.asyncjob_queue.perform(what, args, params)
    
