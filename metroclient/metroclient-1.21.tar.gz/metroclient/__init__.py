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
import pickle
import getpass
import tempfile
import time
import base64

VERSION = '1.21'

def login_required(func):
    def decorator(self, *args, **kwargs):
        if not self._authenticated:
            self.authenticate()
        return func(self, *args, **kwargs)
    return decorator

def app_id_required(func):
    def decorator(self, *args, **kwargs):
        if len(args) == 0 and 'app_id' not in kwargs:
            raise MetroClientError('You must specify an application global ID')
        return func(self, *args, **kwargs)
    return decorator

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
    """
    Metro client

    Handles all operations with AppHosted
    """
    __version__ = VERSION
    def __init__(self, username=None, api_key=None, **kwargs):
        self.__username = username
        self.__api_key = api_key
        self.__auth_token = None
        if 'metro_host' in kwargs:
            #print('Using Metro host: {0}'.format(kwargs['metro_host']))
            self.__metro_url = 'https://{0}'.format(kwargs['metro_host'])
        else:
            self.__metro_url = 'https://metro.apphosted.com'
        self.__api_url = '{0}/api/1.0'.format(self.__metro_url)
        self.__manage_url = '{0}/manage'.format(self.__api_url)
        self.__version = VERSION
        self._authenticated = False
        self._http = httplib2.Http()
        self._headers = {
            'User-Agent': 'metroclient/{0}'.format(VERSION),
            'Content-type': 'application/json',
        }
        

    def _request(self, url=None, method='GET', body=None):
        try:
            if not url:
                raise MetroClientError('You must specify a url')
            resp = None
            cont = None
            if body:
                resp, cont = self._http.request(url, method, headers=self._headers, body=body)
            else:
                resp, cont = self._http.request(url, method, headers=self._headers)
            return resp, cont
        except Exception, d:
            raise MetroClientError(d)

    def authenticate(self, username=None, password=None):
        """
        Authenticates to Metro
        """
        try:
            if not self.__username and not username:
                self.__username = raw_input('AppHosted Username: ').strip()
            if not self.__api_key and not password:
                password = getpass.getpass('AppHosted Password: ')
            if username:
                self.__username = username
            self._headers['x-auth-user'] = self.__username
            if self.__api_key:
                self._headers['x-auth-key'] = self.__api_key
            else:
                self._headers['x-auth-pass'] = password
            # auth
            url = '{0}/auth'.format(self.__api_url)
            resp, cont = self._request(url)
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
            return True
        except KeyboardInterrupt:
            return False

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
                return
                #raise MetroClientError('You must specify a task ID')
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
    
    @login_required
    def deploy(self, archive_file=None):
        '''Deploys the specified package'''
        try:
            if not archive_file:
                raise MetroClientError('You must specify an archive file')

            # convert to base64
            f = open(archive_file, 'r')
            data = {
                'package': base64.b64encode(f.read()),
            }
            f.close()
            url = '{0}/deploy'.format(self.__manage_url)
            resp, cont = self._request(url, method='POST', body=json.dumps(data))
            json_resp = json.loads(cont)
            task_id = None
            if resp.status == 200:
                if json_resp.has_key('task_id'):
                    task_id = json_resp['task_id']
            else:
                print('Error deploying: {0}'.format(json_resp['message']))
            return task_id
        except Exception, d:
            raise MetroClientError(d)

    @login_required
    def list_apps(self):
        """
        Returns a dict of applications and global IDs
        """
        resp, cont = self._request(url='{0}/apps'.format(self.__manage_url))
        json_resp = json.loads(cont)
        if resp.status == 200:
            return json_resp['apps']
        else:
            raise MetroClientError('Error getting applications: {0}'.format(json_resp['message']))

    @login_required
    def start_shell(self, app_name=None):
        if not app_name:
            raise MetroClientError('You must specify an application name')
        try:
            apps = self.list_apps()
            app_id = apps[app_name]
            resp, cont = self._request(url='{0}/{1}/shell'.format(self.__manage_url, app_id))
            json_resp = json.loads(cont)
            if resp.status == 200:
                conn_info = {}
                conn_info['host'] = json_resp['host']
                conn_info['port'] = json_resp['port']
                return conn_info
            else:
                raise MetroClientError('Error starting shell: {0}'.format(json_resp['message']))

        except Exception, d:
            raise MetroClientError(d)

    @login_required
    @app_id_required
    def get_app_info(self, app_id=None):
        """
        Returns a dict with application information
        """
        resp, cont = self._request(url='{0}/{1}/info'.format(self.__manage_url, app_id))
        json_resp = json.loads(cont)
        if resp.status == 200:
            return json_resp
        else:
            raise MetroClientError('Error getting applications: {0}'.format(json_resp['message']))

    
