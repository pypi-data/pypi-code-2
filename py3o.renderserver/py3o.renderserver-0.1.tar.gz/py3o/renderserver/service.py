# File name: service.py
#
# The service module defines a single class (Py3oWindowsService) that contains
# the functionality for running a py3o.renderserver as a Windows Service.
# 
# To use this class, users must do the following:
# 1. Download and install the win32all package
#    (http://starship.python.net/crew/mhammond/win32/)
#
# 2. Open a command prompt and navigate to the directory where this file
#    is located.  Use one of the following commands to
#    install/start/stop/remove the service:
#    > service.py install
#    > service.py start
#    > service.py stop
#    > service.py remove
#    Additionally, typing "service.py" will present the user with all of the
#    available options for controlling an installed service
#
#    to configure the service use the commands provided by the service.py --help
#    this command is handled by our own program and not by the windows service framework
#
# Once installed, the service will be accessible through the Services
# management console just like any other Windows Service.  All service 
# startup exceptions encountered by the Py3oWindowsService class will be 
# viewable in the Windows event viewer (this is useful for debugging
# service startup errors); all application specific output or exceptions that
# are not captured by the standard TG logging mechanism should 
# appear in the stdout/stderr logs.
#
# This module has been tested on Windows Server 2000, 2003, and Windows
# XP Professional.

from ConfigParser import SafeConfigParser
import optparse
import logging

import sys
import os
from os.path import *

import win32serviceutil
import win32service
import win32event
import win32process
import win32api
from win32com.client import constants
import _winreg
from subprocess import Popen

# the org name used to store your conf in the registry
organization = "py3o"
product_name = "py3orenderserver"

class NullOutput(object):
    """a file-like object that behaves like a black hole.
    Does not consume memory and gives nothing back. Ever.
    """
    def noop(self, *args, **kw):
        pass
    
    write = writelines = close = seek = flush = truncate = noop
    
    def __iter__(self):
        return self

    def next(self):
        raise StopIteration

    def isatty(self):
        return False
    
    def tell(self):
        return 0

    def read(self, *args, **kw):
        return ''

    readline = read
    
    def readlines(self, *args, **kw):
        return list()

def get_config():
    """find the config file path in the registry
    """
    config = dict()

    try:
        reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\%s\\%s' % (organization, product_name))

        config["soffice_path"] = _winreg.QueryValueEx(reg_key, 'soffice_path')[0]
        config["soffice_host"] = _winreg.QueryValueEx(reg_key, 'soffice_host')[0]
        config["soffice_port"] = int(_winreg.QueryValueEx(reg_key, 'soffice_port')[0])
        config["listen_port"] = int(_winreg.QueryValueEx(reg_key, 'listen_port')[0])

    except WindowsError, e:
        logging.exception(str(e))

    return config

def set_config(options):
    """set the config file path in the registry
    """
    reg_key = _winreg.CreateKey(_winreg.HKEY_LOCAL_MACHINE,
            'SOFTWARE\\%s\\%s' % (organization, product_name))

    reg_val = _winreg.SetValueEx(
            reg_key, 'soffice_path', None, _winreg.REG_SZ, options.soffice_path)
    reg_val = _winreg.SetValueEx(
            reg_key, 'soffice_host', None, _winreg.REG_SZ, options.soffice_host)
    reg_val = _winreg.SetValueEx(
            reg_key, 'soffice_port', None, _winreg.REG_SZ, options.soffice_port)
    reg_val = _winreg.SetValueEx(
            reg_key, 'listen_port', None, _winreg.REG_SZ, options.listen_port)

class Py3oWindowsService(win32serviceutil.ServiceFramework):
    """The Py3oWindowsService class contains all the functionality required
    for running a py3o renderserver as a Windows Service. The only
    user edits required for this class are located in the following class
    variables:
    
    _svc_name_:         The name of the service (used in the Windows registry).
                        DEFAULT: The capitalized name of the current directory.
    _svc_display_name_: The name that will appear in the Windows Service Manager.
                        DEFAULT: The capitalized name of the current directory.    

    For information on installing the application, please refer to the
    documentation at the end of this module or navigate to the directory
    where this module is located and type "service.py" from the command
    prompt.
    """
    _svc_name_ = '%s' % (product_name)
    _svc_display_name_ = _svc_name_
    _svc_deps = list()

    def __init__(self, args):
        """set some usefull variables
        """

        # replace normal output channels by fake ones
        # to make sure we don't go over the buffer and inadvertently
        # kill our windows service
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = NullOutput()
        sys.stderr = NullOutput()

        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        """Called when the Windows Service runs."""

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        self.serv_process = self.launch_server()
        pcs = win32process.EnumProcesses()

        if self.serv_process.pid in pcs:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        else:
            # something went wrong and we did not start correctly
            self.ReportServiceStatus(win32service.SERVICE_ERROR_CRITICAL)
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)            

    def SvcStop(self):
        """Called when Windows receives a service stop request."""

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        try:
            win32api.TerminateProcess(int(self.serv_process._handle), -1)
        except:
            # TODO if we see errors one day, maybe do some logging... ?
            pass  

        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def launch_server(self):
        """Launch the server by popening it
        returns: the pid of the server we just popened
        """
        call_flags = 0
        call_flags |= win32process.CREATE_NO_WINDOW

        config = get_config()

        soffice_path = config['soffice_path']
        soffice_base = os.path.split(soffice_path)[0]
        soffice_python = os.path.join(soffice_base, 'python.exe')

        script_path = os.path.join(
                os.path.split(soffice_base)[0],
                'Basis', 'program', 'python-core-2.6.1',
                'Scripts', 'start-py3o-renderserver-script.py')

        call_args = [
                soffice_python,
                script_path,
                #'-s', '"%s"' % config['soffice_path'],
                #'-a', '%s' % config['soffice_host'],
                #'-p', '%s' % config['soffice_port'],
                #'-l', '%s' % config['listen_port'],
                ]

        process = Popen(call_args, creationflags=call_flags)

        return process    

def main():

    optparser = optparse.OptionParser()

    optparser.add_option(
        "-c", "--config",
        dest="config",
        action="store_true",
        help="Config mode, use this flag to set any config option listed below",
        default=False)

    optparser.add_option(
        "-s", "--sofficepath",
        dest="soffice_path",
        help="specify the open office file path FILE",
        metavar="FILE",
        default=None)

    optparser.add_option(
        "-a", "--sofficehost",
        dest="soffice_host",
        help="specify the open office hostname/ip address ADDR",
        metavar="ADDR",
        default="127.0.0.1")

    optparser.add_option(
        "-p", "--sofficeport",
        dest="soffice_port",
        help="specify the open office port PORT",
        metavar="PORT",
        default="8997")

    optparser.add_option(
        "-l", "--listenport",
        dest="listen_port",
        help="specify the PORT on which our service will listen",
        metavar="PORT",
        default="8994")

    (options, args) = optparser.parse_args()

    setup_flag = False

    if options.config:
        setup_flag = True
        set_config(options)

    if setup_flag:
        # if we handle setup tasks, exit we normal flag
        sys.exit(0)

    # The following are the most common command-line arguments that are used
    # with this module:
    #  service.py install (Installs the service with manual startup)
    #  service.py --startup auto install (Installs the service
    #  with auto startup)
    #  service.py start (Starts the service)
    #  service.py stop (Stops the service)
    #  service.py remove (Removes the service)
    #
    # For a full list of arguments, simply type "service.py".
    win32serviceutil.HandleCommandLine(Py3oWindowsService)

if __name__ == '__main__':
    main()
