import time
from paxd.client import task

@task(queue='testapp.app.exclaimer')
def exclaimer(thing):
    time.sleep(0.2)
    return str(thing) + '!!!!!!!'

@task(queue='testapp.app.error_test')
def error_test():
    raise Exception('BAD BAD BAD')
