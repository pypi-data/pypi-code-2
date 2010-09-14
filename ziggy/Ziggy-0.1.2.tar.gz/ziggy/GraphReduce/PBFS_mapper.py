#! /usr/bin/env python
'''
Created on Aug 12, 2010

@author: dwmclary
'''
import sys
import re

class BFSNode(object):
    def __init__(self, nID=None, distance=None, adj=None, path=None):
        if nID != None:
            self.nID = nID
            self.distance = distance
            self.adj = adj
            self.path = path
        
    def write(self):
        s = str(self.nID)+  " "+ " ".join(map(str,self.adj)) +\
         " d: "+str(self.distance) + " path: " + " ".join(map(str,self.path))
        return s
    
    def __str__(self):
        return self.write()
            
    
def read_adjacency(file, comment="#", sep=None):
    for line in file:
        line = line.rstrip()
        if line[0] != comment:
            entry = line.split(sep)
            nid = entry[0]
            if "d:" in entry:
                d_index = entry.index("d:")
                distance = float(entry[d_index+1])
                p_index = entry.index("path:")
                path = entry[p_index+1:]
                adj = entry[1:d_index]
            else:
                distance = float('inf')
                path = []
                adj = entry[1:]
                    
            node = BFSNode(nid,distance,adj, path) 
            yield node

    
#def main(n):
#    data = read_adjacency(sys.stdin)
#    M = {}
#    N = {}
#    for node in data:
#        if node.nID == n:
#            node.distance = 0.0
#            
#        d = node.distance
#        
#        print node.write()
#        
#        if node.distance < float('inf'):
#            M[node.nID] = node
#        else:
#            N[node.nID] = node
#    
#    for key in M.keys():
#        n = M[key]
#        for m in n.adj:
#            if m in N:
#                print N[m].nID + " pathlen: " + str(n.distance+1)

def main(n):
    data = read_adjacency(sys.stdin)
    for node in data:
        if node.nID == n:
            node.distance = 0.0
            print n + " pathlen: 0.0" + " path: "
        d = node.distance
        
        print node
        
        for m in node.adj:
            path = [node.nID] + node.path
            print m + " pathlen: " + str(d+1) + " path: " + ",".join(path)
        
    
            
            
        
if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except:
        pass
    source = open("pbfs_source").readlines()
    source = source[0].strip()
    main(source)
