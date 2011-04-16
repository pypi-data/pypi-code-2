# -*- coding: utf-8 -*-

"""A generic worker manager that creates a pool of workers to handle workloads."""

import threading
from Queue import Queue

class WorkOrder(object):
    """Implement this interface to use as work orders for the Worker."""
    def execute(self):
        pass

class Worker(threading.Thread):
    def __init__(self, queue, *args, **kwargs):
        """Create the worker. It will pull WorkOrder objects from the given queue."""
        super(Worker, self).__init__(*args, **kwargs)
        self.queue = queue

    def run(self):
        while True:
            try:
                work_order = self.queue.get()
                try:
                    work_order.execute()
                finally:
                    self.queue.task_done()
            except Exception as e:
                print "ERROR: " + str(e)

class WorkPool(object):
    def __init__(self, num_threads, queue=None):
        self.queue = queue or Queue(-1)
        self.workers = list()
        for i in range(num_threads):
            worker = self.create_worker(i)
            self.workers.append(worker)
            worker.start()

    def create_worker(self, i):
        """Override this method to create workers of your own type"""
        worker = Worker(self.queue)
        worker.setName("Worker %d in WorkPool %r" % (i, self))
        worker.setDaemon(True)
        return worker

    def join(self):
        self.queue.join()

    def add(self, work_order):
        self.queue.put(work_order)

if __name__ == "__main__":
    wp = WorkPool(5)
    for w in wp.workers:
        print w
    print wp
    wp.join()
    print "Done"