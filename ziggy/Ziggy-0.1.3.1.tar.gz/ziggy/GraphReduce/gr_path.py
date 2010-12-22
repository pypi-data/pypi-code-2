'''
Created on Aug 12, 2010

@author: dwmclary
'''

__author__ = "D. McClary (dan.mcclary@northwestern.edu)"
__all__ = ['out_degree', 'in_degree', 'average_degree', 'average_out_degree', 'average_in_degree',\
          ' connected_components', 'num_connected_components',\
           'single_source_shortest_path', 'single_source_shortest_path_length',\
           'shortest_path', 'shorested_path_length', 'average_shortest_path_length']
from .. import hdmc
from .. hdmc import hdfs
import hadoop_config as config
import networkx as nx
import os
import sys
import string
from GraphLoader import GraphLoader

def connected_components(G, name = None, recompute=False):
    '''Compute the connected components for a networkx graph G'''
    paths = shortest_path(G, None, None, name, recompute)
    components = []
    for p in paths.keys():
        found = False
        for c in components:
            if len(c.intersection(paths[p].keys())) > 0:
                c_index = components.index(c)
                components[c_index] = c.union(paths[p].keys())
                found = True
                break
        if not found:
            components.append(set(paths[p].keys()))
    return map(list, components)

def num_connected_components(G, name=None, recompute=False):
    '''Compute the number of connected components for the networkx graph G.'''
    components = connected_components(G, name, recompute)
    return len(components)

def single_source_shortest_path(G, source, target=None, name=None, recompute=False):
    '''Computer the shortest path from source to a target or all other nodes in the networkx graph G.'''
    if not recompute:
        distance, path = check_for_precomputed_bfs_result(G, name, source)
    else:
        print "at sssp, name = " + name
        distance, path = bfs(G, source, name)
    
    if target:
        try:
            target_path = path[target]
            return target_path
        except KeyError:
            return None
    else:
        for key in path.keys():
            if len(path[key]) == 0:
                del path[key]
    return path
    
def single_source_shortest_path_length(G, source, target=None, name=None, recompute=False):
    '''Computer the shortest path length from source to a target or all other nodes in the networkx graph G.'''
    if not recompute:
        distance, path = check_for_precomputed_bfs_result(G, name, source)
    else:
        distance, path = bfs(G, source, name)
    if target:
        try:
            target_distance = distance[target]
        except KeyError:
            return None
    else:
        for key in distance.keys():
            if distance[key] == float('inf'):
                del distance[key]
    return distance

def single_source_average_shortest_path_length(G, source, target=None, name=None, recompute=False):
    '''Computer the average shortest path length from source to a target or all other nodes in the networkx graph G.'''
    sum = 0.0
    count = 0
    if not recompute:
        distance, path = check_for_precomputed_bfs_result(G, name, source)
    else:
        distance, path = bfs(G, source, name)

    for key in distance.keys():
        if distance[key] != float('inf'):
            sum += distance[key]
        count += 1
    
    return sum/count
    
def shortest_path(G, source=None, target=None, name=None, recompute=False):
    '''Computer the shortest path from each node to all other nodes in the networkx graph G.
    A source and target can optionally passed to limit the search.'''
    if source:
        single_source_shortest_path(G, source, target, name, recompute)
    else:
        paths = {}
        for n in G.nodes():
            this_path = single_source_shortest_path(G, n, target, name, recompute)
            paths[n] = this_path
    return paths

def shortest_path_length(G, source=None, target=None, name=None, recompute=False):
    '''Computer the shortest path length from each node to all other nodes in the networkx graph G.
    A source and target can optionally passed to limit the search.'''
    if source:
        single_source_shortest_path(G, source, target, name, recompute)
    else:
        distances = {} 
        for n in G.nodes():
            this_distance = single_source_shortest_path_length(G, n, target, name, recompute)
            distances[n] = this_distance
    return distances

def average_shortest_path_length(G,name=None, recompute=False):
    '''Computer the average shortest path length from each node to all other nodes in the networkx graph G.
    '''
    sum = 0.0
    count = 0
    for n in G.nodes():
        sum += single_source_average_shortest_path_length(G, n, None, name, recompute)
        count += 1
    return sum/count

def average_out_degree(G, name=None):
    '''Compute the average out-degree for the networkx graph G.'''
    in_d, out_d = degree(G, name)
    average_out = float(sum(out_d.values()))/len(out_d.values())
    return average_out

def average_in_degree(G, name=None):
    '''Compute the average in-degree for the networkx graph G.'''
    in_d, out_d = degree(G, name)
    average_in = float(sum(in_d.values()))/len(in_d.values())
    return average_in

def average_degree(G, name=None):
    '''Compute the average degree for the networkx graph G.'''
    in_d, out_d = degree(G, name)
    average_out = sum(out_d.values())
    average_in = sum(in_d.values())
    return (average_out+average_in)/(float(len(out_d.values()))+float(len(in_d.values())))

def out_degree(G, name=None):
    '''Compute the out-degree for each node in the networkx graph G.'''
    in_d, out_d = degree(G, name)
    return out_d

def in_degree(G, name=None):
    '''Compute the in-degree for each node in the networkx graph G.'''
    in_d, out_d = degree(G, name)
    return in_d

def degree(G, name=None):
    '''Compute the degree for each node in the networkx graph G.'''
    G = GraphLoader(G)
    print name
    if name:
        G.write_adjlist(name)
    else:
        G.write_adjlist("pbfs_input.adjlist")
    hdfs_handle = G.graph_handle.split("/")[-1]
    hdfs.rm(hdfs_handle+"/degree")
    hdfs.copyToHDFS(G.graph_handle, hdfs_handle+"/degree/part-00000")
    in_degree, out_degree = parallel_degree(hdfs_handle)
    return in_degree, out_degree

def bfs(G, source, name=None):
    '''Conduct a parallel BFS from the source node to all other reachable nodes in G.'''
    source = str(source)
    os.system("echo "+source + " > pbfs_source")
    wd = config.GraphReduce_location
    inf_count = len(G)
    print "at bfs, name = " + name
    G = GraphLoader(G, name)
    if name:
        G.write_adjlist(name)
    else:
        G.write_adjlist("pbfs_input.adjlist")
    hdfs_handle = G.graph_handle.split("/")[-1]
    print G.graph_handle
    print hdfs_handle
    print "writing to " + hdfs_handle + "/" + source
    r = hdfs.rm(hdfs_handle+"/shortest_path/"+source)
    
    hdfs.mkdir(hdfs_handle+"/shortest_path/"+source)
    

    hdfs.copyToHDFS(G.graph_handle, hdfs_handle+"/shortest_path/"+source+"/part-00000")
    
    
    distance, path = parallel_bfs(source, hdfs_handle, inf_count)
    return distance, path

def parallel_degree(hdfs_handle):
    '''Compute node degree in parallel for the graph adjacency list stored in hdfs_handle.'''
    hdfs.rm("pdegree")
    base_path =  os.path.realpath( __file__ ).split("/")
    base_path = "/".join(base_path[0:-1])
    hadoop_call = hdmc.build_generic_hadoop_call(base_path+"/Degree_mapper.py", base_path+"/Degree_reducer.py", hdfs_handle+"/degree", "pdegree", [])
    hdmc.execute_and_wait(hadoop_call)
    # copy the output to the input
    hdfs.rm(hdfs_handle+"/degree/part*")
    hdfs.mv("pdegree/part*", hdfs_handle+"/degree/")
    hdfs.rm("pdegree")
    in_d, out_d = fetch_degree_from_hdfs(hdfs_handle)
    return in_d, out_d
    
    
    
def parallel_bfs(source, hdfs_handle, old_inf_count):
    '''Compute shortest path from source to all nodes in parallel for the graph adjacency list stored in hdfs_handle.'''
    hdfs.rm("PBFS-src-"+str(source))
    base_path =  os.path.realpath( __file__ ).split("/")
    base_path = "/".join(base_path[0:-1])
    hadoop_call = hdmc.build_generic_hadoop_call(base_path+"/PBFS_mapper.py", base_path+"/PBFS_reducer.py", hdfs_handle+"/shortest_path/"+source, "PBFS-src-"+str(source), ["pbfs_source"])
    hdmc.execute_and_wait(hadoop_call)
    listing = hdfs.ls("PBFS-src-"+str(source)+"/part*")["stdout"].rstrip().split("\n")
    inf_count = 0
    for entry in listing:
        last_part = entry.split("part-")
        tail = hdfs.tail("PBFS-src-"+str(source)+"/part-"+last_part[-1])["stdout"].split("\n")
    
        for line in tail:
            tail_entry = line.rstrip().split(":")
            if len(tail_entry) > 0:
                if tail_entry[0] == "#inf_count":
                    inf_count += int(tail_entry[1])
    
    # copy the output to the input
    hdfs.rm(hdfs_handle+"/shortest_path/"+source+"/part*")
    hdfs.mv("PBFS-src-"+str(source)+"/part*", hdfs_handle+"/shortest_path/"+source+"/")
    hdfs.rm("PBFS-src-"+str(source))
    if inf_count > 0 and old_inf_count > inf_count:
        results, paths = parallel_bfs(source, hdfs_handle, inf_count)
    else:
        results, paths = fetch_sp_from_hdfs(hdfs_handle, source)
    return results, paths

def fetch_sp_from_hdfs(hdfs_handle, source):
    '''Fetch shortest path results from HDFS.'''
    results = {}
    paths = {}
    output = hdfs.cat(hdfs_handle+"/shortest_path/"+source+"/part*")["stdout"].split("\n")
    for r in output:
        if len(r) > 0:
            if r[0] != "#":
                o = r.rstrip().split("d:")
                p = r.rstrip().split("path:")
                nodes = o[0].split()
                results[nodes[0]] = float(o[1].split()[0])
                paths[nodes[0]] = map(string.strip, p[-1].split(","))
                if '' in paths[nodes[0]]:
                    paths[nodes[0]].remove('')
    return results, paths

def fetch_degree_from_hdfs(hdfs_handle):
    '''Fetch degree results from HDFS.'''
    in_degrees = {}
    out_degrees = {}
    output = hdfs.cat(hdfs_handle+"/degree/part*")["stdout"].split("\n")
    for r in output:
        if len(r) > 0:
            if r[0] != "#":
                entry = r.split()
                key = entry[0]
                in_index = entry.index("in:")
                out_index = entry.index("out:")
                in_count = len(entry[in_index:out_index])
                out_count = len(entry[out_index:])
                in_degrees[key] = in_count
                out_degrees[key] = out_count
    return in_degrees, out_degrees

def check_for_precomputed_degree_result(G, name):
    '''Check to see if degree has been computed for the networkx graph G.'''
    if not name:
        name = "pbfs_input.adjlist"
    try:
        listing = hdfs.ls(name+'/degree')["stdout"].split("\n")
        in_d, out_d = fetch_degree_from_hdfs(name)
    except AttributeError:
        in_d= None
        out_d = None
    return in_d, out_d
        

def check_for_precomputed_bfs_result(G, name, source):
    '''Check to see if shortest path has been computed for the networkx graph G.'''
    #check for a precomputed result
    print "at check: " + name
    if not name:
        name = "pbfs_input.adjlist"
    listing = hdfs.ls(name+'/shortest_path')["stdout"].split("\n")
    result_exists = False
    for line in listing:
        entry = line.rstrip().split("/")[-1]
        if source == entry:
            result_exists = True
    if result_exists:
        distance, path = fetch_sp_from_hdfs(name, source)
    else:
        distance, path = bfs(G, source, name)
    return distance, path

    
