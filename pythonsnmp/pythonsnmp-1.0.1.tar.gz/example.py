#!/usr/local/bin/python
from pythonsnmp import BulkWalker
if __name__ == "__main__":
    """ The main code in the script starts here 
    All you have to do is instantiate the BulkWalker class
    and override its attributes"""
    mySession   = BulkWalker(
            hostlist = ['ony-nm1'],             # Hosts to Walk
            walkmiblist = ['ifDescr','ifSpeed'],# Mibs Needed
            Community = 'public',               # Default Public
            maxrepetitions = 8,                 # Default 16
            Version = 2                         # Default 2
            )
    r = mySession.execute()

    """ Print result object """
    for resultindex,eachresult in r.iteritems():
        print eachresult.hostqueried,'index:%s'%eachresult.iid,
        print eachresult.tag,"=",eachresult.val

