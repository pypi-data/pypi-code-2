"""
Python based account access.
This module allows the user to provision API keys programmatically

Note that setuser() must be called before using any functions
"""
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
import logging

__username = None
__password = None
__httpAdapter = None
__url = None

try:
    from json import dumps as serialize
    from json import loads as deserialize
except ImportError: #If python version < 2.6, we need to use simplejson
    from simplejson import dumps as serialize
    from simplejson import loads as deserialize

from .cloud import CloudException
from .transport.adapter import SerializingAdapter
from .transport.network import HttpConnection

cloudLog = logging.getLogger('Cloud.account')

#URLs:        
_apikey_list_query = 'apikeys/list/'
_apikey_create_query = 'apikeys/create/'
_apikey_deactivate_query = 'apikeys/deactivate/'
_apikey_activate_query = 'apikeys/activate/'
_apikey_updatenote_query = 'apikeys/updatenote/'     

def setuser(username, password):
    """Set the username and password associated with your PiCloud account"""
    global __username, __password    
    __username = username
    __password = password




def _doRequest(url, post_values):    
    global __username, __password, __url, __httpAdapter
    
    if not __username or not __password:
        raise CloudException('cloud.account credentials not set. Please use setuser first before making calls', 
                             logger = cloudLog)
        
    if not __httpAdapter:
        from . import _getcloud
        cloud = _getcloud()
        if isinstance(cloud.adapter,SerializingAdapter) and \
            isinstance(cloud.adapter.connection,HttpConnection) and \
            cloud.adapter.connection.opened:
            __httpAdapter = cloud.adapter.connection
        else:
            __httpAdapter = HttpConnection("","")
            __httpAdapter.open(True)
            
        __url = __httpAdapter.url + 'pyaccount/'
    
    post_values['username'] = __username
    post_values['password'] = __password
    
    lines =  __httpAdapter.rawquery(__url + url, post_values)
    return deserialize(lines)
   

def api_keys():
    """
    Returns a list of dictionaries, each which defines an api_key.
    The keys within each return api_key are:
    
    * api_key: numeric key to use with cloud.setkey
    * api_secretkey: Secret key associated with api_key
    * active: Whether key is active (and can be used)
    * created: Time key was created
    * note: Customizable note associated with key.
    """
    
    return _doRequest(_apikey_list_query,{})

def create_api_key():
    """
    Create an api key, which will automatically be activated.    
    Returns information about the newly created key.
    
    .. note:: 
        
        There is a limit of 50 active api keys
    """
    
    return _doRequest(_apikey_create_query,{})

def deactivate_api_key(key):
    """
    Deactivate an api key specified by the integer *key*
    """
    
    return _doRequest(_apikey_deactivate_query,{'api_key': str(key)})

def activate_api_key(key):
    """
    Deactivate a deactivated api key specified by the integer *key*
    """
    return _doRequest(_apikey_activate_query,{'api_key': str(key)})
    
def update_api_key_note(key, note):
    """
    Set the *note* associated with an api *key*
    """
    
    return _doRequest(_apikey_updatenote_query,{
                                             'api_key': str(key),
                                             'note': str(note)
                                             })
        