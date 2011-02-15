#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Executable instance."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

__all__ = ['Instance']

import sys
import os
import shutil
import io
import errno
from datetime import datetime, timedelta
import json
import subprocess
from threading import Thread
from time import sleep
import logging
from .ZombieConfig import config, datadir


DELTA_T = 0.01


class ActiveTest(Thread):
    """Determine if the list of active instances are still executing."""
    
    def __init__(self):
        super().__init__(name="Instances Alive Test")
        self.daemon = True
        self.__instances = set()
        self.start()
    
    def run(self):
        """Poll the child process on a regular schedule to determine still alive."""
        logging.getLogger("zombie").info("Start %s", self.name)
        while (True):
            try:
                sleep(DELTA_T)
                self.__instances -= set([i for i in self.instances if i.process is None])
                stopped = [i for i in self.instances if i.process.poll() is not None]
                self.__instances -= set(stopped)
                for i in stopped:
                    i._Instance__returncode = i.process.returncode
                    i._Instance__end = datetime.utcnow()
                    i._Instance__save()
                    i.stdout.close()
                    i.stderr.close()
            except Exception as err:
                logging.getLogger("zombie").warning(err)
        logging.getLogger("zombie").info("End %s", self.name)
    
    @property
    def instances(self):
        return self.__instances
activetest = ActiveTest()


class Instance:
    """This represents a instance of an executable. When an instance is
    created it will add itself to the list of loaded instances in the
    owning Executable object.
    
    Properties
    ----------
    executable
        The executable factory that created this instance.
    name
        The name of this execution instance.
    environ
        The environment that was used to start this instance.
    arguments
        The command line arguments used to start this instance.
    datadir
        The path to the instance data directory.
    workdir
        The path to the instance's initial working directory.
    tmpdir
        The path to the instance's temporary directory.
    timeout
        The ``datetime`` stamp when the instance shall be terminated. This will
        update as the process adds data to the stdout and stderr streams.
    remove
        The ``datetime`` stamp after which the instance may be removed from
        the list of instances in the executable. This is generally seven days
        after the creation of the instance.
    process
        The subprocess object the instance is executing in, or ``None`` if
        the instance has completed execution.
    start
        The ``datetime`` stamp when the instance was started.
    end
        The ``datetime`` stamp when the instance was terminated.
    returncode
        The numeric exit status of the instance, or ``None`` if the instance
        is still running.
    stdin
        The file like object to feed data into the instance. If the instance
        has completed execution this will be a closed file. Closing this
        stream will send an EOF to the process instance.
    stdout_path
        This is the path to the stored stdout file.
    stdout
        The file like object that contains the standard output. This is a
        random access read only file.
    stderr_path
        This is the path to the stored stderr file.
    stderr
        The file like object that contains the standard error. This is a
        random access read only file.
    """
    
    @classmethod
    def createname(cls):
        """Create a unique RESTful name for a new executing instance."""
        name = config.get("pyzombie_filesystem", "instance")
        name = "{0}_{1}".format(name, datetime.utcnow().strftime("%Y%jT%H%M%SZ"))
        return name
    
    @classmethod
    def getcached(cls, executable, name):
        """Get a cached instance from the executable if it exists.
        
        Parameters
        ----------
        executable
            The executable factory that creates this instance.
        name
            The name of this instance.
        """
        inst = None
        instpath = os.path.join(executable.dirpath, name, 'state.json')
        if os.path.isfile(instpath):
            if name in executable.instances:
                inst = executable.instances[name]
            else:
                inst = Instance(executable, name)
        return inst
        
    def __init__(self, executable, name, environ={}, arguments=[]):
        """
        Parameters
        ----------
        executable
            The executable factory that creates this instance.
        name
            The name of this instance.
        environ
            The environment dictionary to use to start this instance. If
            ``None`` then a minimal shell environment shall be used: the
            environment of pyzombie server shall not be used implicitly. If
            the named instance already exists then this is ignored.
        arguments
            The list of command line arguments for the instance. If the
            named instance already exists then this is ignored.
        """
        self.__executable = executable
        self.executable.instances[name] = self
        self.__name = name
        self.__statepath = os.path.join(self.datadir, 'state.json')
        self.__environ = environ
        self.__arguments = arguments
        self.__process = None
        self.__timeout_delta = timedelta(seconds=5)
        self.__stdin = None
        self.__stdout = None
        self.__stderr = None
        self.__load()
        
        if not os.path.isdir(self.datadir):
            os.makedirs(self.datadir)
            os.makedirs(self.workdir)
            os.makedirs(self.tmpdir)
            open(self.stdout_path, 'wt').close()
            open(self.stderr_path, 'wt').close()
        
        if self.returncode is None and self.process is None:
            try:
                args = list(self.arguments)
                args.insert(0, "{0}:{1}".format(self.executable.name, self.name))
                
                stdout = open(self.stdout_path, mode='wt', encoding='UTF-8')
                stderr = open(self.stderr_path, mode='wt', encoding='UTF-8')
                self.__process = subprocess.Popen(args,
                    executable=self.executable.binpath,
                    stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                    cwd=self.workdir, env=self.environ, shell=False)
                activetest.instances.add(self)
            except OSError as err:
                if err.errno != errno.ENOENT:
                    raise err
                logging.getLogger("zombie").warn(
                    "Unable to find executable for instance {0}/{1}.".format(self.executable.name, self.name))
            self.__save()
    
    def __str__(self):
        return "<pyzombie.Instance {0}>".format(self.name)
    
    def __repr__(self):
        return "<pyzombie.Instance {0}>".format(self.name)
    
    def state(self, urlprefix, urlpath=""):
        """This will marshall the state of this instance into primative data
        types (e.g. dict, list, and string) that can be used in XML, JSON,
        or YAML marshalling."""        
        state = {}
        state['version'] = __version__
        state['name'] = "{0}/{1}/{2}".format(self.executable.name, urlpath, self.name)
        state['self'] = "{0}/{1}".format(urlprefix.rstrip('/'), state['name'])
        state['stdin'] = "{0}/{1}".format(state['self'].rstrip('/'), "stdin")
        state['stdout'] = "{0}/{1}".format(state['self'].rstrip('/'), "stdout")
        state['stderr'] = "{0}/{1}".format(state['self'].rstrip('/'), "stderr")
        state['environ'] = self.environ
        state['arguments'] = self.arguments
        state['remove'] = self.remove.strftime(self.DATETIME_FMT)
        state['timeout'] = self.timeout.strftime(self.DATETIME_FMT)
        state['start'] = self.start.strftime(self.DATETIME_FMT)
        if self.end:
            state['end'] = self.end.strftime(self.DATETIME_FMT)
        else:
            state['end'] = None
        state['returncode'] = self.returncode
        return state
    
    def delete(self):
        """Terminate the instance and release resources."""
        del self.executable.instances[self.name]
        if self.process is not None and self.process.returncode is None:
            self.process.kill()
            self.process.wait()
        shutil.rmtree(self.datadir, True)
            
    @property
    def executable(self):
        return self.__executable
    
    @property
    def name(self):
        return self.__name
    
    @property
    def restname(self):
        return os.path.join(self.executable.name, 'instances', self.name)
    
    @property
    def environ(self):
        return self.__environ
    
    @property
    def arguments(self):
        return self.__arguments
    
    @property
    def datadir(self):
        return os.path.join(self.executable.dirpath, self.name)
    
    @property
    def workdir(self):
        return os.path.join(self.datadir, 'var')
    
    @property
    def tmpdir(self):
        return os.path.join(self.datadir, 'tmp')
    
    @property
    def timeout(self):
        outmtime = datetime.utcfromtimestamp(os.path.getmtime(self.stdout_path))
        errmtime = datetime.utcfromtimestamp(os.path.getmtime(self.stderr_path))
        if outmtime >= errmtime:
            return outmtime + self.__timeout_delta
        else:
            return errmtime + self.__timeout_delta
    
    @property
    def remove(self):
        return self.__remove
    
    @property
    def process(self):
        return self.__process
    
    @property
    def start(self):
        return self.__start
    
    @property
    def end(self):
        return self.__end
    
    @property
    def returncode(self):
        return self.__returncode
    
    @property
    def stdin(self):
        if self.process:
            return self.process.stdin
        else:
            ret = io.StringIO()
            ret.close()
            return ret
    
    @property
    def stdout_path(self):
        return os.path.join(self.datadir, 'stdout.txt')
    
    @property
    def stdout(self):
        if self.__stdout is None or self.__stdout.closed:
            self.__stdout = open(self.stdout_path, mode='r', encoding='UTF-8')
        return self.__stdout
    
    @property
    def stderr_path(self):
        return os.path.join(self.datadir, 'stderr.txt')
    
    @property
    def stderr(self):
        if self.__stderr is None or self.__stderr.closed:
            self.__stderr = open(self.stderr_path, mode='r', encoding='UTF-8')
        return self.__stderr

    DATETIME_FMT = '%Y-%m-%dT%H:%M:%SZ'
    
    def __save(self):
        """This will save the state of this instance to the instance's data
        directory."""
        state = self.state("file:/{0}/".format(self.executable.datadir))
        state['workdir'] = "file:" + self.workdir
        state['tmpdir'] = "file:" + self.tmpdir
        state['stdout'] = state['stdout'] + '.txt'
        state['stderr'] = state['stderr'] + '.txt'
                
        statefile = open(self.__statepath, 'wt')
        json.dump(state, statefile, sort_keys=True, indent=4)
        statefile.flush()
        statefile.close()
    
    def __load(self):
        """This will load the state of this instance from the instance's
        data directory."""
        if os.path.isfile(self.__statepath):
            statefile = open(self.__statepath, 'rt')
            state = json.load(statefile)
            statefile.close()
            
            self.__remove = datetime.strptime(state['remove'], self.DATETIME_FMT)
            self.__start = datetime.strptime(state['start'], self.DATETIME_FMT)
            
            if state['end']:
                self.__end = datetime.strptime(state['end'], self.DATETIME_FMT)
            else:
                self.__end = datetime.utcnow().strftime(self.DATETIME_FMT)
            
            if state['returncode'] is not None:
                self.__returncode = int(state['returncode'])
            else:
                self.__returncode = None
        else:
            self.__remove = datetime.utcnow() + timedelta(days=7)
            self.__start = datetime.utcnow()
            self.__end = None
            self.__returncode = None






