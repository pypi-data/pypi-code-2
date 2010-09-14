'''
Created on Aug 18, 2010

@author: dwmclary
'''
__author__ = "D. McClary (dan.mcclary@northwestern.edu)"
from .. import hdmc
from .. hdmc import hdfs
import hadoop_config as config
import networkx as nx
import os
import sys
import string
from GraphLoader import GraphLoader

def page_rank(G, name=None, max_iterations=10):
    '''Compute page rank in parallel for the networkx graph G.'''
    
    wd = config.GraphReduce_location
    ranks = dict(zip(map(str,G.nodes()),[1.0/len(G)]*len(G)))
    G = GraphLoader(G)
    if name:
        G.write_adjlist(name)
    else:
        G.write_adjlist("pbfs_input.adjlist")
    hdfs_handle = G.graph_handle.split("/")[-1]
    hdfs.rm(hdfs_handle+"/page_rank")
    hdfs.copyToHDFS(G.graph_handle, hdfs_handle+"/page_rank/part-00000")
    ranking = parallel_page_rank(G,hdfs_handle, ranks, 0, max_iterations)
    return ranking

def parallel_page_rank(G, hdfs_handle, old_ranks, iterations, max_iterations):
    '''Compute page rank in parallel for the networkx graph G.'''
    hdfs.rm("PPR")
    base_path =  os.path.realpath( __file__ ).split("/")
    base_path = "/".join(base_path[0:-1])
    hadoop_call = hdmc.build_generic_hadoop_call(base_path+"/PageRank_mapper.py", base_path+"/PageRank_reducer.py", hdfs_handle+"/page_rank", "PPR", ["rank_mass"])
    hdmc.execute_and_wait(hadoop_call)
    listing = hdfs.ls("PPR/part*")["stdout"].rstrip().split("\n")
    for entry in listing:
        last_part = entry.split("part-")
        data = hdfs.cat("PPR/part-"+last_part[-1])["stdout"].split("\n")
        lost_mass = 0.0
        for line in data:
            line = line.strip().split()
            if "#lost_mass:" in line:
                lost_mass += float(line[1])
        os.system("echo " + str(lost_mass) + " > lost_mass")
        # copy the output to the input
        hdfs.rm(hdfs_handle+"/page_rank/part*")
        hdfs.mv("PPR/part*", hdfs_handle+"/page_rank/")
        hdfs.rm("PPR")
        hadoop_call = hdmc.build_generic_hadoop_call(base_path+"/LostMass_mapper.py", base_path+"/LostMass_reducer.py", hdfs_handle+"/page_rank", "PPR", ["rank_mass", "lost_mass"])
        hdmc.execute_and_wait(hadoop_call)

        
    for entry in listing:
        last_part = entry.split("part-")
        data = hdfs.cat("PPR/part-"+last_part[-1])["stdout"].split("\n")
        rank_sum = 0.0
        ranks= {}
        for line in data:
            pr_value = line.strip().split("pr:")
            if len(pr_value) > 1:
                rank = float(pr_value[-1])
                node = pr_value[0].split()[0]
                ranks[node] = rank
                rank_sum+= rank
    
        converged = True
        for key in ranks.keys():
            if abs(ranks[key] - old_ranks[key]) > 0.0001:
                converged = False
                break
                
    iterations += 1
    # copy the output to the input
    hdfs.rm(hdfs_handle+"/page_rank/part*")
    hdfs.mv("PPR/part*", hdfs_handle+"/page_rank/")
    hdfs.rm("PPR")
    
    if not converged and iterations < max_iterations:
        return parallel_page_rank(G, hdfs_handle, ranks, iterations, max_iterations)
    else:
        return ranks
