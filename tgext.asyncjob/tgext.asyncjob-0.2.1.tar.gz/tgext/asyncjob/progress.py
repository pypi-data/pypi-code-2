from __future__ import with_statement

import tg, threading
from worker import asyncjob_running_uid

class AsyncProgressTracker(object):
    def __init__(self):
        super(AsyncProgressTracker, self).__init__()
        self.status_lock = threading.Lock()
        self.status = {}

    def track(self, entryid):
        with self.status_lock:
            self.status[entryid] = (-1, None)

    def remove(self, entryid):
        with self.status_lock:
            self.status.pop(entryid, None)

    def set_progress(self, entryid, value, message):
        with self.status_lock:
            self.status[entryid] = (value, message)

    def get_progress(self, entryid):
        with self.status_lock:
            return self.status.get(entryid)
asyncjobs_progress_status = AsyncProgressTracker()

def asyncjob_set_progress(value, data=None):
    entryid = asyncjob_running_uid()
    asyncjobs_progress_status.set_progress(entryid, value, data)

def asyncjob_get_progress(entryid):
    return asyncjobs_progress_status.get_progress(entryid)
