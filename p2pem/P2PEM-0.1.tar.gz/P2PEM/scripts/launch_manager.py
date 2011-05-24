#!/usr/bin/env python

from SimpleXMLRPCServer import SimpleXMLRPCServer
import getopt
import os

import sys
sys.path.append(os.getcwd())

try:
    from tor_manager import manager as manager_class
    
except:
    from P2PEM.manager.manager import Manager as manager_class



manager = None
server = None

def set_manager(shaper, swap_limit, log, sudo_mode, *args):
    
    global manager
    manager =  manager_class(shaper, swap_limit, log, sudo_mode, *args)


    server.register_instance(manager, False)

def stop():
    if manager:
        manager.tear_down()
    
    server.server_close()

    
def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    try:

        opts, args = getopt.getopt(argv[1:],[],["address=", "port="])

        address='localhost'
        port=8888

        for o, a in opts:
            if o == "--address":
                address=a
            elif o == "--port":
                port=int(a)
                
        run_manager(address, port)
        
    except IOError:
        return 
    except Exception, msg:
        print >>sys.stderr, msg
        print >>sys.stderr, "usage: --address=<ip_address_to_run_at> --port=<port_to_run_at>"
        return 2

    
def run_manager(address, port):
    
    global server
    server = SimpleXMLRPCServer((address, port), allow_none=True, logRequests = False)
    
    server.register_function(set_manager)
    server.register_function(stop)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop()
    
if __name__ == "__main__":
    main()
