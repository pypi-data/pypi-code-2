#!/usr/bin/env python

import sys

import os
sys.path.append(os.getcwd())

from P2PEM.director.scenario_functions import create
import imp
try:
    from tor_director import director as director_class
except:    
    from P2PEM.director.director import Director as director_class

try:
    from tor_director import get_director_params
except:
    from P2PEM.director.director import get_director_params
    
try:
    from tor_director import tor_pre_scenario
except:
    from P2PEM.director.director import tor_pre_scenario
    
import getopt
import os

def run_function(director, callable, args):
    print args
    callable(director, *args)

def run_director(filename, directory):

    sys.path.append(directory)

    try:
        fp, pathname, description = imp.find_module(filename)

    
        sys.path.pop(-1)
    except:
        directory = directory or "[]"
        print >> sys.stderr, "ERROR: Scenario file does not exist. directory=%s, file=%s" % (str(directory), str(filename))
        return False
        
    try:    
        sc = imp.load_module(filename,fp, pathname, description)
        
        params = get_director_params(sc)
        director = director_class(sc.MACHINES_DEF, sc.DIR_LOG, {'address': sc.MAN_TO_DIR_LOG_ADDR, 'port': sc.MAN_TO_DIR_LOG_PORT},
                                  sc.PEER_IDENT_MODE, sc.SWAP_LIMIT,
                                   
                      *params)

        
    except Exception as e:
        print "ERROR - scenario unparsable: %s" % str(e)
        return False
    finally:
        if fp:
            fp.close()
    
    read_scenario(director, sc)
    return True
    
def pre_scenario(sc, director):
    idranges = list()
    for step in sc.scenario:
        if step[0] == create:
            idranges.append((step[1], step[2]))

    director.set_ids(idranges)
    tor_pre_scenario(sc, director)
    
def read_scenario(director, sc):

    
    i = 0
    try:
        if director.start():
            
            pre_scenario(sc, director)
            print 
            for step, i in zip(sc.scenario, range(len(sc.scenario))):

                run_function(director, step[0], step[1:])
    
    except KeyboardInterrupt:
        pass        
    except Exception as e:
        print >>sys.stderr, "WRONG scenario definition"
        print e
        try:
            print >>sys.stderr, "ERROR at line %d" % (i+1,)
        except:
            pass

    
    director.tear_down()
    
    
def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    try:

        opts, args = getopt.getopt(argv[1:],[],["scenario-name=", "scenario-directory="])
               
        filename='test_scenario'
        directory=''

        for o, a in opts:
            if o == "--scenario-name":
                filename=a
            elif o == "--scenario-directory":
                directory=a
        
        try:
            suc = run_director(filename, directory)
            if not suc:
                usage()
        except Exception, msg:
            print >>sys.stderr, msg
            print >>sys.stderr, "Code ERROR."
            return 2
        
    except Exception, msg:
        print >>sys.stderr, msg
        usage()
        return 2 

def usage():
    print >>sys.stderr, "usage: --scenario-name=<file_name_without_suffix> --scenario-directory=<directory>"
    
if __name__ == "__main__":
    main()