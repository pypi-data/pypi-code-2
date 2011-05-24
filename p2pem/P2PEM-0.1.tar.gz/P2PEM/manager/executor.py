import subprocess
import sys
import P2PEM

execute_as_root_simple = None
execute_as_root = None
password = None
"""
root password or None
"""

exec_log = None


def get_passwd():
    return '%s\n' % password
    


def _execute_with_password_simple(command):
    
    cmd = "sudo -S %s" % (command)
    exec_log.debug("Executor - execute_with_password_simple: command=%s" % cmd)

    sp = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.communicate(get_passwd())

    return sp.returncode
    
def _execute_with_password(command):

    cmd = "sudo -S %s" % (command)
    exec_log.debug("Executor - execute_with_password: command=%s" % cmd)
    sp = subprocess.Popen(cmd, shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)                
    out, err = sp.communicate(get_passwd())

    return sp.returncode, out, err

def _execute_without_password_simple(command):
    
    cmd = "sudo %s" % (command)
    exec_log.debug("Executor - execute_without_password_simple: command=%s" % cmd)   
 
    return subprocess.call(cmd, shell=True)

def _execute_without_password(command):

    cmd = "sudo %s" % (command)
    exec_log.debug("Executor - execute_without_password: command=%s" % cmd)
    
 
    sp = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    return sp.returncode, out, err


def execute_simple(command):
    """
    Executes command as root.
    params:
        command
    returns:
        returncode
    """
    
    exec_log.debug("Executor - execute_simple: command=%s" % command)
    
 
    return subprocess.call(command, shell=True)

def execute(command):
    """
    Executes command as root.
    params:
        command
    returns:
        returncode
        out - string
        err - string
    """
    
    exec_log.debug("Executor - execute: command=%s" % command)   
 
    sp =  subprocess.Popen(command, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    return sp.returncode, out, err

def set_mode(passwd):
    """
    Sets the mode of the executor.
    params:
        passwd - None (no password) or string (set password)
    """
    
    module = sys.modules[__name__]
    if passwd:
        module.password = passwd
        module.execute_as_root_simple = _execute_with_password_simple
        module.execute_as_root = _execute_with_password
    else:
        module.execute_as_root_simple = _execute_without_password_simple
        module.execute_as_root = _execute_without_password
        
    module.exec_log = P2PEM.loggs.used_logger
         


