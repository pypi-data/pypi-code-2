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
    
def read_map_output(file, sep=None):
    for line in file:
        line = line.rstrip().split()
        nid = line[0]

        if not "indegree:" in line:
            type = "node"
            d_index = line.index("in:")
            p_index = line.index("out:")
            in_degree = line[d_index+1:p_index]
            out_degree = line[p_index+1:]
            adj = line[1:d_index]
            node = DegreeNode(nid, in_degree, adj, out_degree)
            yield type, nid, node
        else:
            type = "degree"
            d_index = line.index("indegree:")
            in_degree = line[d_index+1]
            yield type, nid, in_degree
            
def main():
    in_degrees = {}
    M = {}
    changed = 0
    data = read_map_output(sys.stdin)
    for type, key, value in data:
        if type == "degree":
            if key in in_degrees:
                in_degrees[key].append(value)
                    
            else:
                in_degrees[key] = [value]
        elif type == "node":
            M[key] = value
    for key in M.keys():
        if key in in_degrees:
            degree_before = len(M[key].in_degree)
            M[key].in_degree = set(in_degrees[key]).union(M[key].in_degree)
            degree_after = len(M[key].in_degree)
            if degree_before != degree_after:
                changed +=1
        print M[key]
    print "#Changed:"+str(changed)
        
            
if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()