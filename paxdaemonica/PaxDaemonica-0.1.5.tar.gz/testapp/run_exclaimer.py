import time
import uuid
import pickle
import json
from redis import Redis
from app import exclaimer


if __name__ == '__main__':
    rqs = []
    for i in range(0, 1):
        promise = exclaimer.delay(str(i), paxd_timeout=2)
        print promise.get()
        # try:
        #     rqs.append(request.send())
        # except Exception, e:
        #     print e.type, e.traceback
        # time.sleep(1)
        # str(i),
        #     'response_queue' : rq,
        # }))
