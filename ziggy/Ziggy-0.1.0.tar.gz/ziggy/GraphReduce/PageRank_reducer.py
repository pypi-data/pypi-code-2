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
    
def read_map_output(file, sep=None):
    for line in file:
        line = line.rstrip().split()
        nid = line[0]

        if "#lost_mass:" in line:
            print " ".join(line)
        elif not "pagerank:" in line:
            type = "node"
            pr_index = line.index("pr:")+1
            rank = float(line[pr_index])

            adj = line[1:pr_index-1]
            node = PRNode(nid, rank, adj)
            yield type, nid, node
        else:
            type = "pagerank"
            pr_index = line.index("pagerank:")
            rank = line[pr_index+1]
            yield type, nid, rank
            
def main():
    M = {}
    pr = {}
    data = read_map_output(sys.stdin)
    for type, key, value in data:
        if type == "node":
            M[key] = value
            if key not in pr:
                pr[key] = 0.0
        elif type == "pagerank":
            if key not in pr:
                pr[key] = 0.0
            pr[key] += float(value)
    for key in M.keys():
        if key in pr:
            M[key].page_rank = pr[key]
        print M[key]
        
if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()
