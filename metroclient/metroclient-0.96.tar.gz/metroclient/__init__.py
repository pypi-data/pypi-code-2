#!/usr/bin/env python
#
#   Metro Application Manager
#       (c) Lumentica, 2010
#           support@lumentica.com
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
from optparse import OptionParser
import tarfile
import httplib
import urllib
import getpass
import pycurl
import time
import tempfile

VERSION = '0.96'
METRO_URL = 'https://metro.apphosted.com'
USERNAME = None
PASSWORD = None

class response_callback(object):
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents += buf
    def decode(self):
        self.contents = urllib.unquote(self.contents)
        return self.contents

def get_connection():
    if METRO_URL.find('https') > -1:
        return httplib.HTTPSConnection(METRO_URL.split('://')[-1])
    else:
        return httplib.HTTPConnection(METRO_URL.split('://')[-1])

def login_to_metro(username=None):
    if not username:
        username = raw_input('AppHosted username: ')
    else:
        print('AppHosted username: {0}'.format(username))
    password = getpass.getpass('Password: ')
    user_params = urllib.urlencode({'username': username, 'password': password})
    headers = { 
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain',
        'X-Requested-With': 'XMLHttpRequest', # set XHR to avoid CSRF restriction
    }
    # connect
    conn = get_connection()
    conn.request('POST', '/accounts/apiauth/', user_params, headers)
    resp = conn.getresponse()
    res = resp.read()
    if res.lower() == 'true': # logged in
        # set vars
        globals()['USERNAME'] = username
        globals()['PASSWORD'] = password
        return True
    else: # login failed
        print(res)
        return False

def check_for_update():
    try:
        conn = get_connection()
        conn.request('GET', '/client/checkversion/')
        resp = conn.getresponse()
        res = resp.read()
        if float(res) > float(globals()['VERSION']):
            print(' ** Update available (Version: {0}) **\n'.format(res))
    except:
        # ignore update check errors
        pass

def upload_to_metro(package_path=None, username=None):
    if login_to_metro(username=username):
        try:
            # create package and upload to Metro
            print('Deploying... Please wait...')
            cb = response_callback()
            c = pycurl.Curl()
            c.setopt(c.WRITEFUNCTION, cb.body_callback)
            c.setopt(c.POST, 1)
            #c.setopt(c.VERBOSE, 1)
            c.setopt(pycurl.TIMEOUT, 1200)
            c.setopt(pycurl.HTTPHEADER, ['X-Requested-With: XMLHttpRequest'])
            c.setopt(c.URL, METRO_URL + '/appdeploy/push/')
            form_fields = [
                ('username', USERNAME),
                ('password', PASSWORD),
                ('archive', (c.FORM_FILE, package_path)),
            ]
            c.setopt(c.HTTPPOST, form_fields)
            c.perform()
            res = cb.contents
            c.close()
            r = res.lower()
            if r.find('task') > -1:
                task_id = r.split(':')[-1]
            else:
                print('Deploy failed: {0}'.format(res))
                sys.exit(1)
            # check for status
            status = 'deploy'
            connect_errors = 0
            while status == 'deploy':
                try: # watch for connect errors
                    conn = get_connection()
                    conn.request('GET', '/appdeploy/task/{0}/status/'.format(task_id))
                    resp = conn.getresponse()
                    res = resp.read().lower()
                    if res == 'deploy':
                        time.sleep(5)
                        pass
                    elif res == 'success':
                        status = 'success'
                        print('Deploy successful...')
                    else:
                        status = 'fail'
                        print('Deploy failed: %s' % (res))
                except:
                    connect_errors += 1
                    time.sleep(5)
                    # check for max errors
                    if connect_errors == 4:
                        status = 'fail'
                        print('Deploy failed: Connect error.')
        except:
            sys.exit(1)

def create_archive(filename=None, path=None):
    if filename and path and filename != '' and path != '':
        base_dir = os.path.basename(path)
        cwd = os.getcwd()
        os.chdir(path)
        archive_file = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(archive_file):
            print('Removing existing package...')
            os.remove(archive_file)
        archive = tarfile.open(archive_file, 'w:gz')
        archive.add(os.getcwd(), arcname=base_dir)
        archive.close()
        os.chdir(cwd)

