"""
Top-level object for PiCloud
Manages caching and client-side type checking
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
 
import sys
import threading
import time
import pickle
import collections
import weakref
try:
    from itertools import izip_longest
except ImportError: #python 2.5 lacks izip_longest
    from .util import izip_longest 

from . import cloudconfig as cc
from .cloudlog import cloudLog
from . import serialization

from .util import funcname
from .util.cache import JobCacheManager, JobFiniteDoubleCacheManager, \
    JobFiniteSizeCacheManager, JobAbstractCacheManager
from .util.xrange_helper import filterXrangeList, maybeXrangeIter


# set by the instantiation of a Cloud object
_cloud = None

class CloudException(Exception):
    """
    Represents an exception that has occurred by a job on the cloud.
    CloudException will display the job id for failed cloud requests.
    """
    
    status = None
    jid = None
    parameter = None
    
    def __init__(self, value, jid=None, status=None, logger = cloudLog):
        self.jid = jid
        self.parameter = value
        self.status = status
        if logger:
            self._logmsg(logger)
        
    def __str__(self):
        if self.jid is not None:
            return 'Job ' + str(self.jid) + ': ' + str(self.parameter)
        elif self.status is not None:
            return 'Status ' + str(self.status) + ': ' + str(self.parameter)
        else:
            return str(self.parameter)      

    def _logmsg(self, logger):
        """logmsg - only log on jid related"""
        if self.jid is not None:
            logger.warning(''.join(['Job ',str(self.jid),' threw exception:\n ', str(self.parameter)]))
            
class CloudTimeoutError(CloudException):
    """CloudException specifically for join timeouts"""
    
    def __init__(self, value = 'Timed out', jid=None, logger = cloudLog):
        CloudException.__init__(self, value, jid, None, logger)
    
    
    def _logmsg(self, logger):
        """logmsg - only log on jid related"""
        if self.jid is not None:
            logger.warning(''.join(['Job ',str(self.jid),' %s\n ' % self.parameter ]))

def _getExceptionMsg(status):
    """Return exception method associated with a status"""
    if status == 'killed':
        return 'Killed'
    elif status == 'stalled':
        return 'Could not start due to dependency erroring'
    else:
        return 'unknown error'      

class FakeException(Exception):
    pass

#_catchCloudException = CloudException
_catchCloudException = FakeException
_docmsgpkl = "\nPlease see PiCloud documentation for more information about pickle errors"

class Cloud(object):
    """
    Top-level object that manages client-side type checking and client-side cache for Cloud  
    """
       
    jobCacheSize = 8191 #cache size for cache manager. None = no cache; 0 = no limit
    resultCacheSize = 4096 #cache size for results (applies only if limited jobCache) in bytes; None = no cache; 0 = no limit
    
    finished_statuses = ['done', 'stalled', 'error', 'killed']
    
    # process locally or over network via http
    adapter = None
    
    # manages callbacks
    manager = None
    
    #manages job caching
    cacheManager = None

    __isopen = False
    
    openLock = None
    
    parentModule = None #string representation of module this object is placed in (if any)
    
    __running_on_cloud = cc.transportConfigurable('running_on_cloud', default=False, 
                                        comment="Internal. States if running on PiCloud",
                                        hidden = True) 
        
    @property
    def opened(self): 
        """Returns whether the cloud is open"""
        return self.__isopen
    
    def running_on_cloud(self):  #high level check
        """
        Returns true iff current thread of execution is running on PiCloud servers.
        """
        
        return self.__running_on_cloud
           
    def __init__(self, adapter):
        self.adapter = adapter
        adapter._cloud = self
        self.openLock = threading.RLock()
        self._opening = False
    
    def open (self):
        """Enable the cloud"""
        
        with self.openLock:
            
            if self.opened: #accept this for threading issues
                return                
            
            #hackish re-entry check -- due to issues with local adapter opening this           
            if self._opening:
                return

            try:
                self._opening = True
                if not self.adapter.opened:
                    self.adapter.open()                    
            except _catchCloudException, e:
                raise e
            finally:
                self._opening = False
    
            self.manager = CloudTicketManager(self)
            self.manager.start() 
            
            if self.jobCacheSize == None: #no cache
                self.cacheManager = JobAbstractCacheManager()
            elif self.jobCacheSize == 0: #no limit on cache
                self.cacheManager = JobCacheManager()            
            else:
                if self.resultCacheSize == None:  #no cache
                    resultCacheSize = 0
                elif self.resultCacheSize == 0:  #effectively no limit on cache
                    resultCacheSize = sys.maxint
                else:                           #default
                    resultCacheSize = self.resultCacheSize
                
                childManager = JobFiniteSizeCacheManager(resultCacheSize,'result')             
                self.cacheManager = JobFiniteDoubleCacheManager(self.jobCacheSize, childManager)
                 
            self.__isopen = True
            if not self.adapter.isSlave:
                cloudLog.info('Cloud started with adapter =%s', str(self.adapter))  
    
    
    def close(self):
        """
        Shutdown cloud
        """    
        if not self.opened:
            raise CloudException('%s: Cannot close a closed Cloud' % str(self))                   
        if self.adapter.opened:
            self.adapter.close()    
        self.manager.stop()
        cloudLog.info('Cloud closed with adapter =%s', str(self.adapter))
        self.__isopen = False                
    
    def _checkOpen(self):
        """Open cloud if it is not already"""
        if not self.opened:
            self.open()
    
    def is_simulated(self):
        """
        Returns true iff cloud processor is being run on the local machine.
        """        
        return self.adapter.is_simulated() 
    
    def connection_info(self):
        """
        Returns a dictionary of information describing the current connection.
        """
        return self.adapter.connection_info()

    
    def needs_restart(self, **kwargs):        
        """
        For internal use
        Return true if cloud requires restart based on changed params
        """
        return self.adapter.needs_restart(**kwargs)
    
    def _getJobParameters(self, func, mappings, ignore=[]):
        """Return parameters from function and mappings
        Removes keys from mappings handled by this function
        Ignores keys in ignore[]"""
        
        # defaults
        job_label = None
        job_priority = 5
        job_restartable = True
        cpu_units = 1.0
        profile = False
        depends_on = []
        fast_serialization = 0
        kill_process = False #not documented yet
        
        if '_label' in mappings and '_label' not in ignore:
            #job_label must be an ASCII string
            try:
                job_label = mappings['_label'].decode('ascii').encode('ascii')
            except (UnicodeDecodeError, UnicodeEncodeError):
                raise TypeError('_job_label must be an ASCII string')
            del mappings['_label']
        
        if '_priority' in mappings and '_priority' not in ignore:
            job_priority = mappings['_priority']
            if not isinstance(job_priority, (int, long)):
                raise TypeError(' _priority must be an integer')             
            del mappings['_priority']

        if '_restartable' in mappings and '_restartable' not in ignore:
            job_restartable = mappings['_restartable']
            if not isinstance(job_restartable, bool):
                raise TypeError(' _job_restartable must be boolean')             
            del mappings['_restartable']
        
        if '_depends_on' in mappings and '_depends_on' not in ignore:
            if hasattr(mappings['_depends_on'],'__iter__'):
                depends_on = mappings['_depends_on']
            elif isinstance (mappings['_depends_on'], (int,long)):
                depends_on = [mappings['_depends_on']]
            else:
                raise TypeError('_depends_on must be a jid or list of jids')
            del mappings['_depends_on']
            
            # convert CloudPromises to jids
            if not isinstance(depends_on, xrange):
                test = reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), depends_on, True)
                if not test:
                    raise TypeError( '_depends_on list can only contain jids' )
        
        if '_fast_serialization' in mappings  and '_fast_serialization' not in ignore:
            fast_serialization = mappings['_fast_serialization']
            if not isinstance(fast_serialization, (int, long)):
                raise TypeError(' _fast_serialization must be an integer')                        
            del mappings['_fast_serialization']    
        
        if '_high_cpu' in mappings  and '_high_cpu' not in ignore:
            if mappings['_high_cpu']:
                cpu_units = 2.5
            del mappings['_high_cpu']
            
        if '_profile' in mappings and  '_profile' not in ignore:
            profile = bool( mappings['_profile'])
            del mappings['_profile']
            
        if '_kill_process' in mappings and '_kill_process' not in ignore:
            kill_process = bool( mappings['_kill_process'])
            del mappings['_kill_process']

        
        parameters = {'fast_serialization': fast_serialization,
                      'func_name': funcname(func),
                      'job_label': job_label,
                      'job_priority': job_priority,
                      'job_restartable': job_restartable,
                      'cpu_units': cpu_units,
                      'profile': profile,
                      'depends_on': depends_on,
                      'kill_process' : kill_process
                      }
        
        for ig_key in ignore:
            if ig_key in parameters:
                del parameters[ig_key]
        
        return parameters
    
    def call(self, func, *args, **kwargs):
        """       
        Invoke *func* (a callable) in the cloud.
        When invoked, *func* will be invoked on PiCloud's cluster with the passed 
        *args* that follow it.  The invoked function is known as a 'job'.  The
        return value of the invoked function is known as the 'internal result'.

        Call will return an integer Job IDentifier (jid) which can be passed into 
        the status and result methods to obtain the status of the job and the 
        internal result respectively.
        
        Example::    
        
            def mult3(x):
                return 3*x
            cloud.call(mult3, 2) 
        
        This will cause mult3 to be invoked on PiCloud's cluster with x=2
        
        See online documentation for additional information.
        
        Reserved special *kwargs* (see docs for details):
            
        * _callback: 
                A list of functions that should be run on the callee's computer once
                this job finishes successfully.
        * _callback_on_error:  
                A list of functions that should be run on the callee's computer if this
                job errors.  
        * _depends_on:
                An iterable of jids that represents all jobs that must complete successfully 
                before the job created by this call function may be run.
        * _fast_serialization:
            This keyword can be used to speed up serialization, at the cost of some functionality.
            This affects the serialization of both the arguments and return values
            *func* will always be serialized by the enhanced serializer, with debugging features.
            Possible values keyword are:
                        
            0. default -- use cloud module's enhanced serialization and debugging info            
            1. no debug -- Disable all debugging features for arguments            
            2. use cPickle -- Use Python's fast serializer, possibly causing PicklingErrors                
                    
        * _high_cpu:
                Set this to true to run your job on a faster processor. Additional charges apply.
        * _kill_process:
                Terminate the Python interpreter *func* runs in after *func* completes, preventing
                the interpreter from being used by subsequent jobs.  See Technical Overview for more info.                
        * _label: 
                A user-defined string label that is attached to the job. Labels can be
                used to filter when viewing jobs interactively (i.e. on the PiCloud 
                website).
    	* _profile:
    	        Set this to True to enable profiling of your code. Profiling information is 
    	        valuable for debugging, but may slow down your job.
        * _restartable:
                In the very rare event of hardware failure, this flag indicates that the job
                can be restarted if the failure happened in the middle of the job.
                By default, this is true. This should be unset if the job has external state
                (e.g. it modifies a database entry)                   
        """            
        
        self._checkOpen()

        if not callable(func):
            raise TypeError( 'cloud.call first argument (%s) is not callable'  % (str(func) ))
        
        parameters = self._getJobParameters(func, kwargs)
        
        if '_callback' in kwargs:
            callback = kwargs['_callback']
            del kwargs['_callback']
        else:
            callback = None
            
        if '_callback_on_error' in kwargs:
            callback_on_error = kwargs['_callback_on_error']        
            del kwargs['_callback_on_error']
        else:
            callback_on_error = None        
        
        try:
            jid = self.adapter.job_call(parameters,func,args,kwargs)
        except _catchCloudException, e:
            raise e    
        except pickle.PicklingError, e:            
            e.args = (e.args[0] + _docmsgpkl,)            
            raise e
              
        # only add ticket to manager (will poll to see whether job has
        # finished) if there is a callback assigned to the call
        if callback:            
            self.manager.add_callbacks(jid, callback, 'success')
        if callback_on_error:
            self.manager.add_callbacks(jid, callback_on_error, 'error')        

        return jid    
    
    def join(self, jids, timeout = None, ignore_errors = False):
        """
        Block current thread of execution until the job specified by the integer *jids*
        completes.  Completion is defined as the job finishing or erroring
        (including stalling).          
        If the job errored, a CloudException detailing the exception that triggered
        the error is thrown. If multiple errors occur, it is undefined which job's exception
        will be raised.
        If the job does not exist, a CloudException is thrown.
        
        This method also accepts an iterable describing *jids* and blocks until all
        corresponding jobs finish. If an error is seen, join may terminate before 
        all jobs finish.
        
        If *timeout* is set to a number, join will raise a CloudTimeoutError if the
        job is still running after *timeout* seconds
        
        If *ignore_errors* is True, no CloudException will be thrown if a job errored.
        Join will block until every job is complete, regardless of error status.
        """
        
        #TODO: Use cloud ticket manager with this
        poll_interval = 1.0
        
        self._checkOpen()
                
        if not hasattr(jids,'__iter__'):
            jids = [jids] 
        
        if not isinstance(jids, xrange):
            if not reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True):
                raise TypeError( 'cloud.join requires numeric jid(s)' )                        
        
        #variables filter can modify:
        #NOTE: With Python3, they can just be nonlocal
        #Some of this code is legacy
        class FilterSideEffects:
            isDone = True           #if jobs are all done up to the job we are reading
            seenException = False   #if an exception has been seen
            aptr = 0                #Pointer into returned statuses/exceptions            
        
        def filterJob(jid, status):
            """Helper function to filter out jobs and fire exceptions if needed                
            """                        
            if status != 'done': 
                if status in self.finished_statuses:
                    if ignore_errors:
                        return False
                    exception = self.info(jid,'exception')[jid]['exception'] 
                    if status == 'error' or (status == 'killed' and exception):
                        raise CloudException(exception, jid=jid, status=status)
                    else:
                        msg = _getExceptionMsg(status)
                        raise CloudException(msg, jid=jid, status=status)  
                return True  #keep iterating
            return False            
       
        cachedStatuses, = self.cacheManager.getCached(jids, ('status',))
       
        def cacheJobFilter(jid):
            """Filter out cached jobs"""
            status = cachedStatuses.get(jid)
            if status:
                return filterJob(jid, status)
            else: #job not in cache
                return True  
        
        neededJids = filterXrangeList(cacheJobFilter,jids)
        #print 'needed=%s, base=%s' % (neededJids, jids)

        time_ctr = 0
        while True:
            
            if neededJids:
                try:
                    astatuses = self.adapter.jobs_join(neededJids, timeout)
                    if astatuses is False: #adapter does not support jobs_join:
                        astatuses = self.adapter.jobs_status(jids=neededJids)
                except _catchCloudException, e:
                    raise e                             
            else:
                break 
            
            fse = FilterSideEffects()
                        
            def resultFilter(jid):
                """Filter out and cache jobs we got the status for
                """            
                status = astatuses[fse.aptr]
                fse.aptr += 1
                
                if not filterJob(jid, status): #this can raise exceptions
                    #job is done!
                    self.cacheManager.putCached(jid, status=status)
                    return False
                return True            
            
            neededJids = filterXrangeList(resultFilter, neededJids)            
            
            if not neededJids:
                break

            if timeout and time_ctr > timeout:
                raise CloudTimeoutError('cloud.join timed out', neededJids)
            
            time.sleep(poll_interval) #poll
            time_ctr+= poll_interval
            
    def status(self, jids):
        """
        Returns the status of the job specified by the integer *jids*. If 
        the job does not exist, a CloudException is thrown.
        This method also accepts an iterable describing *jids*, in which case a respective list
        of statuses is returned.
        """
        self._checkOpen()        
        
        deseq = False
        if not hasattr(jids,'__iter__'):
            jids = [jids]
            deseq = True

        if not isinstance(jids, xrange):
            if not reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True):
                raise TypeError( 'cloud.status requires numeric jid(s)' )
        
        cachedStatuses,  = self.cacheManager.getCached(jids, ('status',))
        
        neededJids = filterXrangeList(lambda jid: jid not in cachedStatuses,jids)
        
        if neededJids:
            try:
                astatuses = self.adapter.jobs_status(jids=neededJids)
            except _catchCloudException, e:
                raise e                                           
            
            cnt = 0
            for neededJid in maybeXrangeIter(neededJids):
                if astatuses[cnt] in self.finished_statuses:
                    self.cacheManager.putCached(neededJid, status=astatuses[cnt])
                cnt+=1                                
        else:
            astatuses = []

        aptr = 0
        outstatuses = []
        for jid in maybeXrangeIter(jids):       
            status = cachedStatuses.get(jid)
            if not status:  
                status = astatuses[aptr]
                aptr+=1
            
            outstatuses.append(status)
      
        if deseq:
            return outstatuses[0]
        else:
            return outstatuses
        
    def result(self, jids, timeout = None, ignore_errors = False):
        """
        Blocks until the job specified by the integer *jids* has completed and
        then returns the internal result of the job.         
        If the job errored, a CloudException detailing the exception that triggered
        the error is thrown. 
        If the job does not exist, a CloudException is thrown.        

        This function also accepts an iterable describing *jids*, in which case a respective list
        of internal results is returned
        
        If *timeout* is set to a number, result will raise a CloudTimeoutError if the
        job is still running after *timeout* seconds
        
        If *ignore_errors* is True, a job that errored will not raise an exception.
        Instead, its return value is the CloudException describing the error.
        """

        deseq = False
        if not hasattr(jids,'__iter__'):
            jids = [jids]
            deseq = True
            
        if not isinstance(jids, xrange):
            test = reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True)
            if not test:
                raise TypeError( 'cloud.result(s) requires numeric jid(s)' )
            
        self._checkOpen()
        
        try:
            statuses = self.join(jids, timeout = timeout, ignore_errors=ignore_errors)  # wait for jids to be ready
        except _catchCloudException, e:
            raise e            
        #everything is now cached AND done
        
        cachedResults,  = self.cacheManager.getCached(jids, ('result',))
        neededJids = filterXrangeList(lambda jid: jid not in cachedResults,jids)
        
        jid_exceptions = {}
        if ignore_errors:
            #as ignore_errors is a rarely used flag, this block is not fully optimized                        
            statuses = self.status(jids)
            exceptions_dct = self.info(jids, 'exception')
                         
            for jid, status in izip_longest(jids, statuses):
                if status != 'done':
                    exception = exceptions_dct[jid]['exception']
                    if not exception:
                        exception = _getExceptionMsg(status)
                    jid_exceptions[jid] = (status, exception)
            neededJids = filterXrangeList(lambda jid: jid not in jid_exceptions, jids)                 
        
        if neededJids:
            try:                
                aresults = self.adapter.jobs_result(jids=neededJids)
            except _catchCloudException, e:
                raise e                                           
            
            cnt = 0
            
            for neededJid in maybeXrangeIter(neededJids):            
                self.cacheManager.putCached(neededJid, status='done', result=aresults[cnt])
                cnt+=1                                
        else:
            aresults = []

        aptr = 0
        outresults = []
        for jid in maybeXrangeIter(jids):
            if cachedResults.has_key(jid):            
                result = cachedResults.get(jid)
            elif jid_exceptions.has_key(jid):
                status, exception = jid_exceptions.get(jid)
                clexp = CloudException(exception, jid=jid, status=status, logger=None)                
                outresults.append(clexp)
                continue
            else:
                result = aresults[aptr]
                aptr+=1
            #what is returned must be deserialized:
            outresults.append(serialization.deserialize(result))
      
        if deseq:
            return outresults[0]
        else:
            return outresults 

    def iresult(self, jids, timeout = None, num_in_parallel=10, ignore_errors = False):
        """
        Similar to result, but returns an iterator that iterates, in order, through  
        the internal results of *jids* as the respective job finishes, allowing quicker 
        access to results and reducing memory requirements of result reading.
        
        If a job being iterated over errors, an exception is raised. 
        However, the iterator does not exhaust; if the exception is caught, one can continue
        iterating over the remaining jobs.
        
        If *timeout* is set to a number, a call to the iterator's next function 
        will raise a CloudTimeoutError after *timeout* seconds if no result becomes available.
        
        *num_in_parallel* controls how many results are read-ahead from the cloud
        Set this to 0 to use the allowed maximum.
        
        If *ignore_errors* is True, a job that errored will return the CloudException describing 
        its error, rather than raising an Exception        
        """
        if not hasattr(jids,'__iter__'):
            jids = [jids]
            
        if not isinstance(jids, xrange):
            test = reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True)
            if not test:
                raise TypeError( 'cloud.iresult requires numeric jid(s)' )
        
        max_in_parallel = 1024
        if num_in_parallel < 1 or num_in_parallel > max_in_parallel:
            num_in_parallel = max_in_parallel
        
        self._checkOpen()
                            
        ready_results = collections.deque()  #queue of results
        result_cv = threading.Condition()  #both main and loop threads sleep on this
        errorJid = []  #1st element set to a job if an error is to be returned
        isDone = [] #1st element set to 'done' when result_loop finishes
        
        def result_loop(iterator_ref):
            """
            Helper function run inside another thread
            It downloads results as the main thread continues work
            
            Slight issue is present in that if the condition variable is not necessarily
            waited on if an error is present in the ready_results buffer
            """
            jidIterator = maybeXrangeIter(jids)
            jids_testing = collections.deque()   #queue of jobs being tested            
            
            while self.__isopen:                
                #First add jobs to check
                try:
                    while len(jids_testing) < num_in_parallel:
                        jids_testing.append(jidIterator.next())
                except StopIteration:
                    if not jids_testing:  #loop is done!
                        cloudLog.debug('cloud.iresult.result_loop has completed')
                        isDone.append(True)
                        break 
                
                with result_cv:
                    while True:
                        if not iterator_ref(): #GC Detection on iterator removal
                            break
                        
                        if (len(ready_results) < num_in_parallel and not errorJid):
                            break
                        result_cv.wait(5.0)  #poll for Garbage collection
                  
                if not iterator_ref():  #GC Detection on iterator removal
                    break
                assert (len(ready_results) < num_in_parallel)
                assert (not errorJid)                
                statuses = self.status( jids_testing )
                cloudLog.debug('cloud.iresult.result_loop testing %s. got status %s' % \
                               (jids_testing, statuses))
                ctr = 0
                jids_to_access = []
                
                #find all done jobs whose results we can grab
                for jid in jids_testing:                    
                    status = statuses[ctr]
                    if status not in self.finished_statuses:
                        break
                    if status == 'done':                    
                        jids_to_access.append(jid)
                    else: 
                        #postpone error handling until all good results handled:
                        if not jids_to_access and not ready_results:                                                                                 
                            errorJid.append(jid)
                        break
                    ctr+=1
                #technically race condition here -- what if error_jid is popped?
                if errorJid: #on error, return to top. Top will wait on cv
                    jids_testing.popleft()
                    with result_cv:
                        result_cv.notify()
                    continue 
                    
                if not jids_to_access: #no jobs ready yet -- wait and return to top
                    time.sleep(0.2)  
                    #FIXME: Adapter join first job!
                    continue                
                
                cloudLog.debug('cloud.iresult.result_loop getting results of %s' % jids_to_access)
                new_results  = self.result(jids_to_access) #slow - bypass status check
                with result_cv:
                    for result in new_results:
                        ready_results.append(result)
                        jids_testing.popleft()
                    result_cv.notify()
                                    
            cloudLog.debug('cloud.iresult.result_loop is terminating')
            with result_cv:
                result_cv.notify()            
        
        class ResultIterator(object):
            """Iterator that handles results"""
            
            def __init__(self, parentInstance):
                self.parent = parentInstance              
                self.cnt = 0
            
            def __iter__(self):
                return self
            
            def next(self, timeout = timeout):
                """Just walk through ready_results"""               
                with result_cv:                    
                    if not errorJid and not ready_results:
                        if isDone:
                            cloudLog.debug('cloud.iresult.ResultIterator is done')
                            raise StopIteration
                        cloudLog.debug('cloud.iresult.ResultIterator is going to sleep')
                        result_cv.wait(timeout)
                        if not errorJid and not ready_results:
                            if isDone:  #in rare cases, done may come in after the cv wait
                                cloudLog.debug('cloud.iresult.ResultIterator is done (after cv wait)')
                                raise StopIteration        
                            
                            #we timed out
                            raise CloudTimeoutError('iresult iterator timed out')
                        cloudLog.debug('cloud.iresult.ResultIterator is awake. num ready results = %s errorJid is %s' % (len(ready_results), errorJid))
                    
                    result_cv.notify() #result thread will awake once lock released
                    
                    if errorJid:  #trigger exception with join:
                        try:
                            self.parent.join(errorJid)
                        except CloudException, e:
                            errorJid.pop()  #result thread can now continue
                            if ignore_errors:
                                return e
                            else:
                                raise e
                        else: #should never occur
                            assert(False) 
                        
                    assert(ready_results)
                    return ready_results.popleft()
                    
        ri = ResultIterator(self)
        result_thread = threading.Thread(target=result_loop, args=(weakref.ref(ri),))  
        result_thread.daemon = True
        result_thread.start()  
                    
        return ri

    
    def iresult_unordered(self, jids):
        """Hackish - probably should not use"""
        
        class UnorderedResultIterator(object):
            """Iterator that handles results"""
            
            def __init__(self, parent):              
                self.jids_testing = list(maybeXrangeIter(jids))
                self.parent = parent
                
            
            def __iter__(self):
                return self
            
            def next(self):
                                
                while True:
                    
                    jids = self.jids_testing                
                    statuses = self.parent.status( jids )                
                                
                    for jid, status in zip(jids, statuses):
                        if status in self.parent.finished_statuses:
                            self.jids_testing.remove(jid)
                            
                            if status == 'done': #ignore errors
                                res = self.parent.result(jid)                            
                                return jid, res
                    
                    if self.jids_testing:
                        time.sleep(0.5)
                    else:
                        raise StopIteration
        
        return UnorderedResultIterator(self)
    
               
    def info(self, jids, info_requested):
        """        
        Request information about jobs specified by integer or iterable *jids*
        
        As this function is designed for console debugging, the return value 
        is a dictionary whose keys are the *jids* requested.  The values are themselves
        dictionaries, whose keys in turn consist of valid values within the iterable
        *info_requested*.  Each key maps to key-specific information
        about the job, e.g. stdout maps to standard output of job.

        Possible *info_requested* items are one of more of:
	    'stdout', 'stderr', 'exception', 'runtime'- which return standard output, 
	    standard error, exception raised (if applicable) and real runtime of job respectively.
	    
	    When connected to PiCloud, to obtain fields other than 'runtime', the job must have completed
	    
	    e.g. cloud.info(42,'stdout') to get standard output of job 42
        """
                
        if not hasattr(jids,'__iter__'):
            jids = [jids]
        
        if not isinstance(jids, xrange):
            if not reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True):
                raise TypeError( 'cloud.info requires numeric jid(s)' )                
        
        if not hasattr(info_requested,'__iter__'):
            info_requested = [info_requested]
        test = reduce(lambda x, y: x and (isinstance(y,str)), info_requested, True)   
        if not test:
            raise TypeError( 'info_requested must be a valid string value or list of strings' )         

        self._checkOpen()   
        
        if len(info_requested) == 1 and 'runtime' in info_requested:        
            #runtime can change if job is incomplete.
            #Do not request cached runtime when it is only request
            cachedInfo = [{}]            
        else:
            cachedInfo  = self.cacheManager.getCached(jids, info_requested)            
        
        #As we only do a single request, we must request all information for any job missing any info items
        def notInInfo(jid):
            for dct in cachedInfo:
                if jid not in dct:
                    return True
            return False
        
        neededJids = filterXrangeList(notInInfo,jids)     
        
        if neededJids:
            try:
                ainfo = self.adapter.jobs_info(jids=neededJids,info_requested=info_requested)           
            except _catchCloudException, e:
                raise e 
            
            if len(info_requested) != 1 or 'runtime' not in info_requested:
                #runtime can change if job is incomplete.
                #Do not cache runtime requests alone.
                cnt = 0            
                for neededJid in maybeXrangeIter(neededJids):            
                    self.cacheManager.putCached(neededJid, **(ainfo[cnt]))
                    cnt+=1                                                       
               
        else:
            ainfo = []

        aptr = 0
        outinfo = {}
        merged_info = zip(info_requested, cachedInfo)
        for jid in maybeXrangeIter(jids):                
            if notInInfo(jid):
                info = ainfo[aptr]
                aptr+=1
            else:
                info = {}
                for info_item, info_dict in merged_info:
                    info[info_item] = info_dict[jid]
            outinfo[jid] = info
      
        return outinfo 
    
    def kill(self, jids=None):
        """
        Kill any incomplete jobs specified by the integer or iterable *jids*.
        If no arguments are specified (or jids is None), kill every job that has been submitted.
        """
        
        #Internal Note: No caching takes place here, due to rarity of this command
                   
        if jids!=None:
            if not hasattr(jids,'__iter__'):
                jids = [jids]
            
            if not isinstance(jids, xrange):
                test = reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True)
                if not test:
                    raise TypeError( 'cloud.kill requires numeric jid(s)' )
            
            if hasattr(jids,'__len__') and len(jids) == 0:
                return

        self._checkOpen()
                
        try:
            self.adapter.jobs_kill(jids)
        except _catchCloudException, e:
            raise e    
        
        #return statuses[0] if deseq else statuses                    
    
    def delete(self, jids):
        """
        Remove all data (result, stdout, etc.) related to jobs specified by the 
        integer or iterable *jids* 
        Jobs must have finished already to be deleted.
        
        .. note::
            
            In MP/Simulator mode, this does not delete any datalogs, only in-memory info
        """
        if not hasattr(jids,'__iter__'):
            jids = [jids]
        
        if not isinstance(jids, xrange):
            test = reduce(lambda x, y: x and (isinstance(y,(int,long,xrange))), jids, True)
            if not test:
                raise TypeError( 'cloud.delete requires numeric jid(s)' )

        self._checkOpen()
                    
        try:
            self.adapter.jobs_delete(jids)
        except _catchCloudException, e:
            raise e
        finally:
            self.cacheManager.deleteCached(jids)
        
    
    def map(self, func, *args, **kwargs):
        """
        Map *func* (a callable) over argument sequence(s).
        cloud.map is meant to mimic a regular map call such as::
            
            map(lambda x,y: x*y, xlist, ylist)
        
        *args* can be any number of iterables. If the iterables are of different
        size, 'None' is substituted for a missing entries.    
        
        Map will return an iterable describing integer Job IDentificatiers (jids).  Each jid
        corresponds to func being invoked on one item of the sequence(s) (a 'job').
        In practice, the jids can (and should) be treated as a single jid;
        the returned iterable may be passed directly into status, result, etc.
        
        Using cloud.result on the returned jids will return a list of internal results 
        (each being the result of applying the function to an item of the argument sequence(s)).
        
        Example::
    
            def mult(x,y):
                return x*y
            jids = cloud.map(mult, [1,3,5], [2,4,6]) 
    
        This will cause mult3 to be invoked on PiCloud's cluster with x=2
        
        Results::
    
            cloud.result(jids)
            >> [2,12,30]
        
        The result is [1*2,3*4,5*6]
        
        See online documentation for additional information    
        
        Reserved special *kwargs* (see docs for details):
        
        * _depends_on:
            An iterable of jids that represents all jobs that must complete successfully 
            before any jobs created by this map function may be run.
        * _fast_serialization:
            This keyword can be used to speed up serialization, at the cost of some functionality.
            This affects the serialization of both the map arguments and return values
            The map function will always be serialized by the enhanced serializer, with debugging features.
            Possible values keyword are:
                        
            0. default -- use cloud module's enhanced serialization and debugging info            
            1. no debug -- Disable all debugging features for arguments            
            2. use cPickle -- Use python's fast serializer, possibly causing PicklingErrors                
        * _high_cpu:
            Set this to true to run your job on a faster processor.  Additional charges apply.
        * _kill_process:
                Terminate the Python interpreter *func* runs in after *func* completes, preventing
                the interpreter from being used by subsequent jobs.  See Technical Overview for more info.                            
        * _label: 
            A user-defined string label that is attached to the created jobs. 
            Labels can be used to filter when viewing jobs interactively (i.e.
            on the PiCloud website).            
        * _profile:
                Set this to True to enable profiling of your code. Profiling information is 
                valuable for debugging, but may slow down your job.
        * _restartable:
                In the very rare event of hardware failure, this flag indicates that the job
                can be restarted if the failure happened in the middle of the job.
                By default, this is true. This should be unset if the job has external state
                (e.g. it modifies a database entry)
        
        """
        
        #TODO: Add split/chunking param.. see multiprocessing
        if not callable(func):
            raise CloudException( 'cloud.map first argument (%s) is not callable'  % (str(func) ))
        
        if len(args) == 0:
            raise CloudException('cloud.map needs at least 2 arguments')
        
        self._checkOpen()
                
        parameters = self._getJobParameters(func, kwargs)
        
        #typecheck and access correct iterator:
        argIters = []
        cnt = 1
        for arg in args:
            try:
                argIters.append(maybeXrangeIter(arg))
            except AttributeError:
                raise TypeError( 'map argument %d (%s) is not an iterable'  % (cnt,str(arg) ))
            else:
                cnt +=1 
                        
        #[(a,b,c), (1,2,3)] --> [(a,1), (b,2), (c,3)]
        argList = izip_longest(*argIters)
       
        try:
            jids = self.adapter.jobs_map(params=parameters,func=func,mapargs=argList)
        except _catchCloudException, e:
            raise e    
        
        except pickle.PicklingError, e:
            e.args = (e.args[0] + _docmsgpkl,)
            raise e
        
        
        # TODO: ADD SUPPORT FOR CALLBACKS!
        
        return jids
    
class CloudTicketManager(threading.Thread):
    """
    CloudTicketManager is responsible for managing callbacks
    associated with specific jobs/tickets.
    """
    
    cloud = None
    
    # list of tickets to 
    pending_tickets = None
    
    # condition variable
    cv = None
    
    # dict mapping ticket -> callbacks on success
    _callbacks_on_success = None
    
    # dict mapping ticket -> callbacks on error
    _callbacks_on_error = None
    
    # event indicating if thread should die
    die_event = None
    
    def __init__(self, cloud):
        threading.Thread.__init__(self)
    
        self.cloud = cloud
        self.pending_tickets = []
        self.cv = threading.Condition()
        
        # make this a daemon thread
        self.setDaemon(True)
        
        self._callbacks_on_success = {}
        self._callbacks_on_error = {}
        self.die_event = threading.Event()
        
    def stop(self):
        self.die_event.set()
        with self.cv:    
            self.cv.notify()
    
    def add_callbacks(self, ticket, callbacks, type='success'):
        """
        Callbacks should be a function or a list of functions that
        take as its first argument the return value of the cloud call.
        Callbacks will be called in order from left to right. 
        
        Returns True if callbacks are added, False otherwise. 
        """

        # filters empty lists
        if not callbacks:
            return False
                
        # if callbacks is a function, make it a one item list
        # otherwise, assume it is a list of functions
        if not hasattr(callbacks,'__iter__'):
            callbacks = [callbacks]

        if not reduce(lambda x, y: x and (callable(y)), callbacks, True):
            raise CloudException( 'All callbacks must be callable')
        
        # add to different trigger list depending on type
        if type == 'success':
            self._callbacks_on_success.setdefault(ticket, []).extend(callbacks)
        elif type == 'error':
            self._callbacks_on_error.setdefault(ticket, []).extend(callbacks)
        else:
            raise Exception('Unrecognized callback type.')
    
        # add ticket to watch list
        with self.cv:
            # only add if ticket is not currently present
            if ticket not in self.pending_tickets:
                self.pending_tickets.append(ticket)
                self.cv.notify()
        
        return True
    
    def run(self):
        
        while not self.die_event.isSet():
            with self.cv:
                while len(self.pending_tickets) == 0 and not self.die_event.isSet():                                    
                    self.cv.wait()
                
                if self.die_event.isSet():
                    return                
            
            # ASSUMPTION: This is the only thread that will remove tickets
            # TODO: If job does not finish for some time, increase sleep interval
            time.sleep(2.0)
            
            with self.cv:
                
                # get status of tickets
                statuses = self.cloud.status(self.pending_tickets)
                
                # for each ticket, call callbacks if in a finished state
                for ticket, status in zip(self.pending_tickets, statuses):
                    
                    if status in Cloud.finished_statuses:
                        
                        # call appropriate callback
                        callbacks = self._callbacks_on_success.get(ticket,[]) if status == 'done' else self._callbacks_on_error.get(ticket,[])
         
                        # call callback with function argument if it takes an argument
                        for callback in callbacks:
                            if callback.func_code.co_argcount > 0:
                                callback(ticket)
                            else:
                                callback()
                        
                        # callback triggered -> remove ticket from watch list
                        self.pending_tickets.remove(ticket)
                    
