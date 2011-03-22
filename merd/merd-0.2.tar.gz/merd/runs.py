# Copyright (c) 2011, The merd Project
# All rights reserved.
   
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#    * Neither the name of the merd project nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Pieter Hooimeijer, Dan Lepage

from datetime import datetime
from inspect import getsource

from os import access
from os import unlink
from os import X_OK
from os.path import exists, join

from re import compile
from re import MULTILINE

from shlex import split

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from subprocess import Popen
from subprocess import PIPE

from threading import Thread

from tempfile import NamedTemporaryFile


from messages import log, FILE_EXECUTOR_DESCR, NOT_EXECUTABLE, ERROR, SOURCE_DEFAULT, \
    BASIC_PROC_EXECUTOR_DESCR

from model import Paper, DataSet, Run, Result, SUCCESS, FAIL, RUNNING, DONE, INPROGRESS


class Executor:
    def handle_run_meta(self, runmeta):
        raise NotImplementedError()

    def meta_description(self):
        raise NotImplementedError()

    def start_run(self, dataelt):
        raise NotImplementedError()

    def stop_run(self):
        raise NotImplementedError()

    def postprocess(self, res):
        raise NotImplementedError()

class Proc(Thread):
   def __init__(self, comm):
       Thread.__init__(self)
       self.proc = None
       self.returncode = None
       self.stdoutdata = None
       self.stderrdata = None
       self.starttime = None
       self.endtime = None
       self.timedout = False
       self.runningtime = None
       self.comm = comm
      
   def run(self):
       self.starttime = datetime.today()
       self.proc = Popen(self.comm, bufsize=-1, stdin=None,  
                                   stdout=PIPE, stderr=PIPE, shell=True, close_fds=True)
      
       (self.stdoutdata, self.stderrdata) = self.proc.communicate()
       self.endtime = datetime.today()
       self.returncode = self.proc.poll()

class BasicProcExecutor(Executor):
    def __init__(self, exepath, timeout):
        self.exepath = split(exepath)
        self.timeout = timeout
        self.aborted = False
        self.procthread = None

    def meta_description(self):
        src = SOURCE_DEFAULT()
        try:
            src = getsource(self.__class__)
        except Exception:
            pass
        res =  '\n'.join([BASIC_PROC_EXECUTOR_DESCR(),
                          src])
        return res

    def handle_run_meta(self, thedata):
        return None

    def start_run(self, dataelt):
        params = self.genparams(dataelt)

        if params is None:
            params = []
     
        paramsfull = [x for x in self.exepath]
        paramsfull.extend(params)

        self.procthread = Proc(' '.join(paramsfull))
        self.procthread.start()
        
        if self.timeout > 0:
            self.procthread.join(self.timeout)
        else:
            self.procthread.join()

        wastimeout = False
        if self.procthread.isAlive():
            wastimeout = True
            self.procthread.proc.terminate()

        self.procthread.join()
        self.procthread.timedout = wastimeout
        return self.procthread

    def stop_run(self):
        self.aborted = True
        self.procthread.proc.terminate()
        self.cleanup()

    def genparams(self, dataelt):
        return []

    def postprocess(self, res):
        res.started = self.procthread.starttime
        res.finished = self.procthread.endtime
        res.stdout = self.procthread.stdoutdata
        res.stderr = self.procthread.stderrdata
        res.status = SUCCESS
        res.runningtime = self.procthread.runningtime
        res.exitcode = self.procthread.returncode

        pattern = compile(r"^TIME: (\d+)ms", MULTILINE)
        matches = pattern.search(self.procthread.stdoutdata)
        if matches is not None:
            res.runningtime = int(matches.group(0))
        else:
            res.runningtime = -1

    def cleanup(self):
        pass 
        
class FileExecutor(BasicProcExecutor):
    def __init__(self, exepath, timeout):
        BasicProcExecutor.__init__(self, exepath, timeout)
        self.filename = None
    
    def genparams(self, dataelt):
        with NamedTemporaryFile(delete=False) as f:
            self.filename = f.name
            f.write(dataelt.content)
        return [f.name]

    def cleanup(self):
        unlink(self.filename)

class ExecutorThread(Thread):
    def __init__(self, executor, rid, dsid, pid, sessionmaker):
        Thread.__init__(self)
        self.executor  = executor
        self.sessionmaker = sessionmaker
        self.rid = rid
        self.dsid = dsid
        self.pid = pid

    def run(self):
        self.dbsession = scoped_session(self.sessionmaker)
        self.runinst   = self.dbsession.query(Run).filter_by(rid=self.rid).first()
        self.dataset   = self.dbsession.query(DataSet).filter_by(dsid=self.dsid).first()
        self.paper     = self.dbsession.query(Paper).filter_by(pid=self.pid).first()

        try:
            newmeta = self.executor.handle_run_meta(self.runinst.meta)
            if newmeta is not None:
                self.runinst.meta = newmeta

            self.dbsession.merge(self.runinst)
            addition = self.executor.meta_description()
            self.runinst.descr = self.runinst.descr + addition
            
            self.runinst.executorsrc = getsource(self.executor.__class__)
            self.dbsession.commit()

            try:
                for e in self.dataset.elements:
                    if self.executor.aborted:
                        break
                    res = Result()
                    res.run = self.runinst
                    res.dataelt = e
                    res.status = RUNNING
                    self.dbsession.add(res)
                    self.dbsession.commit()
                    self.executor.start_run(e)
                    self.dbsession.merge(res)
                    self.executor.postprocess(res)
                    self.executor.cleanup()
                    self.dbsession.commit()
            except ValueError as e:
                print "aborting run"
                raise e

            self.runinst.status = DONE
            self.dbsession.merge(self.runinst)
            self.dbsession.commit()
        except ValueError as e:
            print "run failed"
            raise e
        else:
            self.dbsession.close()

    def abort(self):
        self.executor.stop_run()
