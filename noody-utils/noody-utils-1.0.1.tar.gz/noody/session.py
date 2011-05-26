# -*- coding: latin-1 -*-

import sys
import traceback
import urllib, urllib2

GW_ADDRESS = '192.168.51.1'
GW_PORT = '2060'
GW_ID = 'n_zola1'
LOGIN_URL = 'https://www.econoeticalabs.com/wifidog/login/index.php'
AUTH_SOURCE = 'default-network'

class Session(object):

    def __init__(self, username=None, password=None,
                 gw_address=GW_ADDRESS, gw_port=GW_PORT,
                 gw_id=GW_ID):
        self.username = username
        self.password = password
        self.gw_address = gw_address
        self.gw_port = gw_port
        self.gw_id = gw_id
        self.debug = False

    def debug_on(self):
        self.debug = True


    def debug_off(self):
        self.debug = True

    def open(self):
        params = urllib.urlencode(
            dict(username=self.username,
                 password=self.password,
                 form_request='login',
                 gw_address=self.gw_address,
                 gw_port=self.gw_port,
                 gw_id=self.gw_id,
                 auth_source=AUTH_SOURCE))
        if self.debug:
            print "DEBUG MODE __ Login __ URL: %s" % LOGIN_URL
            print "DEBUG MODE __ Login __ PARAMS: %s" % params
        try:
            f = urllib2.urlopen(LOGIN_URL, params)
        except urllib2.URLError:
            print "Error in opening Noody session. (Invoke with -d for" \
                  u" printing error stacktrace)."
            if self.debug:
                traceback.print_exc(file=sys.stdout)

    def close(self):
        pass