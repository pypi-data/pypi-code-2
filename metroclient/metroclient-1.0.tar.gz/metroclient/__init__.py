#!/usr/bin/env python
#
#   Metro Application Manager
#       (c) Lumentica, 2011
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
import httplib2
import json
import getpass
import tempfile
import time
import base64

VERSION = '1.0'

class MetroClientAuthError(Exception):
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return repr(self.value)

class MetroClientError(Exception):
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return repr(self.value)

class MetroClient(object):
    '''Metro Client
        handles all operations with AppHosted
    '''
    __version__ = '1.0'
    def __init__(self, username=None, api_key=None):
        self.__username = username
        self.__api_key = api_key
        self.__auth_token = None
        self.__metro_url = 'https://metro.apphosted.com'
        self.__api_url = 'https://metro.apphosted.com/api/v1.0'
        self.__manage_url = '{0}/manage'.format(self.__api_url)
        self.__version = VERSION
        self._authenticated = False
        self._http = httplib2.Http()
        self._headers = {
            'User-Agent': 'metroclient/{0}'.format(VERSION),
            'Content-type': 'application/json',
        }
        

    def _request(self, url=None, method='GET', body=None):
        if not url:
            raise MetroClientError('You must specify a url')
        if body:
            return self._http.request(url, method, headers=self._headers, body=body)
        else:
            return self._http.request(url, method, headers=self._headers)

    def authenticate(self, username=None, password=None):
        '''Authenticates to Metro
        '''
        if not self.__username and not username:
            self.__username = raw_input('AppHosted Username: ').strip()
        if not self.__api_key and not password:
            password = getpass.getpass('AppHosted Password: ')
        self._headers['x-auth-user'] = self.__username
        if self.__api_key:
            self._headers['x-auth-key'] = self.__api_key
        else:
            self._headers['x-auth-pass'] = password
        # auth
        resp, cont = self._request('{0}/auth'.format(self.__api_url))
        try:
            data = json.loads(cont)
        except:
            raise MetroClientAuthError('Invalid response')
        # remove x-auth-key & x-auth-pass as soon as possible
        if self._headers.has_key('x-auth-key'):
            self._headers.pop('x-auth-key')
        if self._headers.has_key('x-auth-pass'):
            self._headers.pop('x-auth-pass')
        if resp.status == 200:
            if data.has_key('x-auth-token'):
                self._headers['x-auth-token'] = data['x-auth-token']
            else:
                raise MetroClientAuthError(data['message'])
        else:
            raise MetroClientAuthError(data['message'])
        self._authenticated = True

    def check_for_update(self):
        '''Checks for updates to the Metro client'''
        resp, cont = self._request('{0}/client/checkversion/'.format(self.__metro_url))
        if resp.status == 200:
            if float(cont) > float(self.__version):
                print('** Update available (Version: {0}) **\n'.format(cont))
        else:
            raise MetroClientError('Error checking for updates')

    def create_package(self, filename=None, path=None):
        '''Creates a package to be used for deployment'''
        try:
            if filename and path and filename != '' and path != '':
                base_dir = os.path.basename(path)
                cwd = os.getcwd()
                os.chdir(path)
                # if abs path; use
                if filename.startswith(os.sep):
                    archive_file = filename
                else:
                    archive_file = os.path.join(tempfile.gettempdir(), filename)
                if os.path.exists(archive_file):
                    # remove existing archive:
                    os.remove(archive_file)
                archive = tarfile.open(archive_file, 'w:gz')
                archive.add(os.getcwd(), arcname=base_dir)
                archive.close()
                os.chdir(cwd)
        except Exception, d:
            raise MetroClientError(d)
    
    def get_task_status(self, task_id=None):
        '''Gets the status of a pending task'''
        try:
            if task_id == None:
                raise MetroClientError('You must specify a task ID')
            if not self._authenticated:
                self.authenticate()
            url = '{0}/task/{1}/status'.format(self.__manage_url, task_id)
            resp, cont = self._request(url)
            data = json.loads(cont)
            if resp.status == 200:
                return data
            else:
                return data['message']
        except Exception, d:
            raise MetroClientError(d)

    def deploy(self, archive_file=None):
        '''Deploys the specified package'''
        try:
            if not archive_file:
                raise MetroClientError('You must specify an archive file')
            if not self._authenticated:
                self.authenticate()

            # convert to base64
            f = open(archive_file, 'r')
            data = {
                'package': base64.b64encode(f.read()),
            }
            f.close()
            url = '{0}/deploy'.format(self.__manage_url)
            resp, cont = self._request(url, method='POST', body=json.dumps(data))
            json_resp = json.loads(cont)
            if resp.status == 200:
                task_id = json_resp['task_id']
            else:
                print('Error deploying: {0}'.format(json_resp['message']))
            return task_id
        except Exception, d:
            raise MetroClientError(d)



