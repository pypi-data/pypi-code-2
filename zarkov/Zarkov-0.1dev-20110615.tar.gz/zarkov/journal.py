import os
import sys
import time
import bson
import struct
import logging
from datetime import datetime
from hashlib import sha1

import gevent

from zarkov import model

log = logging.getLogger(__name__)

class JournalWriter(object):
    MAX_FILES = 3
    # MAX_SIZE = 1*2**25
    MAX_SIZE = 1*2**20
    RETRY_DELAY=10

    def __init__(self, journal_dir, replay=True):
        self._in_replay = False
        self._needs_replay = replay
        self._mongo_retry = time.time()
        self._journal_dir = journal_dir
        if replay: gevent.spawn(self.replay)
        self._fp = None
        self._bytes_written = 0
        self.open_writer()

    def __call__(self, obj):
        self._bytes_written  += self._write(obj)
        if self._bytes_written > self.MAX_SIZE:
            self.open_writer()
        if self._mongo_retry <= time.time():
            self._try_save(obj)

    def _try_save(self, obj):
        try:
            if self._in_replay:
                model.doc_session.db.event.save(obj, safe=False)
            else:
                model.doc_session.db.event.insert(obj, safe=False)
            if self._needs_replay:
                gevent.spawn(self.replay)
            return True
        except Exception, ex:
            self._mongo_retry = time.time() + self.RETRY_DELAY
            self._needs_replay = True
            log.error('Save fail(%s), try again at %s (now is %s)',
                      ex, self._mongo_retry, time.time())
            return False
        
    def open_writer(self):
        if self._fp:
            self._fp.close()
        if not os.path.exists(self._journal_dir):
            os.makedirs(self._journal_dir)
        # Trim filenames
        while len(self.filenames) > self.MAX_FILES and not self._needs_replay:
            os.remove(os.path.join(
                    self._journal_dir, self.filenames[0],))
        fn = os.path.join(
            self._journal_dir, 'z_%s.j' % datetime.utcnow().isoformat())
        self._fp = open(fn, 'wb')
        self._bytes_written = 0

    @property
    def filenames(self):
        return sorted([
                fn for fn in os.listdir(self._journal_dir)
                if fn.startswith('z_') ])

    def replay(self):
        if self._in_replay: return
        self._needs_replay = False
        self._in_replay = True
        try:
            if not os.path.exists(self._journal_dir):
                os.makedirs(self._journal_dir)
            filenames = self.filenames
            if not filenames: return
            for fn in filenames:
                full_fn = os.path.join(self._journal_dir, fn)
                log.info('Replay journal %s', full_fn)
                with open(full_fn, 'rb') as fp:
                    while True:
                        obj = self._read(fp)
                        if obj is None: break
                        if not self._try_save(obj): return
            self.open_writer()
        except Exception, ex:
            log.error('Error replaying log: %s', ex)
            gevent.spawn(self.replay)
        finally:
            self._in_replay = False

    def _write(self, obj):
        try:
            obj_buf = bson.BSON.encode(obj)
            checksum = sha1(obj_buf).digest()
            self._fp.write(struct.pack('<I', len(obj_buf)))
            self._fp.write(obj_buf)
            self._fp.write(checksum)
            self._fp.flush()
            return len(obj_buf) + len(checksum)
        except:
            log.fatal('Cannot journal, exiting', exc_info=True)
            sys.exit(1)

    def _read(self, fp):
        s = fp.read(4)
        if len(s) < 4:
            return None
        length = struct.unpack('<I', s)[0]
        s = fp.read(length)
        calc_sum = sha1(s).digest()
        read_sum = fp.read(len(calc_sum))
        if calc_sum != read_sum:
            return None
        return bson.BSON(s).decode()
