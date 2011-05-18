#! /usr/bin/env python

import networkx as nx 
import os
import glob
import optparse
import sys
import pprint as pp

from geopy import distance

import re
import numpy as np


def distances(G):
    # Calculate distance for each edge
    for src, dst, data in G.edges(data=True):
        (x1, y1) = (G.node[src]['Latitude'], G.node[src]['Longitude'])
        (x2, y2) = (G.node[dst]['Latitude'], G.node[dst]['Longitude'])
        geo_dist = distance.distance( (x1, y1), (x2, y2))
        #print "{0} to {1} is {2}".format(G.node[src]['label'],
        #                                 G.node[dst]['label'],
        #                                 geo_dist.kilometers)
        # Store the distance on the edge
        G[src][dst]['weight'] = geo_dist.kilometers
    return G

opt = optparse.OptionParser()
opt.add_option('--directory', '-d', help="process directory")
opt.add_option('--file', '-f', help="process file")
opt.add_option('--output_dir', '-o', help="process directory")

options, args = opt.parse_args()

network_files = []

if options.file:
    network_files.append(options.file)

use_pickle = False
if options.directory:
    network_files = glob.glob(options.directory + "*.gml")

if len(network_files) == 0:
    # try pickle format
    #toDO: also make pickle work for single file - use extracted dir
    network_files = glob.glob(options.directory + "*.pickle")
    if len(network_files) > 0:
        use_pickle = True
    else:
        print "No files found. Please specify a -f file or -d directory"
        sys.exit(0)


if options.directory:
    filepath = options.directory
elif options.file:
    filepath, filename = os.path.split(options.file)

pickle_dir = filepath + "/cache"
if not os.path.isdir(pickle_dir):
    os.mkdir(pickle_dir)

for net_file in sorted(network_files):
    # Extract name of network from file path
    filepath, filename = os.path.split(net_file)
    network_name, extension = os.path.splitext(filename)
    print "\nNetwork: {0}".format(network_name)

    pickle_file = "{0}/{1}.pickle".format(pickle_dir, network_name)
    if (os.path.isfile(pickle_file) and
        os.stat(net_file).st_mtime < os.stat(pickle_file).st_mtime):
        # Pickle file exists, and source_file is older
        G = nx.read_gpickle(pickle_file)
    else:
        # No pickle file, or is outdated
        G = nx.read_gml(net_file)
        nx.write_gpickle(G, pickle_file)
 
    # Convert to single-edge and undirected
    G = nx.Graph(G)

    # Remove any external nodes
    external_nodes = [n for n, data in G.nodes(data=True)
                      if 'Internal' in data and data['Internal'] == 0]
    G.remove_nodes_from(external_nodes)

    hyperedge_nodes = [n for n, data in G.nodes(data=True) if 'hyperedge' in
                          data and data['hyperedge'] == 1]

    # Take subgraph so can split into connected components
    he_subgraph = G.subgraph(hyperedge_nodes)
    # Break into connected components
    for he_connected in nx.connected_components(he_subgraph):
        # Get all nodes connected to these hyperedges
        neigh_list = []
        for node in he_connected:
            # Neighbors that are not hyperedges
            neigh_list += [neigh for neigh in G.neighbors(node) if neigh not in
                          hyperedge_nodes]

        # Create clique between these neighbors
        # Use subgraph to retain node properties (lat/long for distance calcs)
        G_clique = nx.subgraph(G, neigh_list)
        # Remove all edges, as want clique
        G_clique.remove_edges_from(G_clique.edges())
        # Edge between all node pairs, but no self-edges
        edges_to_add = [(a,b) for a in neigh_list for b in neigh_list if a != b]
        G_clique.add_edges_from(edges_to_add)
        # Calculate distances for these edges
        G_clique = distances(G_clique)
        print G_clique.edges(data=True)
        # Find MST
        G_mst = nx.minimum_spanning_tree(G_clique)
        print ", ".join( [ (G.node[s]['label'] + " <-> " + G.node[t]['label'])
                          for s, t in G_mst.edges()])

        # TODO: Compare these two measures for distances
        # TODO: Apply to the main graph

    geocoded_cities = [ n for n, data in G.nodes(data = True)
                if 'Latitude' in data and 'Longitude' in data]

    # Check all nodes geocoded
    if G.number_of_nodes() != len(geocoded_cities):
        print ("Error: not all nodes in {0} geocoded."
               "Skipping").format(network_name)
        print "%d/%d geocoded" % (len(geocoded_cities), G.number_of_nodes())
        continue
        # Get list of non-geocoded nodes

    if not nx.is_connected(G):
        print "not connected"
        #print nx.connected_components(G)
        continue


    G = distances(G)

    ave_length = nx.average_shortest_path_length(G, weighted=True)
    print "Average length: %d km" % ave_length

    # This is inefficient, but netx doesn't appear to have a function that 
    # returns both distance and path
    dists = nx.all_pairs_dijkstra_path_length(G)
    #paths = nx.all_pairs_dijkstra_path(G)
    import pprint
    #pprint.pprint(dists)

    # Find the longest path in network
    curr_best = 0
    best_pair = None
    for src, data in dists.items():
        for dst, length in data.items():
            if length > curr_best:
                curr_best = length
                best_pair = (src, dst)

    print "Longest path is %d km from %s to %s" % (curr_best,
                                                G.node[best_pair[0]]['label'],
                                                G.node[best_pair[1]]['label'])

    # And find the path taken from these nodes
    path = nx.shortest_path(G, best_pair[0], best_pair[1])
    path_country = [G.node[n]['Country'] for n in path] 
    if len(set(path_country)) > 1:
        # More than one country in path (ie more than one unique element)
        print "via " + ", ".join(path_country)
    else:
        # All elements the same, print only the first
        print "All within %s" % path_country[0]





