import time
import transaction
from ZEO.ClientStorage import ClientStorage
from ZODB import DB
import ZODB.POSException
import ZEO.zrpc.error
import ZEO.Exceptions
import logging
logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(0)


storage = ClientStorage([('127.0.0.1', 8200), ('127.0.0.1', 8201)],
                        storage='main')
db = DB(storage)
conn = db.open()
root = conn.root()

root['x'] = 0

while True:
    root['x'] += 1
    try:
        transaction.commit()
    except (ZODB.POSException.ConflictError,
            ZEO.zrpc.error.DisconnectedError,
            ZEO.Exceptions.ClientDisconnected):
        transaction.abort()
        continue
    print root['x']
    time.sleep(1)
