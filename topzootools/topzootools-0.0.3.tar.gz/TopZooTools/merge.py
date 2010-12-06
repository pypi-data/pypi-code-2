#! /usr/bin/env python

import networkx as nx

import os
import glob
import sys
import pprint as pp

import csv
import re
import optparse 
from time import strftime

#TODO: run pylint across this script, aim for 10/10
#todo: write main function


def extract_edge_data(label):

    # Note starts off as label and is trimmed as data is extracted
    data = {'Label': label, 'Note': label, 'Units': '', 'Type': '',
            'Speed': '', 'time': ''}

    extract_speed = True

    #TODO: try with regex compile to see if faster
    # (and move out of function back into main and compile outside loop)

    #TODO: see if can remove the first check

    # Note: Could likely optimise the following into a single regexp
    # Skip speed if ambiguities, ie if - or + present and not in STM- or OC-
    if re.search(r"-+", label):
        # Contains + or -
        # Remove OC- and STM- and check if still contains - 
        temp = re.sub(r"OC-\d+|STM-\d+", "", label)
        if re.search(r"-+", temp):
            # label contains - or + not inside OC- or STM-, so skip speed
            extract_speed = False
      
    num_units = "(\d+\.*\d*)\s*(k|K|m|M|g|G|t|T)(b?p?/?s?)"
    speed_invalidators = "[>|<|<=|>=|=>|=<|*|x|-]"
    if extract_speed:
        if re.search( speed_invalidators+"\s*"+num_units, label, re.IGNORECASE):
            # eg >45Mbps, <=1gbps, 2x>2.5G, etc
            # Ambiguous as to actual speed -> skip
            pass
        elif len(re.findall(num_units, label, re.IGNORECASE)) > 1:
            # Speed should only occur once
            pass
        else:
            # Try and extract units if present
            m = re.search(num_units, label, re.IGNORECASE)
            if m:
                speed = m.group(1)
                units = m.group(2)
                # Get the bps bp/s bit as well to remove from note 
                units_extra = m.group(3)
                data['Note'] = data['Note'].replace(speed, "")
                data['Note'] = data['Note'].replace(units, "")
                data['Note'] = data['Note'].replace(units_extra, "")
                #TODO: convert speed to float (can't be int as may have 3.2
                data['Speed'] = speed
                data['Units'] = units.upper()
                #print "extract: {0} {1}".format(m.group(1), m.group(2))

    #TODO: remove the above from ongoing label/note

    # Try to extract Type
    edge_types="OC-\d+|STM-\d+|SDH|Fib[e|r]{2}|Optical|GIGE|FE|Ethernet|Satellite|Wireless|Microwave|Serial|ATM|MPLS"

    if len(re.findall(edge_types, label, re.IGNORECASE)) > 1:
        # Should only occur once -> ignore
        # see if occurs as type (over|via) type,
        # eg Ethernet over SDH, Ethernet over Satellite, etc
        over_via =  r"({0})\s(over|via)\s({0})".format(edge_types)
        m = re.search(over_via, label, re.IGNORECASE)
        if m:
            edge_type = m.group(0)
            data['Note'] = data['Note'].replace(edge_type, "")
            data['Type'] = edge_type
        else:
            # skip this entry as invalid
            pass
    else:
        m = re.search(edge_types, label, re.IGNORECASE)
        if m:
            edge_type = m.group(0)
            data['Note'] = data['Note'].replace(edge_type, "")
            # pretty up the type
            # eg ethernet -> Ethernet, ETHERNET -> Ethernet, STM -> STM (ie same)
            if not edge_type.isupper():
                # Not upper case, tidy up
                # Ignore all upper case, eg ATM, SDH, STM, etc
                edge_type = edge_type.title()
            data['Type'] = edge_type
    
    
    # Try to extract temporal information
    temporal = "Future|Planned|Current|Proposed|Planning|Under Construction"
    m = re.search(temporal, label, re.IGNORECASE)
    if m:
        temporal_type = m.group(0)
        data['Note'] = data['Note'].replace(temporal_type, "")
        data['Time'] = temporal_type.title()

    # Tidying up: remove note if it is just punctuation
    # eg () or + left over from extraction
    if (len(data['Note']) > 0) and (len(re.findall("\w+", data['Note'], re.IGNORECASE)) == 0):
        # Non-trivial length and no alphanumeric characters present so wipe note
        data['Note'] = ''
  
    # Remove any empty fields
    for key, val in data.items():
        if val == '':
            del data[key]
    # Don't include note if same as label - redundant
    if ('Note' in data) and (data['Note'] == data['Label']):
        del data['Note']

    return data


def main():


    # Converts from yED traced file into cleaned GML
    # with optional CSV parameters

    opt = optparse.OptionParser()
    opt.add_option('--file', '-f', 
                help="Load data from FILE")

    opt.add_option('--directory', '-d', 
                help="process directory")


    opt.add_option('--output_dir', '-o', 
                help="process directory")

    opt.add_option('--csv', '-c', 
                help="CSV file for metadata")

    opt.add_option('--dataset_only', action="store_true",
                   dest="dataset_only", default=False,
                   help="Only use entries marked True in dataset column of csv")

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
   
    if options.output_dir:
        output_path = options.output_dir 
    else:
        output_path = path + "/merged"
   
    if options.dataset_only:
        output_path += "_dataset_only"

    #output_path += strftime("%Y%m%d_%H%M%S")
    if not os.path.isdir(output_path):
        os.mkdir(output_path)  


    # sanity check
    if options.dataset_only and not options.csv:
        print "\nWARNING: Can only use dataset_only if CSV file specified"

    metadata = {}
    # Metadata to use from CSV
    metadata_headings = ["Network", "Geo Extent", "Geo Location", 
                         "Type", "Classification", "Last Access",
                        "Source", "Layer", "Date Obtained",
                        "Network Date", "Developed"]
    
    if options.csv:
        #TODO: check csv file exists
        csv_file = open( options.csv, "rb" )
        csv_reader = csv.DictReader( csv_file, delimiter=",", quotechar='"' )
        for line in csv_reader:
            if line["Filename"] != "":
                net_name = line["Filename"].replace(".gml", "")
                metadata[net_name] = line
        print "Loaded csv {0}".format(options.csv)

    for source_file in network_files:

        # Extract name of network from file path
        path, filename = os.path.split(source_file)
        net_name, extension = os.path.splitext(filename)
        print "{0}".format(net_name)

        proceed = True
        if options.dataset_only:
            skip_net = False
            if net_name not in metadata:
                print "{0} not in metadata, skipping as assume not in dataset".format(net_name)
                skip_net = True
            if ( net_name in metadata 
                and 'Dataset' in metadata[net_name]):
                true_vals = "Yes|True|1"
                value = metadata[net_name]['Dataset']
                m = re.search(true_vals, value, re.IGNORECASE)
                if not m:
                    # Network not in dataset
                    print "{0} not in dataset, skipping".format(net_name)
                    skip_net = True 

            if skip_net:
                continue
        #TODO: check order here when converting to multi graph and undirected 
        graph = nx.read_gml(source_file)
        graph = graph.to_undirected()
        graph = nx.MultiGraph(graph)

        # Check for self loops
        for n, data in graph.nodes(data=True):
            if n in graph.neighbors(n):
                print "WARNING: Self loop {0} {1}".format(data['label'], n)

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


        #TODO: convert 1 and 0 into True and False once 
        # netx writing bug resolved (booleans text but not quoted)

        # Set category for node
        for node, data in graph.nodes(data=True):
            graph.node[node]['Internal'] = 1 

            if "graphics" in data and "type" in data["graphics"]:
                shape = data["graphics"]["type"]
                #TODO: remove all diamonds from source files
                if shape == "diamond":
                    print "Node {0}".format(data['label'])
                    print "Warning: diamond shape no longer supported"
                
                if shape == "triangle":
                    graph.node[node]['Internal'] = 0 

                #TODO: replace octagons for hyperedges with diamonds
                # As currently have overloaded the doubt and hyperedge symbols
                if shape == "octagon" or shape == "hexagon":
                    # Check if hyperedge or doubted node
                    if data['label'] == '':
                        graph.node[node]['hyperedge'] = 1 
                    else:
                        # Unsure about this node
                        graph.node[node]['doubted'] = 1



        #*********************************
        # Apply key/legend nodes
        #*********************************
        # Check to see if any legend nodes, if so extract the shape/color combo
        legend_keys = {}
        for node, data in graph.nodes(data=True):
            label = data['label']
            if label.find('Legend') != -1:
                # Find returns position of search string, -1 if not found
                # Format the label
                legend_key = label.replace("Legend:", "").strip()
                # Color corresponding to this key
                color = data['graphics']['fill']
                shape = data['graphics']['type']
                if shape not in legend_keys:
                    legend_keys[shape] = {}
                legend_keys[shape][color] = legend_key 
                # Remove the legend node from graph as not a network node
                graph.remove_node(node)

        #TODO: document how to use "Legend:" and colours
        # Apply the legend to other nodes in graph
        if len(legend_keys) > 0:
            # Using legend keys, set node details appropriately
            for node, data in graph.nodes(data=True):
                if 'hyperedge' in data:
                        # Don't apply color class to hyperedges
                        continue
                color = data['graphics']['fill']
                shape = data['graphics']['type']

                #TODO: check/catch color key being present in
                if shape in legend_keys and color in legend_keys[shape]:
                    legend_label = legend_keys[shape][color]
                    graph.node[node]['type'] = legend_label
                else:
                    # Ignore default color FFCC00 (yellow)
                    if color != "#FFCC00":
                        print "Error: Color {0} for node {1} has no legend associated".format(color, data['label'])
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
        network_label = net_name

        # extract edge data
        for src, dst, key, data in graph.edges(data=True, keys=True):
            if 'label' in data:
                label = data['label']
                extracted_data = extract_edge_data(label)
                # Replace the edge data with extracted
                graph.edge[src][dst][key] = extracted_data


        # insert metadata
        if net_name in metadata:
            network_label = metadata[net_name]['Network']

            # Insert into graph
            for key in metadata_headings:
                if key in metadata[net_name]:
                    value = metadata[net_name][key]
                    # Ensure key is in camelCase format
                    # as whitespace seperates key val in GML 
                    key = key.title()
                    key = key.replace(" ", "")
                    graph.graph[key] = value
        elif options.csv:
            # Not found, and using csv, give error
            print "Warning: {0} not found in metadata file".format(net_name)

        # Strip & as yEd fails on it
        network_label_clean = network_label.replace("&", "and")
        
        # Set other graph attributes
        graph.graph['Creator'] = "Topology Zoo Toolset"
        graph.graph['Version'] = "1.0"

        graph.graph['label'] = network_label_clean

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
    try:
        main()
    except KeyboardInterrupt:
        pass    
