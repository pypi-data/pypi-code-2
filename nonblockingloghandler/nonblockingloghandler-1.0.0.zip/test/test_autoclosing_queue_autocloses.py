#!/usr/bin/env python

""" Test that auto-closing queue shuts down only when expected. """

import sys
import threading
import time


# When True, shows the program terminating abruptly. When False, shows improvement with autoclosing queue.
USE_STANDARD_QUEUE = False

if USE_STANDARD_QUEUE:
    from Queue import Queue
else:
    from autoclosingqueue import Queue

def main():
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

    queue.put("Test running: 1 of 3.")
    queue.put("Test running: 2 of 3.")
    queue.put("Test running: 3 of 3.")
    queue.put("Test passed")

    # Finish main thread abruptly, without waiting for the consumer.
    # Application should still hang around to complete the task.

# Note: main() has to be last thing called in the process.

if __name__ == "__main__":
    main()
