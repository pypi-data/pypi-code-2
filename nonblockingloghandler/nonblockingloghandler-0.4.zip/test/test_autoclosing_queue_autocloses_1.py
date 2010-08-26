#!/usr/bin/env python

""" Test that auto-closing queue shuts down only when expected. """

import sys
import threading
import time

sys.path = [".."] + sys.path

# When True, shows the program terminating abruptly. When False, shows improvement.
USE_STANDARD_QUEUE = False

if USE_STANDARD_QUEUE:
    from Queue import Queue
else:
    from autoclosingqueue import Queue

queue = Queue()

def consume(queue):
    while True:
        item = queue.get(timeout=1)
        print item
        if item:
            queue.task_done()
        time.sleep(1) # Don't process too quickly.

consumer_thread = threading.Thread(name="Consumer Thread", target=consume, args=(queue,))
consumer_thread.daemon = True
consumer_thread.start()

queue.put("Item 1")
queue.put("Item 2")
queue.put("Item 3")

# Finish abruptly, without waiting.

print "Main loop finished"

# Should stay around to complete the task.
