"""
For managing crons on PiCloud.  
Crons allow you to "register" a function to be invoked periodically on PiCloud
according to a schedule you specify.

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
import sys

from .util import numargs
from .util.zip_packer import Packer
from .util.cronexpr import CronTime
from .transport.adapter import SerializingAdapter
from .transport.network import HttpConnection

try:
    from json import dumps as serialize
    from json import loads as deserialize
except ImportError: #If python version < 2.6, we need to use simplejson
    from simplejson import dumps as serialize
    from simplejson import loads as deserialize


_register_query = 'cron/register/'
_deregister_query = 'cron/deregister/'
_run_query = 'cron/run/'
_list_query = 'cron/list/'
_info_query = 'cron/info/'

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
        raise RuntimeError('Cannot use cloud.cron functions when in simulation')
    

def register(func, label, schedule, **kwargs):
    """       
    Register *func* (a callable) to be run periodically on PiCloud according to *schedule*
    
    The cron can be managed in the future by the specified *label* 
    
    *Schedule* is a BSD-style cron timestamp, specified as either a string of 5 non-
    whitespace characters delimited by spaces or as a sequence (tuple, list, etc.) of 
    5 elements, each with non-whitespace characters.
    The ordering of the characters represent scheduling information for minutes, 
    hours, days, months, and days of week.                   
    See full format specification at http://unixhelp.ed.ac.uk/CGI/man-cgi?crontab+5        
    Year is not supported.  The N/S increment format is though.
                    
    PiCloud schedules your crons under the *GMT (UTC+0) timezone*.

    Certain special *kwargs* associated with cloud.call can be attached to the periodic jobs: 
        
    * _fast_serialization:
        This keyword can be used to speed up serialization, at the cost of some functionality.
        This affects the serialization of the spawned jobs' return value.
        The stored function will always be serialized by the enhanced serializer, with debugging features.
        Possible values keyword are:
                    
        0. default -- use cloud module's enhanced serialization and debugging info            
        1. no debug -- Disable all debugging features for result            
        2. use cPickle -- Use python's fast serializer, possibly causing PicklingErrors                
    
    * _high_cpu:
            Set this to true to run jobs on a faster processor. Additional charges may apply.
    * _profile:
            Set this to True to enable profiling of your code. Profiling information is 
            valuable for debugging, but may slow down your jobs.
    * _restartable:
            In the very rare event of hardware failure, this flag indicates that a spawned 
            job can be restarted if the failure happened in the middle of it.
            By default, this is true. This should be unset if the function has external state
            (e.g. it modifies a database entry)
                 
    .. note:: 
    
        The callable must take no arguments.  To schedule functions that take arguments,
        wrap it with a closure. e.g. func(x,y) --> lambda: func(x,y)
    """
    
    cloud = _getCloud()     
    
    if not callable(func):
        raise TypeError( 'cloud.cron.register first argument (%s) is not callable'  % (str(func) ))
    try:
        nargs = numargs(func)
    except ValueError: #some types we don't error check
        nargs = 0         
    if nargs != 0:
        raise ValueError('cron functions must have 0 (required) arguments. %s requires %s' \
                         % (str(func), nargs))
        
        
    
    #TODO: Additional error checking for args
    
    #check for cron sanity
    if hasattr(schedule,'__iter__'):
        schedule = ' '.join(schedule)
    if not isinstance(schedule, str):
        schedule = str(schedule)
    CronTime(schedule) #throw exception if invalid cron format
    
    #ASCII label:
    try:
        label = label.decode('ascii').encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        raise TypeError('label must be an ASCII string')
    
    params = cloud._getJobParameters(func, kwargs, 
                                        ignore=['_label', '_depends_on'])
    
    conn = _getConnection(cloud)
    
    sfunc, sarg, logprefix, logcnt = cloud.adapter.cloudSerialize(func,params['fast_serialization'], 
                                                                  [],logprefix='cron.')
    
    #Below is derived from HttpAdapter.job_add
    conn._update_params(params)
    
    cloud.adapter.depSnapShot() #let adapter make any needed calls for dep tracking
    
    data = Packer()
    
    #Store as params1, func1, args1
    data.add(serialize({'label': label,
                        'cron_exp' : schedule,
                        'priority': params['job_priority'],
                        'restartable': params['job_restartable'],
                        'cpu_units': params['cpu_units'],
                        'profile': params['profile'],                            
                        'fast_serialization' : params['fast_serialization'],
                        'mod_versions' : params['mod_versions']
                                   }) )
    data.add(sfunc)
    
    params['data'] = data.finish()       
            
    del params['fast_serialization'], params['job_priority'], \
        params['job_restartable'], params['cpu_units'], params['profile'],                     
    
    #send over the wire!
    conn.query(_register_query, params) 

def deregister(label):
    """
    Deregister (delete) the cron specified by *label*
    """
    cloud = _getCloud() 

    #ASCII label:
    try:
        label = label.decode('ascii').encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        raise TypeError('label must be an ASCII string')
    
    conn = _getConnection(cloud)
    
    conn.query(_deregister_query, {'label': label})   
        
def manual_run(label):
    """
    Manually run the cron specified by *label*
    Returns the 'jid' of the job created by this run command 
    """ 
    cloud = _getCloud() 

    #ASCII label:
    try:
        label = label.decode('ascii').encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        raise TypeError('label must be an ASCII string')
    
    conn = _getConnection(cloud)
    
    resp = conn.query(_run_query, {'label': label})
    return deserialize(resp)['jid']   
    
def list():
    """
    List labels of active crons
    """ 
    #note beware: List is defined as this function
    cloud = _getCloud()
    conn = _getConnection(cloud)
    resp = conn.query(_list_query, {})
    return deserialize(resp)['labels']

def info(label):
    """    
    Return a dictionary of relevant info about cron specified by *label*
    
    Info includes:
        
    * label: The same as was passed in
    * schedule: The schedule of this cron
    * last_run: Time this cron was last run
    * last_jid: Last run jid of this cron
    * created: When this cron was created   
    * creator_host: Hostname of the machine that registered this cron    
    * funcname: Name of function associated with cron
    """
    
    cloud = _getCloud()
    conn = _getConnection(cloud)
    resp = conn.query(_info_query, {'label':label})
    return deserialize(resp)    
    
    
     
         
            
        
        
        
        
        
        
            
        