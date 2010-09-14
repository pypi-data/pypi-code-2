#! /usr/bin/env python
'''
Created on Aug 25, 2010

@author: dwmclary
'''

import sys

class DegreeNode(object):
    def __init__(self, nID=None, in_degree=None, adj=None, out_degree=None):
        if nID != None:
            self.nID = nID
            self.in_degree = in_degree
            self.adj = adj
            self.out_degree = out_degree
        
    def write(self):
        s = str(self.nID)+  " "+ " ".join(map(str,self.adj)) +\
        " in: "+" ".join(map(str, self.in_degree)) + " out: " + " ".join(map(str,self.out_degree))
        return s
    
    def __str__(self):
        return self.write()

def read_adjacency(file, comment="#", sep=None):
    for line in file:
        line = line.rstrip()
        if line[0] != comment:
            entry = line.split(sep)
            nid = entry[0]
            if "in:" in entry:
                d_index = entry.index("in:")
                p_index = entry.index("out:")
                in_degree = entry[d_index+1:p_index]
                out_degree = entry[p_index+1:]
                adj = entry[1:d_index]
            else:
                adj = entry[1:]
                out_degree = adj
                in_degree = []
            node = DegreeNode(nid,in_degree,adj, out_degree) 
            yield node
            
def main():
    data = read_adjacency(sys.stdin)
    for node in data:
        
        node.out_degree = node.adj
        print node
        for m in node.adj:
            print str(m) + " indegree: " + node.nID
        
if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except:
        pass
    main()
