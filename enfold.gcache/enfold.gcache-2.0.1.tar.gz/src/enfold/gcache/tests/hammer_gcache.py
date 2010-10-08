# Adapted from http://www.python.org/sf/775414
import sys, os, random, bsddb, thread, tempfile, shutil, time

#sys.path.insert(0, os.path.abspath('../..'))

import logging
from enfold.gcache.cache import Cache
from enfold.gcache.diskstorage import DiskStorage

dirname = None
cache = None
running = True


logger = logging.getLogger('gcache')

hdlr = logging.StreamHandler()
fmt = logging.Formatter("%(levelname)s:%(thread)s:%(message)s")
hdlr.setFormatter(fmt)
logger.addHandler(hdlr)
logger.setLevel(logging.WARN)


class FailingShelve:
    def __init__(self, sh):
        self.sh = sh

    def __getattr__(self, attr):
        return getattr(self.sh, attr)

    def __getitem__(self, key):
        return self.sh.__getitem__(key)

    def __setitem__(self, key, value):
        self.sh.__setitem__(key, value)

    def __delitem__(self, key):
        del self.sh[key]

class FailingStorage(DiskStorage):
    def _open_index(self, index):
        import shelve
        sh = shelve.open(index, "c")
        return FailingShelve(sh)

def setUp(fail):
    global dirname, cache
    dirname = "gcache_stress"
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    if fail:
        Storage = FailingStorage
    else:
        Storage = DiskStorage
    cache = Cache(storage = Storage(dirname, logger=logger),
                  logger=logger,
                  max_len = 1000,
                  max_transient_len = 1100,
                 )
    print "Cache is at", os.path.abspath(dirname)

def tearDown():
    cache.close()
    shutil.rmtree(dirname)

def hammer(db):
    for i in xrange(1000000):
        if not running:
            break
        rnd = random.random()
        if rnd < 0.33:
            # Add/update a value.
            value = "This is a test"[:int(random.random() * 10)]
            db.set(str(int(random.random() * 5000)), (None, value))
        elif rnd < 0.66:
            # Read a value.
            try:
                x = db[str(int(random.random() * 5000))]
            except KeyError:
                pass
        else:
            # Delete a value
            try:
                del db[str(int(random.random() * 100000))]
            except KeyError:
                pass
        if (i+1) % 50000 == 0:
            print i+1
    print "Hammer stopping at", i

def maintain(cache):
    while running:
        if cache.should_maintain():
            cache.maintain()
        cache.flush()
        time.sleep(0.1)

def main():
    """This program should run for a very long time.  Every 50000 iterations
it will print the number of iterations each thread has done.  This may
take many minutes to reach 50000, so be patient.  Each number should
print 5 times."""

    print main.__doc__
    setUp(fail=False)
    try:
        for dummy in range(4):
            #t = threading.Thread(target=hammer, args=(db
            thread.start_new_thread(hammer, (cache,))
        thread.start_new_thread(maintain, (cache,))
        hammer(cache)
    finally:
        print "Done"

if __name__ == '__main__':
    main()
