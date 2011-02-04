"""
Python account management.
This module allows the user to manage account information programmatically.
Features include provisioning api keys and managing real time unit requests.

Note that your api_key must be set before using any functions.
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
import sys, logging, datetime

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
_apikey_list_query = 'pyaccount/apikeys/list/'
_apikey_create_query = 'pyaccount/apikeys/create/'
_apikey_deactivate_query = 'pyaccount/apikeys/deactivate/'
_apikey_activate_query = 'pyaccount/apikeys/activate/'
_apikey_updatenote_query = 'pyaccount/apikeys/updatenote/'

_rt_request_query = 'pyaccount/rt/request/'
_rt_release_query = 'pyaccount/rt/release/'
_rt_list_query = 'pyaccount/rt/list/'        

"""
This module utilizes the cloud object extensively
The functions can be viewed as instance methods of the Cloud (hence accessing of protected variables)
"""

def _getCloud():
    cl = getattr(sys.modules['cloud'],'__cloud')
    cl._checkOpen()
    return cl

def _getConnection(cloud):
    """Return connection object associated Cloud
    Errors if object is not an HttpConnection
    """
    
    if not isinstance(cloud.adapter,SerializingAdapter):
        raise Exception('Unexpected cloud adapter being used')
    conn = cloud.adapter.connection
    if isinstance(conn,HttpConnection):
        return conn
    else:
        raise RuntimeError('Cannot use cloud.account functions when in simulation')

def _fixTimeElement(dct, key):
    item = dct.get(key)
    if item == 'None': #returned by web instead of a NoneType None
        item = None
        dct[key] = item
    if item:
        dct[key] = datetime.datetime.strptime(item,'%Y-%m-%d %H:%M:%S')
    return dct

"""
Api key management
"""

def list_api_keys():
    """
    Returns a list of dictionaries, each which defines an api_key.
    The keys within each returned dictionary are:
    
    * api_key: numeric key used with cloud.setkey
    * api_secretkey: Secret key associated with api_key
    * active: Whether key can be used
    * created: Time key was created (GMT)
    * note: Customizable note associated with key.
    """
    conn = _getConnection(_getCloud())
    keys = deserialize(conn.query(_apikey_list_query,{}))
    return [_fixTimeElement(key,'created') for key in keys]

def create_api_key():
    """
    Create an api key, which will automatically be activated.    
    Returns a dictionary describing the newly created key, with the same format
    as the keys returned by list_api_keys.
    
    .. note:: 
        
        There is a limit of 50 active api keys
    """
    conn = _getConnection(_getCloud())
    return _fixTimeElement(deserialize(conn.query(_apikey_create_query,{})),'created')

def deactivate_api_key(key):
    """
    Deactivate an api key specified by the integer *key*.
    Returns dictionary describing deactivated key.
    """
    try:
        int(key)
    except ValueError:
        raise TypeError('deactivate_api_key requires a numeric api key')
    
    conn = _getConnection(_getCloud())
    return _fixTimeElement(deserialize(conn.query(_apikey_deactivate_query,{'target_key': str(key)})),
                           'created')

def activate_api_key(key):
    """
    Activate a deactivated api key specified by the integer *key*.
    Returns dictionary describing activated key.
    """
    try:
        int(key)
    except ValueError:
        raise TypeError('activate_api_key requires a numeric api key')
    
    conn = _getConnection(_getCloud())
    return _fixTimeElement(deserialize(conn.query(_apikey_activate_query,{'target_key': str(key)})),
                           'created')
    
def update_api_key_note(key, note):
    """
    Set the *note* associated with an api *key*.
    Returns dictionary describing noted key.
    """
    try:
        int(key)
    except ValueError:
        raise TypeError('update_api_key_note requires a numeric api key')
    
    conn = _getConnection(_getCloud())
    return _fixTimeElement(deserialize(conn.query(_apikey_updatenote_query,{
                                             'target_key': str(key),
                                             'note': str(note)
                                             })),'created')
        
"""
Real time requests management
"""
def list_rt_units(request_id = ""):
    """
    Returns a list of dictionaries describing realtime units requests.
    If *request_id* is specified, only show realtime unit request with that request_id
    
    The keys within each returned dictionary are:
    
    * request_id: numeric ID associated with the request
    * compute_units: Number of compute units requested with this request
    * start_time: Time when real time request was satisfied; None if still pending     
    """
    if request_id != "":
        try:
            int(request_id)
        except ValueError:
            raise TypeError('Optional parameter to list_rt_units must be a numeric request_id')

    conn = _getConnection(_getCloud())
    rt_list = deserialize(conn.query(_rt_list_query,{'rid': str(request_id)}))
    return [_fixTimeElement(rt,'start_time') for rt in rt_list]

def request_rt_units(num_units):
    """
    Request *num_units* of real time compute units.
    Returns a dictionary describing the newly created realtime request, with the same format
    as the requests returned by list_rt_units.
    """
    conn = _getConnection(_getCloud())
    return _fixTimeElement(deserialize(conn.query(_rt_request_query,{'rt_cu': num_units})),'start_time')

def release_rt_units(request_id):
    """
    Release the realtime unit request associated with *request_id*. 
    Request must have been satisfied to terminate.
    """
    try:
        int(request_id)
    except ValueError:
        raise TypeError('release_rt_units requires a numeric request_id')
    
    conn = _getConnection(_getCloud())    
    return _fixTimeElement(deserialize(conn.query(_rt_release_query,{'rid': str(request_id)})),'start_time')
