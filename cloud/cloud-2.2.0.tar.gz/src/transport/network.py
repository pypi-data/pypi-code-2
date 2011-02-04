"""
PiCloud network connections
This module manages communication with the PiCloud server

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
from __future__ import with_statement
import os
import sys
import socket
import urllib2
import threading
import time

from ..util import urllib2_file
from .adapter import Adapter
from ..cloud import CloudException
from .. import cloudconfig as cc
from .connection import CloudConnection

import logging
cloudLog = logging.getLogger('Cloud.HTTPConnection')

from cStringIO import StringIO

try:
    from json import dumps as serialize
    from json import loads as deserialize
except ImportError: #If python version < 2.6, we need to use simplejson
    from simplejson import dumps as serialize
    from simplejson import loads as deserialize
    
#xrange serialization:
from ..util.xrange_helper import encodeMaybeXrange, decodeMaybeXrange, iterateXRangeLimit 

#zipping:
from ..util.zip_packer import Packer

#version transport:
from ..versioninfo import release_version

def unicode_container_to_str(data):
    """
    Responses from the server may be in unicode.
    """
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, dict):
        return dict(map(unicode_container_to_str, data.iteritems()))
    elif isinstance(data, (list, tuple, set, frozenset)):
        return type(data)(map(unicode_container_to_str, data))
    else:
        return data

class HttpConnection(CloudConnection):
    """
    HTTPConnnection finds an available cloud cluster, and provides
    a gateway to query it.
    """
    
    api_key = cc.accountConfigurable('api_key',
                                     default='None',
                                     comment='your application\'s api key provided by PiCloud')
    api_secretkey = cc.accountConfigurable('api_secretkey',
                                           default='None',
                                           comment='your application\'s secret key provided by PiCloud')
    
    serverListUrl = cc.accountConfigurable('server_list_url',
                                           default='http://www.picloud.com/pyapi/servers/list/',
                                           comment="url to list of PiCloud servers",hidden=False) 
    
    jobCacheSize = cc.transportConfigurable('cloud_status_cache_size',
                                  default=65536,
                                  comment="Number of job statuses to hold in local memory; set to 0 to disable caching. This option only applies when connected to PiCloud.")
    
    resultCacheSize = cc.transportConfigurable('cloud_result_cache_size',
                                  default=4096,
                                  comment="Amount (in kb) of job results to hold in local memory; set to 0 to disable caching. This option only applies when connected to PiCloud.")
    
    retryAttempts = cc.transportConfigurable('retry_attempts',
                                            default =3, 
                                            comment = 'Number of times to retry requests if http error occurs',
                                            hidden=True)

    
    call_query = 'jobs/add/'
    map_query = 'jobs/map/add/'
    status_query =  'jobs/statuses/'
    result_query = 'jobs/results/'
    kill_query= 'jobs/kill/'
    delete_query= 'jobs/delete/'    
    info_query = 'jobs/info/'
    modules_add_query = 'modules/add/'
    modules_check_query = 'modules/check/'
    packages_list_query = 'packages/list/'
        
    # Most status codes are interpretted by the server
    status_accept = 200
    
    url = cc.accountConfigurable('url', default='',
                                comment="url to picloud server.  Set by server_list_url if not found",hidden=True)
    
    hostname = cc.transportConfigurable('hostname',
                                  default='',
                                  comment="Internal use only: hardcodes hostname.", hidden = True)
    
    #used to track cloud graph for webview
    parent_jid = cc.transportConfigurable('parent_jid',
                                  default=-1, #default must be an int for configs to work
                                  comment="Internal use only: Tracks cloud graph for webview", hidden = True)
    if parent_jid < 0: #flag for None.  
        parent_jid = None
    
    # mapping from jids that have errored to tracebacks
    tracebacks = None
    
    # protocol version
    # 1.0 --- xranges used to communicate
    # 1.1 --- new map uploading protocol
    # 1.2 --- GZIP individual elements
    # 1.3 --- Don't transport exception w/ status. Get through info
    version = "1.3"           
    map_size_limit = 1800000 #1.8 MB map limit    
    map_job_limit = 500 #500 map jobs maximum per request    
    jid_size_limit = 1000 #max 1,000 jids per request
               
    def __init__(self, api_key, api_secretkey, server_url=None):
        if api_key:
            self.api_key = str(api_key)
        if api_secretkey:
            self.api_secretkey = str(api_secretkey)
        if server_url:
            self.url= server_url
        if not self.hostname:
            self.hostname = str(socket.gethostname())
        self.openLock = threading.RLock()
        
        #module caching:
        self._modsInspected = set()
        self._modVersions = {}

    """Module version analysis"""
    def _getModVersions(self):
        for modname, module in sys.modules.items():
            if modname in self._modsInspected:
                continue            
            self._modsInspected.add(modname)
            if '.' in modname:  #only inspect top level
                continue            
            if hasattr(module,'__version__'):
                self._modVersions[modname] = module.__version__
        return self._modVersions            
        
        
    def open(self, force_open = False): 
        #force_open is used if this does not need an api key                           
        with self.openLock:
            if self.opened:  #ignore multiple opens
                return 
            
            if self.adapter:
                if not self.adapter.opened:
                    self.adapter.open()
                    
                self.adapter.cloud.jobCacheSize = self.jobCacheSize
                #config copy:            
                #no cache if size set to 0
                self.adapter.cloud.resultCacheSize = self.resultCacheSize*1024 \
                    if self.resultCacheSize > 0 else None  
            
            if self.api_key == 'None' and not force_open:
                cloudLog.debug('No api_key set: using dummy connection')
                self.url = ''
                return False
            
            # get list of available servers if no url
            if not self.url:
                try:
                    req = urllib2.Request(self.serverListUrl)
                    response = urllib2_file.urlopen(req)
                    lines = response.readlines()
                except Exception, e:
                    raise
                    #raise CloudException('HttpConnection.__init__: Could not get list of servers.',logger=cloudLog)
                
                # check status code of server list
                status = lines.pop(0).strip()
                if int(status) != self.status_accept:
                    raise CloudException('HttpConnection.__init__: Server list returned error',logger=cloudLog)
                
                for accesspoint in lines:
                    accesspoint = accesspoint.strip()
                    if accesspoint == '':
                        continue
                    
                    try:
                        cloudLog.debug('Trying %s' % accesspoint)
                        # see if we can connect to the server
                        req = urllib2.Request(accesspoint)                    
                        resp = urllib2_file.urlopen(req)
                        resp.read()                        
                        
                    except Exception, e:
                        pass
                    else:
                        self.url = accesspoint
                        cloudLog.info('Connected to %s' % accesspoint)
                        if req.get_type() != 'https':
                            cloudLog.warning('Connected over an insecure connection.  Be sure that openssl and python-openssl are installed')
                        break
                        
                else:
                    # if it could not establish a connection any of the listed servers
                    raise CloudException('HttpConnection.__init__: Could not find working cloud server',logger=cloudLog)
                
            #finish open
            self._isopen = True

    def connection_info(self):
        dict = CloudConnection.connection_info(self)
        dict['connection_type'] = 'HTTPS' if 'https://' in self.url else 'HTTP'
        dict['server_url'] = self.url
        dict['api_key'] = self.api_key
        dict['api_secretkey'] = self.api_secretkey
        return dict
    
    def needs_restart(self, **kwargs):
        
        api_key = kwargs.get('api_key')
        if api_key:
            if api_key != self.api_key:
                return True
        server_url = kwargs.get('server_url')
        if server_url:
            if server_url != self.url:
                return True        
        return False
    
    def post(self, url, post_values=None, headers={}, use_gzip = False):
        """
        A simple http post to the input url with the input post_values.
        """
        
        request = urllib2.Request(url, post_values, headers)
        request.use_gzip = use_gzip
        response = urllib2_file.urlopen(request)
        
        return response
    
    def rawquery(self, url, post_values=None, headers={}):
        """
        Creates an http connection to the given url with the post_values encoded.
        Returns the http response if the returned status code is > 200.
        """
        
        post_values['version'] = self.version
        num_retry = self.retryAttempts
        
        while True:
            try:
                body = None
                status = None
                
                response = self.post(url, post_values, headers)
                
                status = response.readline()
                body = response.read()
                
                response.close() #in python 2.5 not automatically done
                
                status = int(status) #in rare cases the status is invalid (e.g. <html>)
            
            except Exception, e:  #HTTP Error            
                if num_retry > 0:
                    cloudLog.warn('HttpConnection.rawquery: Could not open http connection. Retrying. \nError is %s' % str(e))
                    logfunc = cloudLog.warn    
                else:
                    cloudLog.error('HttpConnection.rawquery: http connection failed')
                    logfunc = cloudLog.error
                
                if hasattr(e, 'readlines'):
                    for r in e.readlines():
                        r = r.rstrip()
                        logfunc(r)
                if body:
                    logfunc('Specifically HTTP 200 with invalid data. Data is\n%s' % status)
                    for r in body.split('\n'):
                        logfunc(r.strip())
                        
                if num_retry > 0:
                    num_retry -= 1
                    time.sleep(1.0) #backoff for one second
                    continue
                else:                    
                    raise
                
            else:                          
                if status >  self.status_accept:  #cloud error
                    raise CloudException(body.strip(), status=status, logger=cloudLog)
                else:
                    break                 
                
        return ''.join(body)
    
    def query(self, url, post_values, logfunc = cloudLog.info):
        if self.api_key == 'None':
            raise CloudException('HttpConnection.query: api_key is not set. Please set it via cloudconf.py or calling cloud.setkey()', logger=cloudLog)
        
        if not self.opened:
            raise CloudException('HttpConnection.query: Connection is not open', logger=cloudLog)
        
        if logfunc:
            logfunc('query url %s with post_values =%s' % (url, post_values))

        # add general information
        post_values.update({
                            'api_key': self.api_key,
                            'api_secretkey': self.api_secretkey} )
        
                
        return self.rawquery(self.url + url, post_values)
    
    def is_simulated(self):
        return False
    
    def _update_params(self, params):
        params.update({'hostname': str(self.hostname),
                       'process_id': str(os.getpid()),
                       'language': 'python',
                       'language_version': sys.version
                       })
        
        #get module versions
        params['mod_versions'] = self._getModVersions()
        params['cloud_version'] = release_version
        
        #strip unicode from func_name:
        params['func_name'] = params['func_name'].decode('ascii', 'replace').encode('ascii', 'replace')        
        
    
    def job_add(self, params, logdata = None):
        
        self._update_params(params)
        
        self.adapter.depSnapShot() #let adapter make any needed calls for dep tracking
        
        data = Packer()
        
        #Store as params1, func1, args1
        data.add(serialize({'parent_jid': self.parent_jid,
                                       'depends_on': encodeMaybeXrange(params['depends_on']),
                                       'job_priority': params['job_priority'],
                                       'job_restartable': params['job_restartable'],
                                       'cpu_units': params['cpu_units'],
                                       'profile': params['profile'],
                                       'job_label': params['job_label'],
                                       'fast_serialization' : params['fast_serialization'],
                                       'kill_process' : params['kill_process'],
                                       'mod_versions' : params['mod_versions']
                                       }) )
        data.add(params['func'])
        data.add(params['args'])
        data.add(params['kwargs'])
        
        params['data'] = data.finish()       
               
        del params['func'], params['args'], params['kwargs'], params['depends_on'], \
            params['job_priority'], params['job_label'], params['job_restartable'], \
            params['cpu_units'], params['profile'], params['fast_serialization'], \
            params['kill_process'], params['mod_versions']                    
        
        resp = self.query(self.call_query, params, logfunc = cloudLog.debug)
        
        jid = deserialize(resp)['jids']
        
        cloudLog.info('call %s --> jid [%s]', params['func_name'], jid)
        
        return jid
    
    def jobs_map(self, params, mapargs, logdata = None):

        self._update_params(params)
        
        data = Packer()        
        
        data.add(serialize({'parent_jid': self.parent_jid,
                                      'depends_on': encodeMaybeXrange(params['depends_on']),
                                      'job_priority': params['job_priority'],
                                      'job_restartable': params['job_restartable'],
                                      'cpu_units': params['cpu_units'],                                
                                      'profile': params['profile'],
                                      'job_label': params['job_label'],
                                      'fast_serialization' : params['fast_serialization'],
                                      'kill_process' : params['kill_process'],                                      
                                      'mod_versions' : params['mod_versions']                                      
                                      }) )
        
        data.add(params['func'])
        size = len(params['func']) 
        
        del params['func'], params['depends_on'], params['job_priority'],\
            params['fast_serialization'], params['job_label'], params['job_restartable'],\
            params['cpu_units'], params['profile'], params['mod_versions'], params['kill_process']
        
        # done indicates to the server when the last chunk of the map is being sent
        params['done'] = False
              
        
        
        # this tells the server what the first maparg index of the current map chunk is
        # for ex. first_maparg_index=0 (first request with 4 chunks),
        #         first_maparg_index=4 (second request)
        cnt = 0
        req_item_cnt = 0
        params['first_maparg_index'] = cnt
        
        first_iteration = True
        map_is_done = False
                        
        argIter =  mapargs
        
        fname = params['func_name']
                
        while True:
            
            if size > self.map_size_limit or req_item_cnt > self.map_job_limit or map_is_done:

                self.adapter.depSnapShot() #let adapter make any needed calls for dep tracking
                params['data'] = data.finish()  #payload
                
                resp = self.query(self.map_query, params, logfunc=cloudLog.debug) #actual query
                
                resp_d = deserialize(resp)
                if not map_is_done:

                    if first_iteration:
                        # extract group_id from the response
                        group_id = resp_d['group_id']                                        
                    
                    # Reset parameters
                    params = {'group_id': group_id,
                              'done': False,
                              'first_maparg_index': cnt}
                    
                    #rebuild data object
                    data = Packer()
                    
                else:
                    break
                
                size = 0
                req_item_cnt = 0
                
                # set first iteration to false only after the first *map chunk is sent*
                first_iteration = False

            try:
                next_elm = argIter.next()
            except StopIteration:
                map_is_done = True

            if not map_is_done:
                data.add(next_elm)
                size += len(next_elm) 
                cnt += 1
                req_item_cnt += 1
            
            else:                
                params['done'] = True            
            
                
            
        #print 'done sending mapargs'
        jids = decodeMaybeXrange(resp_d['jids'])
        
        cloudLog.info('map %s --> jids [%s]', fname, jids)
        
        return jids
    
    @staticmethod
    def packJids(jids):
        packedJids = Packer()
        serialized_jids = serialize(encodeMaybeXrange(jids))
        packedJids.add(serialized_jids)
        return packedJids.finish(), serialized_jids
    
    @staticmethod
    def mergeList(lst):
        return reduce(lambda x, y: x+y, lst)
    
    def jobs_status(self, jids):
        """Returns statuses as cacheItems"""
        statuses = []
        exceptions = []
        for rjids in iterateXRangeLimit(jids,self.jid_size_limit):    
            packed_jids, serialized_jids = self.packJids(rjids)        
            cloudLog.debug('query status of jids %s' % serialized_jids) 
               
            resp = self.query(self.status_query, {'jids': packed_jids},
                                                  logfunc = None)
            result = deserialize(resp)
            
            statuses.append(result['statuses'])
    
        return self.mergeList(statuses)
        
    def jobs_result(self, jids):
        # resp is in a pseudo-multipart format with a boundary
        # separating result fields

        results = []
        for rjids in iterateXRangeLimit(jids,self.jid_size_limit):    
            
            packed_jids, serialized_jids = self.packJids(rjids)        
            cloudLog.info('query result of jids %s' % serialized_jids) 
            
            resp = self.query(self.result_query, {'jids': packed_jids}, logfunc = None)
            boundary_index = resp.index('\n')
            
            # parse boundary definition
            boundary = resp[len('boundary='):boundary_index]
            
            # separate the boundary definition from the rest of the data
            rest = resp[boundary_index+1:]
            
            # split results by boundary
            data = rest.split(boundary)
        
            # filter out empty strings
            results.append(filter(lambda datum: datum, data))
        
        return self.mergeList(results)
    
    def jobs_kill(self, jids):                
        if jids == None:
            jids= [] #server expects this
            
        for rjids in iterateXRangeLimit(jids,self.jid_size_limit):
            packed_jids, serialized_jids = self.packJids(rjids)        
            cloudLog.info('kill jids %s' % serialized_jids)             
            self.query(self.kill_query, {'jids': packed_jids}, logfunc = None)

    def jobs_delete(self, jids):
        for rjids in iterateXRangeLimit(jids,self.jid_size_limit):
            packed_jids, serialized_jids = self.packJids(rjids)        
            cloudLog.info('delete jids %s' % serialized_jids) 
            self.query(self.delete_query, {'jids':  packed_jids}, logfunc = None)        
        
    def jobs_info(self, jids, info_requested):
        infos = []
        for rjids in iterateXRangeLimit(jids,self.jid_size_limit):    
                                
            packed_jids, serialized_jids = self.packJids(rjids)        
            serialized_info = serialize(info_requested)
            cloudLog.info('get info "%s" on jids %s' % (serialized_info, serialized_jids)) 
                    
            resp = self.query(self.info_query, {'jids':  packed_jids,
                                                'inforequest': serialized_info,
                                                },logfunc = None)
            
            infos.append( unicode_container_to_str(deserialize(resp)['info']) )
                
        return self.mergeList(infos)
    
    def modules_check(self, modules):
        """
        modules_check determines which modules must be sent from the client
        to the server.
        modules: list of tuples where each tuple is (filename, timestamp)
        
        Returns a list of filenames to send.
        """
        
        packedMods = Packer()
        packedMods.add(serialize(modules))      
        data = packedMods.finish()

        resp = self.query(self.modules_check_query, {'data': data,
                                                     'hostname': str(self.hostname),
                                                     'language': 'python'
                                                     })        
        mods = deserialize(resp)['modules']
        
        return mods
    
    def modules_add(self, modules, modules_tarball):
        """
        modules_add adds the specified modules to the picloud system.
        modules is a list of tuples, where each tuple is (name, timestamp).
        modules_tarball is a string representing the tarball of all the included modules.
        """
        packedMods = Packer()
        packedMods.add(serialize(modules))
        packedMods.add(modules_tarball)        
        data = packedMods.finish()

        resp = self.query(self.modules_add_query, {'data': data,
                                                   'hostname': str(self.hostname),
                                                   'language': 'python'
                                                   })
        
    def packages_list(self):
        """
        Get list of packages from server
        """
        resp = self.query(self.packages_list_query, {'language': 'python' })
        
        pkgs = deserialize(resp)['packages']
        
        # convert from unicode to ascii
        return map(str, pkgs)
    
    def report_name(self):
        return 'HTTPConnection'
        
    