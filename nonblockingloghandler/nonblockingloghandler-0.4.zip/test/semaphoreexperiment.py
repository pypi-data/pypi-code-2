#!/usr/bin/env python


"""
ConsumerThread:
. . while (true)
. . . . process(queue.pop())
. . . . protector.task_done


Protector:
    protected_put(queue, item)
    . . lock (locker)
    . . . . protector.protect
    . . . . queue.Put(item)


    Protect:
        LOCK(lock)
            outstanding_message_count += 1
            if outstanding_message_count == 1
                ProtectorThread.start
        queue.push

    Task_done:
        semaphore.release

    ProtectorThread function:
        finished = False
        while not finished
            semaphore.acquire
            LOCK(lock):
                outstanding_message_count -= 1
                finished = outstanding_message_count == 0

LogFunction:
    Protector.Put


"""

import threading

semaphore = threading.Semaphore(0)

semaphore.release()
semaphore.release()
semaphore.release()
print "Acquiring"
semaphore.acquire()
print "Acquiring"
semaphore.acquire()
print "Acquiring"
semaphore.acquire()
print "Acquiring"
semaphore.acquire()
