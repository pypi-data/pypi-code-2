'''
Created on Aug 11, 2010

@author: dwmclary
'''
import networkx as nx
from .. hdmc import hdfs
class GraphLoader():
    '''
    Provides graph handles in Hadoop MapReduce
    '''


    def __init__(self, G = None, graph_handle=None):
        '''
        Constructor
        '''
        
        if G != None:
            self.G = G
        #sets a string pointing to an flat-file adjacency list
        if graph_handle != None:
            self.graph_handle = graph_handle
        
    def read_edgelist(self, filename):
        self.G = nx.read_edgelist(filename)
        
    def read_adjlist(self, filename, undirected=True):
        if undirected:
            self.G = nx.read_adjlist(filename).to_undirected()
        else:
            self.G = nx.read_adjlist(filename)
        self.graph_handle = filename
        
    def write_adjlist(self, filename=None):
        if filename:
            nx.write_adjlist(self.G.to_directed(), filename)
            self.graph_handle = filename
            hdfs.mkdir(filename)
            hdfs.copyToHDFS(filename, filename+"/page_rank")
            #hdfs.copyToHDFS(filename, filename+"/shortest_path")
            hdfs.copyToHDFS(filename, filename+"/degree")
        else:
            if self.graph_handle:
                nx.write_adjlist(self.G.to_directed(), self.graph_handle)
        
    def write_edgelist(self, filename):
        nx.write_edgelist(self.G,filename)
        
    def in_hdfs(self):
        listing = hdfs.ls(self.graph_handle)["stdout"].split("\n")
        found = False
        disk_tail = self.graph_handle.split("/")[-1]
        for line in listing:
            hdfs_tail = line.split("/")[-1]
            if disk_tail == hdfs_tail:
                found = True
                break
        return found
    
        
