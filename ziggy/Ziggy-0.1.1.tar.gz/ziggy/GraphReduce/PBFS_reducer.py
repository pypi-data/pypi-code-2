#! /usr/bin/env python
'''
Created on Aug 12, 2010

@author: dwmclary
'''
import sys

class BFSNode(object):
    def __init__(self, nID=None, distance=None, adj=None, path = None):
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
    
def read_map_output(file, sep=None):
    for line in file:
        line = line.rstrip().split()
        nid = line[0]

        if not "pathlen:" in line:
            type = "node"
            d_index = line.index("d:")+1
            distance = float(line[d_index])
            p_index = line.index("path:")
            if p_index > len(line)-1:
                path = line[p_index,:]
            else:
                path = []
            adj = line[1:d_index-1]
            node = BFSNode(nid, distance, adj, path)
            yield type, nid, node
        else:
            type = "distance"
            d_index = line.index("pathlen:")
            distance = line[d_index+1]
            p_index = line.index("path:")
            path = line[p_index+1:]
            yield type, nid, (distance, path)

        

def main():
    p_min = {}
    d_min = {}
    M = {}
    data = read_map_output(sys.stdin)
    inf_count = 0
    for type, key, value in data:
        if type == "distance":
            if key in d_min:
                if d_min[key] > value[0]:
                    d_min[key] = value[0]
                    p_min[key] = value[1]
                    
            else:
                d_min[key] = value[0]
                p_min[key] = value[1]
        elif type == "node":
            M[key] = value
    for key in M.keys():
        if key in d_min:
            M[key].distance = d_min[key]
            M[key].path = p_min[key]
            
        if M[key].distance == 'inf':
            M[key].path = ""
            inf_count +=1
        print M[key]
    print "#inf_count: "+str(inf_count)
    
        
        
if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()
