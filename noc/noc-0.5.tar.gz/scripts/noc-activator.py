#!/usr/bin/env python
#
# Service Activation Engine
#
import os,sys,site

if __name__ == '__main__':
    # Adjust paths
    d=os.path.dirname(sys.argv[0])
    if not d:
        d=os.getcwd()
    d=os.path.abspath(os.path.join(d,".."))
    contrib=os.path.abspath(os.path.join(d,"contrib","lib"))
    sys.path.insert(0,contrib)
    sys.path.insert(0,os.path.abspath(os.path.join(d,"..")))
    sys.path.insert(0,d)
    # Install eggs from contrib/lib
    site.addsitedir(contrib)
    # Run activator
    from noc.sa.activator import Activator
    activator=Activator()
    activator.process_command()