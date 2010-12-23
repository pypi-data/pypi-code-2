#!/usr/bin/env python
#-*- coding: utf-8 -*-

# We need some little fix to let consume running from any path
# you must set those two variables.
PROJECT_SETTINGS= 'mp_test.settings'
PROJECT_PARENT_PATH = '/home/sam/Aptana_Studio_Workspace/'
FETCH_JOB_INTERVAL = 5

# do NOT modify those code, because we need fix sys.path
import sys
import os
from django.utils import importlib # this module is very magic
from django.core.management import setup_environ
PROJECT_PATH = os.path.join(PROJECT_PARENT_PATH, PROJECT_SETTINGS.split('.')[0])
sys.path.insert(0, PROJECT_PARENT_PATH)
sys.path.insert(1, PROJECT_PATH)

# import project settings
settings = importlib.import_module(PROJECT_SETTINGS)
# put setting into runtime env
setup_environ(settings)

# now import mp_backend, more like normal django code... ha
from mixpanel_django.backends import mp_backend
import urllib2
import multiprocessing
import time

handler = urllib2.HTTPHandler()
opener = urllib2.build_opener(handler)
opener.addheaders = [('User-agent', 'MixpanelDjango/0.1')]
urllib2.install_opener(opener)

def push_event_worker(job):
    '''
    push event to Mixpanel
    @param job: job is string, that's we builded rest API request url
    '''
    try:
        fp = urllib2.urlopen(job)
        res = fp.read()
    except urllib2.URLError:
        return (False, job)
        
    if res == '1':
        return (True, job)
    else:
        # we accepted job not not logged on Mixpanel.
        return (True, job)
    
def main():
    # check system CPU numbers
    NUMBER_OF_PROCESS = multiprocessing.cpu_count() * 2
    
    # loop forever
    while 1:
        
        # preparing jobs list 
        jobs = []
        for x in range(NUMBER_OF_PROCESS):
            job = mp_backend.fetch_event()
            if job:
                jobs.append(job.body)
            else:
                continue
            # got job, immediately delete on beanstalk queue
            job.delete()
        
        # did not found any jobs, just continue next cycle
        if jobs == []:
            time.sleep(1)
            continue
        # ok jobs are ready, we starting multi processing pool
        pool = multiprocessing.Pool(NUMBER_OF_PROCESS)
        ress = pool.map(push_event_worker, jobs)
        
        # wait all jobs finished and terminat it
        pool.close()
        pool.join()
        pool.terminate()
        
        # check send event result
        for res, job in ress:
            # oops, got error, put job back
            if not res:
                mp_backend.send_event(job)
            
if __name__ == '__main__':
    main()