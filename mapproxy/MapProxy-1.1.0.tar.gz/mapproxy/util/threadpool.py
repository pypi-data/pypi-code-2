import sys
import Queue
import threading

class ThreadPoolWorker(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                self.task_queue.task_done()
                break
            exec_id, result_queue, base_config, func, args = task
            try:
                # with local_base_config(base_config):
                    result = func(args)
            except Exception:
                result = sys.exc_info()
            result_queue.put((exec_id, result))
            self.task_queue.task_done()

import time
from weakref import WeakSet

class ThreadPool(object):
    def __init__(self, initial_size=20):
        self._initial_size = initial_size
        self._current_jobs = 0
        self._running_workers = 0
        self._workers = WeakSet()
        self._worker_queue = Queue.Queue()
        self._worker_lock = threading.Lock()
        self._initialize()
    def _initialize(self):
        with self._worker_lock:
            for i in xrange(self._initial_size):
                self._add_worker()
                self._running_workers += 1
    
    def _add_worker(self):
        t = ThreadPoolWorker(self._worker_queue)
        t.daemon = True
        t.start()
        self._workers.add(t)
    
    def _adjust_worker_pool_size(self, add_n):
        with self._worker_lock:
            self._current_jobs += add_n
            current_workers = self._running_workers
            required_workers = max(self._initial_size, self._current_jobs)
            if current_workers > required_workers:
                for _ in xrange(current_workers - required_workers):
                    self._running_workers -= 1
                    self._worker_queue.put(None)
            elif current_workers < required_workers:
                for _ in xrange(required_workers - current_workers):
                    self._running_workers += 1
                    self._add_worker()
        
    def stop(self):
        for _ in xrange(self._running_workers):
            self._worker_queue.put(None)
        time.sleep(0.01)
        while True:
            try:
                t = self._workers.pop()
                t.join()
            except KeyError:
                break
    
    def map(self, func, args):
        return self.map_each([(func, arg) for arg in args])
        
    def map_each(self, func_args):
        """
        args should be a list of function arg tuples.
        map_each calls each function with the given arg.
        """
        jobs = len(func_args)
        self._adjust_worker_pool_size(jobs)
        result_queue = Queue.Queue()
        base_config = None #deepcopy(mapproxy.config.base_config())
        for i, (func, arg) in enumerate(func_args):
            self._worker_queue.put((i, result_queue, base_config, func, arg))
        result = self._get_results(result_queue, jobs)
        self._adjust_worker_pool_size(-jobs)
        result.sort()
        return [value for _, value in result]
    
    def _get_results(self, result_queue, results):
        result = []
        for _ in xrange(results):
            task_result = result_queue.get()
            if isinstance(task_result[1], tuple) and \
               isinstance(task_result[1][1], Exception):
                exc_class, exc, tb = task_result[1]
                raise exc_class, exc, tb
                # TODO
            result.append(task_result)
        return result

