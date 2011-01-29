#!/usr/local/bin/python
import netsnmp

""" This implements the snmpbulkwalk for snmpV2
using python's NetSNMP bindings. At present there is
no snmpbulkwalk method available, and the snmp walk
takes too long to complete (individual getnext).
I've written this class to overcome that by combining 
getbulk with a user defined maxrepetitions attribute 
-Ajay

BENCHMARK : Walks 1-MX960 for 4 oids in under 2 secs,
as opposed to python's net-snmp implementation of 
snmpwalk which takes 11 seconds to do the same.

USAGE : This is a fairly straightforward class. Please 
scroll down to the __main__ section of the code. All 
you have to do is instantiate an object of BulkWalker
class, and pass in a list of hostnames, oids, Version (2)
and community

CONTACT : The author can be reached at ajay@ajaydivakaran.com

FUTURE CHANGES : Multithreaded implementation of BulkWalk
"""

class BulkWalker:
    """Bulkwalk Session object"""
    def __init__(self,
            hostlist        = [],
            maxrepetitions  = 16,
            walkmiblist     = [],
            Version         = 2,
            Community       = 'public',
            sessionresults  = {}
            ):
        self.hostlist = hostlist
        self.maxrepetitions = maxrepetitions
        self.walkmiblist = walkmiblist
        self.Version = Version
        self.Community = Community
        self.sessionresults = sessionresults
        print "host %s" %self.hostlist
    
    def execute(self):
        """Runs snmp query using mibs in 'walkmiblist',
        against all hosts in 'hostlist'"""
        for thishost in self.hostlist:
            for thismib in self.walkmiblist:
                sess = netsnmp.Session (Version = self.Version,
                        DestHost = thishost,
                        Community = self.Community
                        )
                """Actual bulkwalk using getbulks starts here"""
                startindexpos = 0
                runningtreename = thismib
                while (runningtreename == thismib):
                    vars = netsnmp.VarList(
                            netsnmp.Varbind(thismib,startindexpos)
                            )
                    vals = sess.getbulk(0,self.maxrepetitions,vars)
                    """ Print output from running getbulk"""
                    for i in vars:
                        if (i.tag == thismib):
                            thiskey = i.tag+'-'+str(i.iid)
                            self.sessionresults[thiskey] = i;
                            self.sessionresults[thiskey].hostqueried = thishost
                    """ Set startindexpos for next getbulk """
                    startindexpos = int(vars[-1].iid)
                    """ Refresh runningtreename from last result"""
                    runningtreename = vars[-1].tag
        return self.sessionresults                    
