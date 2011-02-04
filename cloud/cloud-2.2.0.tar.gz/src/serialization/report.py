from __future__ import with_statement 
"""
This module is responsible for managing and writing serialization reports

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

import os, datetime, threading    

import distutils
import distutils.dir_util

from . import pickledebug
from .serializationhandlers import DebugSerializer
from .. import cloudconfig as cc
from ..cloudlog import cloudLog
from pickledebug import DebugPicklingError 

class SerializationReport():
    c = """Path to save object serialization meta-data.
    This path is relative to ~/.picloud/"""    
    serializeLoggingPath = \
        cc.loggingConfigurable('serialize_logging_path',
                                          default='datalogs/',
                                          comment=c)
        
    #k = __import__('f')
    #p = __builtins__.__import__('g')
    
    pid = None #process identifier
    cntLock = None
        
    def __init__(self, subdir = ""):
        """
        Create logging directory with proper path if subdir is set
        """
        if subdir:     
            logpath = os.path.expanduser("".join([cc.baselocation,self.serializeLoggingPath,subdir,'/']))
            
            #uses pidgin's log path format        
            date = str(datetime.datetime.today().date())
            date = date.replace(':','-')
            
            time = str(datetime.datetime.today().time())[:8]
            time = time.replace(':','')
            
            timestamp = date + '.' + time
            
            logpath += timestamp
                        
            
            try_limit = 10000
            ctr = 0
            basepath = logpath
            while True:
                try:
                    logpath += '/'
                    if not distutils.dir_util.mkpath(logpath):
                        raise distutils.errors.DistutilsFileError('retry')
                except distutils.errors.DistutilsFileError, e:
                    if ctr >= try_limit:
                        raise IOError("can't make file %s. Error is %s" % (logpath,str(e)))
                    ctr+=1                    
                    logpath = basepath + '-%d' % ctr  
                else:
                    break
            
            cloudLog.info("Serialization reports will be written to %s " % logpath)            
            #hack for SUDO users
            sudouid = os.environ.get('SUDO_UID')
            if sudouid:
                os.chown(logpath, int(sudouid),  int(os.environ.get('SUDO_GID')))
                
            self.logPath = logpath
                    
        self.pickleCount = {}
        self.cntLock = threading.Lock()
    
    def updateCounter(self, baselogname):
        baselogname = baselogname.replace('<','').replace('>','')
        with self.cntLock:
            cnt = self.pickleCount.get(baselogname,0)
            cnt+=1
            self.pickleCount[baselogname] = cnt
        return cnt
        
    def getReportFile(self, logname, ext, cnt = None, pid = None):
        """Returns the name of a report file with cnt and pid filled in"""
        logname = logname.replace('<','').replace('>','')
       
        mid = ''
        if pid:
            mid += 'P%d.' % pid
        if cnt:
            mid += '%d.' % cnt

        logname = logname % mid
        
        logname+= ext
        
        return self.logPath + logname
        
    
    def openReportFile(self, logname, ext, cnt = None, pid = None):
        """Open an arbitrary report file with cnt and pid filled in"""
        return file(self.getReportFile(logname, ext, cnt, pid),'w')  
        
    
    """Reporting"""
    def saveReport(self, dbgserializer, logname, cnt = None, pid = ''):
        
        if not hasattr(dbgserializer,'writeDebugReport'):
            #due to serialization level being cloud.call argument, we might not have
            # a writeDebugReport in active serializer, even though this object exists
            return
        
        #HACK for default detection
        if type(pid) == str:
            pid = self.pid
         
        reportf = self.openReportFile(logname, '.xml', cnt, pid) 

        dbgserializer.writeDebugReport(reportf)
        reportf.close()
        
        return reportf.name

    

        