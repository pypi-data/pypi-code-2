"""
For managing files on PiCloud's S3 store.

cloud.setkey() must be called before using any functions in this module.

.. note::

    This module cannot be used to access the PiCloud distributed file system.
"""
from __future__ import with_statement
"""
Copyright (c) 2010 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@picloud.com

The cloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html    
"""
import os
import logging
import threading

__httpConnection = None
__url = None
__query_lock = threading.Lock() #lock on http adapter updates

try:
    from json import loads as deserialize
except ImportError: #If python version < 2.6, we need to use simplejson    
    from simplejson import loads as deserialize

from .transport.adapter import SerializingAdapter
from .transport.network import HttpConnection

cloudLog = logging.getLogger('Cloud.account')

_file_new_query = '/new/'
_file_put_query = '/put/'
_file_list_query = '/list/'
_file_get_query = '/get/'
_file_exists_query = '/exists/'
_file_delete_query = '/delete/'


def _check_connection():
    """Generate HTTPConnection if it does not exist
    Also copy last key used
    Note that this cannot be part of the main cloud object due to 
    need for this to connect to PiCloud even in simulation
    """
    global __url, __httpConnection
        
    from . import _getcloud
    cloud = _getcloud()
    if not isinstance(cloud.adapter,SerializingAdapter):
        raise Exception('Unexpected cloud adapter being used')
    
    if isinstance(cloud.adapter.connection,HttpConnection):
        #Connected mode
        if not cloud.adapter.connection.opened:
            cloud.adapter.connection.open()
            
        __httpConnection = cloud.adapter.connection
        
    else:  #running simulator
        from . import cloudinterface
        if __httpConnection: #check for changes?
            if cloudinterface.last_api_key and cloudinterface.last_api_key != __httpConnection.api_key:
                __httpConnection.api_key = cloudinterface.last_api_key
                __httpConnection.api_secretkey = cloudinterface.last_api_secretkey
        else: #no http adapter
            __httpConnection = HttpConnection(cloudinterface.last_api_key,cloudinterface.last_api_secretkey)
            __httpConnection.open(True)
        
    if __httpConnection.api_key is None or __httpConnection.api_secretkey is None:
        raise Exception('cloud.setkey must be called first to set api keys')
    __url = __httpConnection.url + 'file'

def _query(url, post_values, headers={}):
    
    with __query_lock:
        _check_connection()
        
        post_values['api_key'] = __httpConnection.api_key
        post_values['api_secretkey'] = __httpConnection.api_secretkey    
        
        lines =  __httpConnection.rawquery(__url + url, post_values)
        return deserialize(lines)

def _post(url, post_values, headers={}):
    
    response =  __httpConnection.post(url, post_values, headers, use_gzip = False)
    return response

class CloudFile(object):
    """
    A CloudFile represents a file stored on PiCloud as a readonly file-like stream.
    Seeking is not available.
    """
    
    __http_response = None
    
    def __init__(self, http_response):
        self.__http_response = http_response
    
    def __iter__(self):
        return self
    
    def close(self):        
        return self.__http_response.close()
    
    def next(self):
        return self.__http_response.next()
    
    def read(self, size=-1):
        return self.__http_response.read(size)
        
    def readline(self, size=-1):
        return self.__http_response.readline(size)
        
    def readlines(self, sizehint=0):
        return self.__http_response.readlines(sizehint)
            

def put(file_path, name=None):
    """
    Transfers the file specified by ``file_path`` to PiCloud. The file can be retrieved
    later using the get function.    
    
    If ``name`` is specified, the file will be stored as name on PiCloud.
    Otherwise it will be stored as the basename of file_path.
    
    Example::    
    
        cloud.files.put('data/names.txt') 
    
    This will transfer the file from the local path 'data/names.txt'
    to PiCloud and store it as 'names.txt'.
    It can later retrieved via cloud.files.get('names.txt') 
    """

    if not name:
        name = os.path.basename(file_path)
    
    # open the requested file in binary mode (relevant in windows)
    f = open(file_path, 'rb')
    
    putf(f, name)


def putf(f, name):
    """
    Similar to put.
    putf, however, accepts a file object ``f`` instead of a file_path.
    
    .. warning:: 
    
        If the file object does not correspond to an actual file on disk,
        it will be read entirely into memory before being transferred to PiCloud.   
    """
    
    if isinstance(f, (str, unicode)):
        from cStringIO import StringIO
        f = StringIO(f)
    
    
    
    try:
        # get a file ticket
        resp = _query(_file_new_query, {'name': name})
        ticket = resp['ticket']
        params = resp['params']
        
        url = params['action']
        
        # set file in ticket
        ticket['file'] = f
        
        # post file using information in ticket
        resp =  _post(url, ticket)
        resp.read()
        
    finally:
        f.close()


def list():
    """
    List all files stored on PiCloud.
    """
    #note beware: List is defined as this function
    resp = _query(_file_list_query, {})
    files = resp['files']
    return files

def exists(file_name):
    """
    Check if a file named ``file_name`` is stored on PiCloud.
    """
    
    resp = _query(_file_exists_query, {'name': file_name})
    exists = resp['exists']
    return exists
    
def delete(file_name):
    """
    Deletes the file named ``file_name`` from PiCloud.
    """

    resp = _query(_file_delete_query, {'name': file_name})
    deleted = resp['deleted']
    return deleted
    
def get(file_name, save_path=None):
    """
    Retrieves the file named by ``file_name`` from PiCloud and stores it to ``save_path``.
        
    Example::    
    
        cloud.files.get('names.txt','data/names.txt') 
    
    This will retrieve the 'names.txt' file on PiCloud and save it locally to 
    'data/names.txt'. 
    """
    
    if not save_path:
        save_path = os.path.basename(file_name)
        
    cloud_file = getf(file_name)
    
    chunk_size = 64000
    f = open(save_path, 'wb')
    
    while True:
        data = cloud_file.read(chunk_size)
        if not data:
            break
        f.write(data)
    
    f.close()

def getf(file_name):
    """
    Retrieves the file named by ``file_name`` from PiCloud.
    Returns a CloudFile (file-like object) that can be read() to retrieve the file's contents 
    """    

    # get ticket
    resp = _query(_file_get_query, {'name': file_name})
    
    ticket = resp['ticket']
    params = resp['params']
    
    # Set post_values to None to force GET request
    resp =  _post(params['action'], None, ticket)
    
    cloud_file = CloudFile(resp)
    
    return cloud_file
