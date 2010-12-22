#! /usr/bin/env python
'''
Created on Aug 18, 2010

@author: dwmclary
'''
import sys

class PRNode(object):
    def __init__(self, nID=None, rank_mass=None, adj=None):
        if nID != None:
            self.nID = nID
            self.page_rank = rank_mass
            self.adj = adj
            #self.path = path
        
    def write(self):
        s = str(self.nID)+  " "+ " ".join(map(str,self.adj)) +\
         " pr: "+str(self.page_rank) #+ " path: " + " ".join(map(str,self.path))
        return s
    
    def __str__(self):
        return self.write()
            
    
def read_adjacency(file, comment="#", sep=None,mass=None):
    for line in file:
        line = line.rstrip()
        if line[0] != comment:
            entry = line.split(sep)
            nid = entry[0]
            if "pr:" in entry:
                d_index = entry.index("pr:")
                rank_mass = float(entry[d_index+1])
#                p_index = entry.index("path:")
#                path = entry[p_index+1:]
                adj = entry[1:d_index]
            else:
                rank_mass = mass
                path = []
                adj = entry[1:]
                    
            node = PRNode(nid,rank_mass,adj) 
            yield nid, node
            
            
def main(rank_mass):
    data = read_adjacency(sys.stdin, sep=None, mass=rank_mass)
    lost_mass = 0.0
    for nid, node in data:
        p = node.page_rank/len(node.adj)
        
        print node
        for m in node.adj:
            print str(m) + " pagerank: " + str(p)
        if len(node.adj) == 0:
            lost_mass += node.page_rank
    print "#lost_mass: " + str(lost_mass)
            
if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except:
        pass
    source = open("rank_mass").readlines()
    source = source[0].strip()
    main(float(source))
        