""" 
cd eyeswebapp
python util/poster

# should we be using something like http://pypi.python.org/pypi/python-daemon/1.5.5?
"""

import sys
import time
import os
import simplejson
import httplib2
from monitor import ArgSet
from nagios import NagiosPoller

EYES_CORE_HOST = "localhost:8000"

class PollerDaemon():
    
    base_delay = 1
    delay = 1
    poller = NagiosPoller()
    
    def get_pending_monitors(self):
        """ returns a python list of pending monitors - the partial URI's to those monitors"""
        url = "http://%s/api/monitor" % EYES_CORE_HOST
        httpclient = httplib2.Http(".cache")
        (resp, content) = httpclient.request(url)
        if (200 == resp.status):
            # good response
            list_of_pending_monitors = simplejson.loads(content)
        else:
            print "Error accessing Eyes core server"
            print "Accessed: %s", url
            print "Resp: %s", resp
            return None # or do we want to return an empty list... ???
        return list_of_pending_monitors

    def get_monitor_detail(self, uri):
        """ queries the EYES CORE and gets the detail sufficient to run a monitor """
        url = "http://%s%s" % (EYES_CORE_HOST, uri)
        httpclient = httplib2.Http(".cache")
        (resp, content) = httpclient.request(url)
        if (200 == resp.status):
            # good response
            monitor_detail = simplejson.loads(content)
        else:
            print "Error accessing Eyes core server"
            print "Accessed: %s", url
            print "Resp: %s", resp
            return None # or do we want to return an empty list... ???
        return monitor_detail

    def store_monitor_result(self, mon_uri, json_results):
        """ stores the result of a monitor run through the REST api into the EYES CORE """
        httpclient = httplib2.Http(".cache")
        url = "http://%s%s%s" % (EYES_CORE_HOST, mon_uri, "store/")
        headers = {'Content-type': 'application/json'}
        print "POSTING TO %s" % url
        print "DATA: %s" % json_results
        (resp, content) = httpclient.request(url, method="POST", headers=headers, body=json_results)
        # TODO - add error handling...
        #print resp
        #print content

    def run(self):
        """ the running loop for the poller daemon"""
        while True:
            time.sleep(self.delay)
            """ a single pass through a poller run, getting all pending monitors, processing them, 
            and returning the results back through the REST API"""
            mon_list = self.get_pending_monitors()
            if len(mon_list) > 1:
                for mon_uri in mon_list:
                    mon = self.get_monitor_detail(mon_uri)
                    # print mon
                    print "--------------------------------------------------------------"
                    print "%s to use %s, last run: %s, arguments: %s" % \
                        (mon['name'], mon['plugin_name'], mon['nextupdate'], mon['json_argset'], )
                    arg_set = ArgSet()
                    arg_set.loadjson(mon['json_argset'])
                    print "==== INVOKING ===="
                    mon_result = self.poller.run_plugin(mon['plugin_name'], argset=arg_set)
                    print "--------------------------------------------------------------"
                    print "==== STORING ===="
                    self.store_monitor_result(mon_uri, mon_result.json())
                    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            else:
                # set up an exponential backup, capped at 5 minutes
                if self.delay < 60:
                    self.delay = self.delay * 2
                else:
                    self.delay = 60

if __name__ == '__main__':
    daemon = PollerDaemon()
    daemon.run()
