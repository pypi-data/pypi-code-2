from logging import getLogger
from ZODB.POSException import POSKeyError
from ZODB.serialize import referencesf
from ZODB.utils import z64
from transaction import get

logger = getLogger("dm.zodb.repair")

def restore_from_backup(lost, backup, target):
  """restore objects *lost* reading *backup* writing *target*.

  *lost* is an iterable of oids identifying lost objects,
  *backup* and *target* are open ZODB storages.

  writes ``dm.zodb.repair`` log entries.
  """
  T = get()
  T.note("dm.zodb.repair")
  target.tpc_begin(T)
  lost = list(lost)
  # work around a "ZEO.ClientStorage" bug
  target.load(z64, '')
  while lost:
    oid = lost.pop()
    logger.info("restoring %r", oid)
    # check that ``oid`` is indeed missing
    try:
      target.load(oid, '')
      logger.warn("%r present in target -- ignoring", oid)
      continue
    except POSKeyError: pass
    try: data, serial = backup.load(oid, '')
    except POSKeyError:
      logger.error("%r not found in backup -- ignoring", oid)
      continue
    target.store(oid, serial, data, '', T)
    # add referenced objects if not in target
    refs = referencesf(data)
    for r in refs:
      try: target.load(r, '')
      except POSKeyError:
        logger.info("added %r referenced by %r to lost objects", r, oid)
        lost.append(r)
  target.tpc_vote(T)
  target.tpc_finish(T)


