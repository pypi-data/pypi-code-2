"""
Defines all Cloud Adapters - objects that control lower-level behavior of the cloud
There is a one to one instance mapping between a cloud and its adapter

Copyright (c) 2009 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

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

import sys
import time
import types
import threading
from functools import partial
from itertools import izip, imap, count

from ..cloud import CloudException
from .. import serialization
from .. import cloudconfig as cc
from ..cloudlog import cloudLog
from ..util import OrderedDict


class Adapter(object):
    """
    Abstract class to deal with lower-level cloud operations
    """
          
    _isopen = False
    
    @property
    def opened(self): 
        """Returns whether the adapter is open"""
        return self._isopen
    
    def open(self):
        """called when this adapter is to be used"""
        if self.opened:
            raise CloudException("%s: Cannot open already-opened Adapter", str(self))
        if not self._cloud.opened:
            self._cloud.open()
    
    def close(self):
        """called when this adapter is no longer needed"""
        if not self.opened:
            raise CloudException("%s: Cannot close a closed adapter", str(self))
        self._isopen = False
        
    @property
    def cloud(self):
        return self._cloud
    
    def needs_restart(self, **kwargs):
        """Called to determine if the cloud must be restarted due to different adapter parameters"""
        return False
        
    def call(self, params, func, *args):
        raise NotImplementedError
    
    def jobs_join(self, jids, timeout = None):
        """
        Allows connection to manage joining
        If connection manages joining, it should return a list of statuses and a list of exceptions  
        describing the finished job
        Else, return False, False
        """
        return False, False
    
    def jobs_map(self, params, func, argList):
        """Treat each element of argList as func(*element)"""
        raise NotImplementedError
    
    def jobs_status(self, jids):
        raise NotImplementedError
    
    def jobs_result(self, jids):
        raise NotImplementedError

    def jobs_kill(self, jids):
        raise NotImplementedError
    
    def jobs_delete(self, jids):
        raise NotImplementedError    
    
    def jobs_info(self, jids, info_requested):
        raise NotImplementedError
    
    def is_simulated(self):        
        raise NotImplementedError
    
    def connection_info(self):
        return self.connection.connection_info()
        

"""
TheSerializingAdapter is responsible for serializing data passed into args
It then passes data onto its CloudConnection handler
It can (optionally) log serializations
"""

class SerializingAdapter(Adapter):
    
    #config for pickle debugging        
    c = """Should serialization routines track debugging information?
    If this is on, picklingexceptions will provide a 'pickle trace' that identifies what member of an object cannot be pickled"""
    serializeDebugging =  \
        cc.loggingConfigurable('serialize_debugging',
                                          default=True,
                                          comment=c, hidden=True)
    c = """Should all object serialization meta-data be logged to the serialize_logging_path?""" 
    serializeLogging = \
        cc.loggingConfigurable('serialize_logging',
                                          default=False,
                                          comment=c)      
    if serializeLogging and not serializeDebugging:
        serializeDebugging = True
        cloudLog.warning("serialize_logging implies serialize_debugging. Setting serialize_debugging to true.")
    
    
    c = """Maximum amount of data (in bytes) that can be sent to the PiCloud server per function or function argument"""
    maxTransmitData = \
        cc.transportConfigurable('max_transmit_data',
                                  default=1000000,
                                  comment=c)
        
    
    
    #live:
    _report = None  
    _isSlave = False #True if this adapter is a slave (it's connection is in a master process)
                  
        
    def __init__(self, connection, isSlave = False):
        self.connection = connection 
        connection._adapter = self
        self.opening = False
        self.openLock = threading.RLock()            
        self._isSlave = isSlave
        
    def initReport(self, subdir = ""):
        try:
            self._report = serialization.SerializationReport(subdir)
        except IOError, e:
            cloudLog.warn('Cannot construct serialization report directory. Error is %s' % str(e))
            self._report = None
            self.serializeLogging = False #disable logging
        
    @property
    def report(self):
        return self._report
    
    @property
    def isSlave(self):
        return self._isSlave

    def _configureLogging(self):
        #Seperated from open to allow for dynamic changes at runtime
        
        #set up cloud serializer object
        self.min_size_to_save =  0 if self.serializeLogging else (self.maxTransmitData / 3)   
        #reporting:                
        if not self._report:
            if self.serializeLogging or self.connection.force_adapter_report():
                if self._isSlave:
                    self.initReport()
                    self._report.logPath = self.connection.getReportDir() 
                else:
                    self.initReport(self.connection.report_name())            
            else:
                self._report = None  

    def getSerializer(self, serialization_level = 0):
        """Return the correct serializer based on user settings and serialization_level"""
        if serialization_level >= 2:
            return serialization.Serializer
        elif self.serializeDebugging and serialization_level == 0:
            return serialization.DebugSerializer
        else:
            return serialization.CloudSerializer        
        
    
    def open(self):      
        with self.openLock:
            if self._isopen or self.opening:
                return

            self.opening = True
            Adapter.open(self)  
                                                
            try:                 
                #always try to open               
                if self._isSlave:  
                    #must open connection first to get reportDir                  
                    self.connection.open()
                    self._configureLogging()
                else:
                    self._configureLogging()
                    self.connection.open()
            finally:
                self.opening = False        
                        
            self._isopen = True
        
        
                 
    def close(self):
        Adapter.close(self)
        if hasattr(self.connection, 'opened') and self.connection.opened:
            self.connection.close()        

    def checkSize(self, serializerInst, logfilename):
        """Check if transmission size exceeds limit"""
        totalsize = len(serializerInst.serializedObject)
        if totalsize > self.maxTransmitData:
            exmessage = 'Excessive data (%i bytes) transmitted.  See help at %s' % (totalsize, 'http://docs.picloud.com')
            if self.serializeDebugging:
                exmessage += ' Snapshot of what you attempted to send:\n'
                serializerInst.setReportMinSize(totalsize/3)
                exmessage += serializerInst.strDebugReport(hideHeader=True)
            else:
                exmessage += '\n To see data snapshots, enable serialize_debugging in cloudconf.py\n'
            exmessage += 'Cloud has produced this error as you are sending too large of an object.\n'
            exmessage += 'The above snapshot describes the data that must be transmitted to execute your PiCloud call.\n'
            if cc.transportConfigurable('running_on_cloud',default=False):
                exmessage += 'You cannot send more than 100 mb via cloud.call/map'
            else:
                exmessage += 'If you decide that you actually need to send this much data, increase max_transmit_data in cloudconf.py\n'
             
            if logfilename:
                exmessage+= 'See entire serialization snapshot at ' + logfilename
            elif not self.cloud.running_on_cloud():
                exmessage+='Please enable serialize_logging in cloudconf.py to see more detail'
            raise CloudException(exmessage)
    
    def _cloudSerializeHelper(self, func, arg_serialization_level, args, argnames=[], logprefix=""):
        """Returns a serialization stream which produces a serialized function, then its arguments in order
        Also returns name of logfile and any counter associated with it"""
        baselogname =  logprefix

        if isinstance(func,partial):
            f = func.func
        else:
            f = func

        if hasattr(f,'__module__'):            
            baselogname+=(f.__module__ if f.__module__ else '__main__') +'.'
        if hasattr(f,'__name__'):
            baselogname+=f.__name__        
        
        acname = None                
      
        sargs = []
        
        cnt = self._report.updateCounter(baselogname) if self._report else 0

        def generate_stream():
            """Helper generator that produces the stream"""
            #serialize function:
            sfunc = self.getSerializer(0)(func)
            try:
                sfunc.runSerialization(self.min_size_to_save)
            finally:        
                if self.serializeLogging:
                    logname = baselogname + '.%sfunc'
                    acname = self._report.saveReport(sfunc, logname, cnt)
                else:
                    acname = ""  
            
            self.checkSize(sfunc,acname) 
            yield sfunc
            
            #arguments
            argSerializer = self.getSerializer(arg_serialization_level)
            for obj, name in izip(args, argnames):
                #TODO: Policy change here
                serializerI = argSerializer(obj)
            
                try:
                    serializerI.runSerialization(self.min_size_to_save)
                finally:
                    if self.serializeLogging:                        
                        logname = baselogname + '.%s' + name
                        acname = self._report.saveReport(serializerI, logname, cnt)  
            
                self.checkSize(serializerI,acname) 
            
                yield serializerI                                        
        return generate_stream(), baselogname, cnt

        
    
    def cloudSerialize(self, func, arg_serialization_level, args, argnames=[], logprefix=""):
        """Return serialized_func, list of serialized_args
        Will save func and args to files.
        """
        serialize_stream, baselogname, cnt = self._cloudSerializeHelper(func, arg_serialization_level, args, argnames, logprefix)
        sfunc = serialize_stream.next().serializedObject        
        sargs = imap(lambda sarg: sarg.serializedObject, serialize_stream) #stream
                
        return sfunc, sargs, baselogname, cnt

    
    def job_call(self, params, func, args, kwargs):
        sfunc, sargs, logprefix, logcnt =  self.cloudSerialize(func, params['fast_serialization'], [args, kwargs], ['args', 'kwargs'], 'call.') 
        
        params['func'] = sfunc
        params['args'] = sargs.next()
        params['kwargs'] = sargs.next()

        return self.connection.job_add(params=params, logdata = (logprefix, self._report.pid if self._report else 0, logcnt))
    
    def jobs_join(self, jids, timeout = None):
        return self.connection.jobs_join(jids, timeout)
    
    def jobs_map(self, params, func, mapargs):
        """Treat each element of argList as func(*element)"""
        
        mapargnames = imap(lambda x: 'jobarg_' + str(x),count(1)) #infinite stream generates jobarg_ for logging                
        
        sfunc, sargs, logprefix, logcnt =  self.cloudSerialize(func, params['fast_serialization'], mapargs, mapargnames, 'map.')

        params['func'] = sfunc
        
        if self.isSlave: #fixme: Find a way to pass stream through to master
            sargs = list(sargs)
            
        return self.connection.jobs_map(params=params, mapargs = sargs,   
                                       logdata = (logprefix, self._report.pid if self._report else 1, logcnt))
        
    def jobs_status(self, jids):
        #statuses, exceptions
        return  self.connection.jobs_status(jids=jids)        
    
    def jobs_result(self, jids):
        """Returns serialized result; higher level deals with it"""
        return self.connection.jobs_result(jids=jids)
    
    def jobs_kill(self, jids):
        return self.connection.jobs_kill(jids=jids)
    
    def jobs_delete(self, jids):
        return self.connection.jobs_delete(jids=jids)        
    
    def jobs_info(self, jids, info_requested):
        return self.connection.jobs_info(jids=jids, info_requested=info_requested)
   
    def is_simulated(self):        
        return self.connection.is_simulated()
    
    def needs_restart(self, **kwargs):        
        return self.connection.needs_restart(**kwargs)

class DependencyAdapter(SerializingAdapter):
    """
    The DependencyAdapter is a SerializingAdapter capable of sending modules
    to PiCloud
    """
    

    # manages file dependencies:
    dependencyManager = None


    c = """Should a more aggressive, less optimal, module dependency analysis be used?  This is always used on stdin"""
    aggressiveModuleSearch = \
        cc.transportConfigurable('aggressive_module_search',default=False,comment=c, hidden=True)

    def _checkForcedMods(self):
        """find things that may be imported via import a.b at commandline
        Set __main__.___pyc_forcedImports__ to that list
        """
        marked = set()        
        main = (sys.modules['__main__'])  
        marked.add(main)        
        def recurse(testmod, name): #name is tuple version of testmod
            for key, val in testmod.__dict__.items():                
                if not name: #inspecting main module -- use val name
                    if isinstance(val,types.ModuleType):
                        item = val.__name__
                        if item in ['cloud','__builtin__']:
                            continue
                        tst = tuple(item.split('.'))
                        
                    else:
                        continue
                else: #child module cannot be renamed inside a parent
                    item = key
                    tst = name + (item,) 
                if item in marked: 
                    continue                
                tstp = '.'.join(tst)                
                themod = sys.modules.get(tstp)
                if not themod:
                    continue          
                self.dependencyManager.inject_module(themod)  
                marked.add(item)
                if len(tst) > 1: #this is a forced import:
                    if not hasattr(main,'___pyc_forcedImports__'):
                        main.___pyc_forcedImports__ = set()
                    main.___pyc_forcedImports__.add(themod)
                recurse(themod,tst)                                    
        with self.modDepLock:
            recurse(main,tuple())                

    
    def _argHandler(self, sarg):
        """Used by cloudSerialize imap on serialized args"""
        with self.modDepLock:
            for moddep in sarg.getModuleDependencies():
                self.dependencyManager.inject_module(moddep)
        return sarg.serializedObject
        
    
    def cloudSerialize(self, func, arg_serialization_level, args, argnames=[], logprefix=""):
        """
        Similar to the normal cloudSerialize, except tracks dependencies
        """               
        main = (sys.modules['__main__'])
        if serialization.cloudpickle.useForcedImports and \
            (self.aggressiveModuleSearch or not hasattr(main,'__file__')):
            self._checkForcedMods()      

        #No need to track dependencies on cloud:
        if self._cloud.running_on_cloud():
            return SerializingAdapter.cloudSerialize(self, func, arg_serialization_level, args, argnames, logprefix)   
        
        serialize_stream, baselogname, cnt = self._cloudSerializeHelper(func, arg_serialization_level, args, argnames, logprefix)
        outargs = []
        
        sfunc = serialize_stream.next()
        outfunc = self._argHandler(sfunc)
                    
        outargs = imap(lambda sarg: self._argHandler(sarg), serialize_stream)

        return outfunc, outargs, baselogname, cnt

    def depSnapShot(self):
        """This function, called downstream from the network connection object, 
        deals with calling the dependency checking functions
        Note that it can be called in between successive maps"""
        deps =  self.dependencyManager.getUpdatedSnapshot()
        
        if deps:
            cloudLog.debug('New Dependencies %s' % str(deps))
            #modules are a tuple of (modname, timestamp, archvie)
            modules = self.connection.modules_check(deps)
            if modules:
                from ..transport.codedependency import FilePackager
                f = FilePackager(map(lambda module: (module[0], module[2]), modules))
                tarball = f.getTarball()
                cloudLog.info('FileTransfer: Transferring %s' % modules)
                self.connection.modules_add(modules, tarball)        
    
    def open(self):                
        with self.openLock:
            if self.opening or self.opened:
                return        
            SerializingAdapter.open(self)
            self._isopen = False
                                
            from ..transport import DependencyManager
            ignoreList = self.connection.packages_list()
            self.dependencyManager = DependencyManager(excludes=ignoreList,debug = 0)
            self.modDepLock = threading.Lock()
            
            self._isopen = True

                    