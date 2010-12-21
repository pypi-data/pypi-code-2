# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os

from paste.fileapp import _FileIter
from threading import Thread
from stellaris.service import Serve, SecureServe
from tempfile import mkstemp
from subprocess import Popen, PIPE

def file_to_str(path):
    return ''.join([l for l in open(path, 'r')])

def dump_to_file(data):
    (fd, tmp_name) = mkstemp()

    f = os.fdopen(fd, 'w+')
    f.write(data)
    
    f.close()
    
    return tmp_name

def remove_dirs(dir_path):
    """
    Recursively removes the directory and all sub-directories.
    """
    for f in os.listdir(dir_path):
        cur_path = os.path.join(dir_path, f)
        if os.path.isdir(cur_path):
            remove_dirs(cur_path)
        else:
            os.remove(cur_path)

    os.rmdir(dir_path)
    
class StellarisServerThread(Thread):
    
    def __init__(self, config):
        Thread.__init__(self)
        self.server = Serve(config)
    
    def run(self):
        self.server.start()
        
    def stop(self):
        self.server.stop()
        self.join()

class StellarisSecureServerThread(Thread):
    
    def __init__(self, config):
        Thread.__init__(self)
        self.server = SecureServe(config)
    
    def run(self):
        self.server.start()
        
    def stop(self):
        self.server.stop()
        self.join()
        
## below is taken from:
## http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/286222
## and modified

## some other tricks:
## http://www.pixelbeat.org/scripts/ps_mem.py
## also, see: man proc
## os.sysconf("SC_PAGE_SIZE")

def _VmB(pid, VmKey):
    '''Private.
    '''
    _proc_status = '/proc/%d/status' % pid
    
    _scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}

     # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
     # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
     # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(pid, since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB(pid, 'VmSize:') - since


def resident(pid, since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB(pid, 'VmRSS:') - since


def stacksize(pid, since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since       

def memory_usage(pid):
    page_size = os.sysconf("SC_PAGE_SIZE")
    mem = file("/proc/%d/statm" % pid).readline().split()
    bytes = 2**10
    return [(int(m.strip())*page_size)/bytes for m in mem]
    
def child_pids(parent_pid):
  """
    This function use the "ps" linux command to get children info
      (pid and command) of a given process.
  """
  p = Popen(["ps", "--no-headers", "--ppid", str(parent_pid), "-o", "pid"], stdout=PIPE)
  output = p.communicate()[0]
  return [int(pid.strip()) for pid in output.split('\n') if pid.strip() and str(p.pid) != pid.strip()]
     
