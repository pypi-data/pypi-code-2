import sys
import time

try:
    import json
except ImportError:
    import simplejson as json

def dispatch(taskstring, url, *args):
    task = json.loads(taskstring)
    print >> sys.stderr, task
    print >> sys.stderr, url
    time.sleep(1)
    return taskstring
