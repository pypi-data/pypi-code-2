#! /usr/bin/env python

import networkx as nx

import os
import glob
import sys
import pprint as pp

import csv
import re
import optparse  

#TODO: run pylint across this script, aim for 10/10
#todo: write main function

def main():


    # Converts from yED traced file into cleaned GML
    # with optional CSV parameters

    opt = optparse.OptionParser()
    opt.add_option('--file', '-f', 
                help="Load data from FILE")

    opt.add_option('--directory', '-d', 
                help="process directory")

    opt.add_option('--csv', '-c', 
                help="CSV file for metadata")


    opt.add_option('--keep_graphics', action="store_true",
                   dest="keep_graphics", default=False,
                   help="Keep yEd graphics data")

    options, arguments = opt.parse_args()

    network_files = []
    if options.file:
        network_files.append(options.file)

    if options.directory:
        network_files = glob.glob(options.directory + "*.gml")

    if len(network_files) == 0:
        print "No files found. Please specify file or directory using -f or -d"
        sys.exit(0)


    if options.directory:
        path = options.directory
    elif options.file:
        path, filename = os.path.split(options.file)
    
    output_path = path + "/output"
    if not os.path.isdir(output_path):
        os.mkdir(output_path)  

    metadata = {}
    # Metadata to use from CSV
    metadata_headings = ["Network", "Geo Extent", "Geo Location", 
                         "Type", "Classification", "Last Access",
                        "Source", "Layer", "Date Obtained",
                        "Network Date", "Developed"]
    
    if options.csv:
        print "loading csv {0}".format(options.csv)
        csv_file = open( options.csv, "rb" )
        csv_reader = csv.DictReader( csv_file, delimiter=",", quotechar='"' )
        for line in csv_reader:
            if line["Filename"] != "":
                #print line["Filename"]
                network_name = line["Filename"].replace(".gml", "")
                metadata[network_name] = line

    for source_file in network_files:

        # Extract name of network from file path
        path, filename = os.path.split(source_file)
        network_name, extension = os.path.splitext(filename)

        print "Converting: {0}".format(network_name)

        graph = nx.read_gml(source_file)
        graph = graph.to_undirected()
        graph = nx.MultiGraph(graph)

        category_mappings = {
            #TODO: document these
            #TODO: clarify these vs previous minutes notes
            "ellipse": "internal",
            "triangle": "external",
            "rectangle": "internal",
            "roundrectangle": "internal", # also used as normal rectangle
            "diamond": "switch",
            "octagon": "uncertain",
            "hexagon": "uncertain",
        }

        #*********************************
        # Editing
        #*********************************

        # Set category for node
        for node, data in graph.nodes(data=True):
            if "graphics" in data and "type" in data["graphics"]:
                shape = data["graphics"]["type"]
                # Remove quotes from string
                shape = shape.replace("\"", "")
                #TODO: throw error if shape not in the allow mappings
                if shape not in category_mappings:
                    print "ERROR: Shape {0} for node {1} {2} \
                            not permitted".format(shape, node, data['label']) 
                category = category_mappings[shape]

                # Special case: if shape is octagon or hexagon, and has no label
                # then is used to represent a hyperedge central point
                if category == "uncertain" and data['label'] == "":
                    category = "Hyperedge Node"

                # Note need to append to graph itself
                # quote as yEd requires quoted strings
                graph.node[node]['category'] = category



        #*********************************
        # Apply key/legend nodes
        #*********************************
        # Check to see if any legend nodes, if so extract the name/color combo
        legend_keys = {}
        for node, data in graph.nodes(data=True):
            label = data['label']
            if label.find('Legend') != -1:
                # Find returns position of search string, -1 if not found
                # Format the label
                legend_key = label.replace("Legend:", "").strip()
                # Color corresponding to this key
                color = data['graphics']['fill']
                legend_keys[color] = legend_key 
                # Remove the legend node from graph as not a network node
                graph.remove_node(node)

        #TODO: document how to use "Legend:" and colours
        # Apply the legend to other nodes in graph
        if len(legend_keys) > 0:
            # Using legend keys, set node details appropriately
            for node, data in graph.nodes(data=True):
                if data['category'] == "Hyperedge Node":
                        # Don't apply color class to hyperedges
                        continue
                color = data['graphics']['fill']
                #TODO: check/catch color key being present in
                if color not in legend_keys:
                    print data['category']
                    print "Error: Color {0} for node {1} has no legend\
                            associated".format(color, data['label'])
                    continue
                legend_label = legend_keys[color]
                graph.node[node]['type'] = legend_label

        #*********************************
        # Remove graphics data 
        #*********************************
       
        # TODO: make this a command line option
        if options.keep_graphics is False:
            for node, data in graph.nodes(data=True):
                if "LabelGraphics" in data:
                    # Note we need to remove entry from graph itself
                    del graph.node[node]["LabelGraphics"]

                if "graphics" in data:
                    # Note we need to remove entry from graph itself
                    del graph.node[node]["graphics"]

            for src, dst, key, data in graph.edges(data=True, keys=True):
                # Need key as may be multiple edges between same node pair
                # also remove for edge formatting
                # Note need to remove entries from graph itself, not data
                if "graphics" in data:
                    del graph[src][dst][key]["graphics"]
                if "LabelGraphics" in data:
                    del graph[src][dst][key]["LabelGraphics"]
                if "edgeAnchor" in data:
                    del graph[src][dst][key]["edgeAnchor"]
        

   
        # Will be overwritten with name from metadata if present
        network_label = network_name 
        # insert metadata
        if network_name in metadata:
            network_label = metadata[network_name]['Network']

            # Insert into graph
            for key in metadata_headings:
                if key in metadata[network_name]:
                    value = metadata[network_name][key]
                    # Ensure key is in camelCase format
                    # as whitespace seperates key val in GML 
                    key = key.title()
                    key = key.replace(" ", "")
                    graph.graph[key] = value
        elif options.csv:
            # Not found, and using csv, give error
            print "Warning: {0} not found in metadata file".format(network_name)


        # Set other graph attributes
        graph.graph['Creator'] = "Topology Zoo"
        graph.graph['Version'] = "1.0"
        graph.graph['label'] = network_label 

        #*********************************
        #OUTPUT - Write the graphs to files
        #*********************************

        filename = network_label.lower().strip()
        filename = filename.title()
        filename = filename.replace(" ", "_")

        pattern = re.compile('[\W_]+')
        filename = pattern.sub('', filename)

        gml_file =  "{0}/{1}.gml".format(output_path, filename)
        nx.write_gml(graph, gml_file)
   
     
if __name__ == "__main__":
    main()



