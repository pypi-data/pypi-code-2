#! /usr/bin/env python

import networkx as nx

import os
import glob
import sys
import pprint as pp

import urllib
import xml.etree.ElementTree as ET


import csv
import re
import optparse 
from time import strftime

#TODO: run pylint across this script, aim for 10/10
#todo: write main function

def convert_to_undirected(graph):
    if graph.is_multigraph():
        # When NetworkX converts from MultiDiGraph to MultiGraph, it will discard
        # an edge if it exists in both directions, eg (1,2) and (2,1) will discard
        # (2,1). For maps traced in yED, the existence of a link means it was 
        # deliberately added, and we wish to keep it. In the above example we wish to
        # have 2 edges between nodes 1 and 2. To do this, we need to manually add
        # another link from (1,2) and remove (2,1)
        for src, dst, key, data in graph.edges(data=True, keys=True):
            # See if reverse link
            if graph.has_edge(dst, src):
                # Reverse link exists, want all to go same direction
                # All edges for node pair need to originate from same node, 
                # choose lower node id to decide
                if src > dst:
                    # Switch the link
                    graph.add_edge(dst, src, attr_dict=data)
                    graph.remove_edge(src, dst, key)

    # Undirected version of graph (both single and multi edge)
    graph =  graph.to_undirected(graph)
    
    return nx.MultiGraph(graph)

def extract_edge_data(label):

    # Note starts off as label and is trimmed as data is extracted
    data = {'LinkLabel': label, 'LinkNote': label, 'LinkSpeedUnits': '', 'LinkType': '',
            'LinkSpeed': '', 'time': ''}

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
                data['LinkNote'] = data['LinkNote'].replace(speed, "")
                data['LinkNote'] = data['LinkNote'].replace(units, "")
                data['LinkNote'] = data['LinkNote'].replace(units_extra, "")
                #TODO: convert speed to float (can't be int as may have 3.2
                data['LinkSpeed'] = speed
                data['LinkSpeedUnits'] = units.upper()
                #print "extract: {0} {1}".format(m.group(1), m.group(2))

    #TODO: remove the above from ongoing label/note

    # Try to extract Type
    edge_types="OC-\d+|STM-\d+|SDH|Fib[e|r]{2}|Optical|GIGE|FE"
    edge_types += "|Ethernet|Satellite|Wireless|Microwave|Serial|ATM|MPLS"

    if len(re.findall(edge_types, label, re.IGNORECASE)) > 1:
        # Should only occur once -> ignore
        # see if occurs as type (over|via) type,
        # eg Ethernet over SDH, Ethernet over Satellite, etc
        over_via =  r"({0})\s(over|via)\s({0})".format(edge_types)
        m = re.search(over_via, label, re.IGNORECASE)
        if m:
            edge_type = m.group(0)
            data['LinkNote'] = data['LinkNote'].replace(edge_type, "")
            data['LinkType'] = edge_type
        else:
            # skip this entry as invalid
            pass
    else:
        m = re.search(edge_types, label, re.IGNORECASE)
        if m:
            edge_type = m.group(0)
            data['LinkNote'] = data['LinkNote'].replace(edge_type, "")
            # pretty up the type
            # eg ethernet -> Ethernet, ETHERNET -> Ethernet, STM -> STM (ie same)
            if not edge_type.isupper():
                # Not upper case, tidy up
                # Ignore all upper case, eg ATM, SDH, STM, etc
                edge_type = edge_type.title()
            data['LinkType'] = edge_type
    
    
    # Try to extract temporal information
    temporal = "Future|Planned|Current|Proposed"
    temporal += "|Planning|Under Construction|Under Development"
    m = re.search(temporal, label, re.IGNORECASE)
    if m:
        temporal_type = m.group(0)
        data['LinkNote'] = data['LinkNote'].replace(temporal_type, "")
        data['LinkStatus'] = temporal_type.title()

    # Tidying up: remove note if it is just punctuation
    # eg () or + left over from extraction
    if ( (len(data['LinkNote']) > 0) and
        (len(re.findall("\w+", data['LinkNote'], re.IGNORECASE)) == 0) ):
        # Non-trivial length and no alphanumeric characters present so wipe note
        data['LinkNote'] = ''
  
    # Remove any empty fields
    for key, val in data.items():
        if val == '':
            del data[key]
    # Don't include note if same as label - redundant
    if ('LinkNote' in data) and (data['LinkNote'] == data['LinkLabel']):
        del data['LinkNote']

    return data

def geocode_place_sql(place):
    # uses sqlite to find place
    conn = sqlite3.connect('~/czoo/geonames')
    print conn
    


def geocode_place(place, count=1, country=None, continentCode=None,
                  fuzzy=0, return_style="SHORT", feature_class="P"):
    results = []
    # P is featureClass for towns/villages/cities (eg not lakes, rivers, hills)
    options = "&maxRows={0}".format(count)
    if country:
        # use this country code
        options += "&country={0}".format(country)
    if fuzzy > 0:
        options += "&fuzzy={0}".format(fuzzy)

    # sanity check feature class
    if feature_class not in ['P', 'A']:
        print "Invalid style {0}".format(feature_class)
        # Set as geonames default
        feature_class = "P"
    options += "&featureClass={0}".format(feature_class)


    # sanity check
    if return_style not in ['SHORT', 'MEDIUM', 'LONG', 'FULL']:
        print "Invalid style {0}".format(return_style)
        # Set as geonames default
        return_style = "MEDIUM"
    options += "&style={0}".format(return_style)

    url = "http://ws.geonames.org/search?q=" + urllib.quote(place) + options
    dom = ET.parse(urllib.urlopen(url))
    geonames =  dom.findall("geoname")


    #print url
    for g in geonames:
        #print ET.dump(g)
        
        if g is None:
            print "No result for {0}".format(g)
            return
      
        # attributes we wish to search for
        attributes = [ "name", "countryCode", "lat", "lng",
                      "adminName1", "population", "countryName" ]
        place_data = {}

        for attr in attributes:
            try:
                value = g.find(attr)
                #print value.text
                # result found, extract string from unicode
                value = value.text
                value = value.encode('utf-8')
            except AttributeError, e:
                # Problem with attribute, use default
                value = ""

            place_data[attr] = value
        results.append(place_data)
    if len(results) == 0:
        # TODO: note in docstring that caller must handle case of no results
        return 

    #print results
    if count == 1:
        # return tuple of results, not a list
        return results[0]

    return results 


def geocode(graph):
    #TODO: do smart analysis to check places are nearby, find outliers
    # and check countries similar, etc
    # have option for interactive mode or auto guess mode

    #TODO: use the geo extent and geo location tags
    # eg if geo extent is country, then only all <5% nodes outside that country
    # and bias towards that country, etc
    # How fuzzy we accept results to be [0,1], lower = accept fuzzier answers 
    fuzzy = 0.6

    #TODO: check on cases where country code might choose from inside country,
    # when there may be one or two nodes outside the country
    # these need manual check
    # this can probably be picked up by average geo link length, and then
    # seeing which lie a few standard deviations out from the average length
    # may require tuning

    #TODO: if node has no co-ords, set to be the middle of the graph

    # See if set country bias
    #TODO: extend thisto support other classifications eg continent, region in
    # a country, etc
    country = None
    if 'GeoExtent' in graph.graph and graph.graph['GeoExtent'] == 'Country':
        # get country code
        #http://www.geonames.org/advanced-search.html?q=australia&country=&featureClass=A&continentCode=
        #country = 
        country = graph.graph['GeoLocation']
        geodata = geocode_place(country, feature_class='A')
        country = geodata['countryCode']  

    # can also use continent
    # http://www.geonames.org/advanced-search.html?q=blah&country=&featureClass=&continentCode=AS

    for index, (n, nodedata) in enumerate(graph.nodes(data=True)):
        print "Geocoding {0}".format(nodedata['label'])
        geodata = geocode_place(nodedata['label'],
                                fuzzy = fuzzy, country = country)
        #print geodata
        if geodata:
            graph.node[n]['Latitude'] =  float(geodata['lat'])
            graph.node[n]['Longitude'] = float(geodata['lng'])
        else:
            # No result found
            print "No geodata found for {0}".format(nodedata['label'])

    # for any nodes with no lat/long, set to be average of neighbors
    # and give warning
    #TODO: put this into converter as that is where you can choose to alter data
    # output of merge should be the network AS IS from the trace
    for n, data in graph.nodes(data=True):
        if 'Latitude' not in data or 'Longitude' not in data:
            # get neighbour's co-ords
            neigh_lats = []
            neigh_lngs = []
            for neigh in graph.neighbors(n):
                if 'Latitude' in graph.node[neigh]:
                    neigh_lats.append(graph.node[neigh]['Latitude'])
                if 'Longitude' in graph.node[neigh]:
                    neigh_lngs.append(graph.node[neigh]['Longitude'])

            if len(neigh_lats) == 0 or len(neigh_lngs) == 0:
                # No data for neighbors either
                #TODO: use centre of entire graph
                print "No geo data for neighbors of {0}".format(data['label'])
            else:
                lat_mean = float(sum(neigh_lats) / len(neigh_lats)) 
                lng_mean = float(sum(neigh_lngs) / len(neigh_lngs))
                graph.node[n]['Latitude'] = lat_mean
                graph.node[n]['Longitude'] = lng_mean

    return graph

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

    opt.add_option('--geocode', '-g',  action="store_true",
                   default=False,
                   help="Attempt to lookup co-ordinates")

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

    # Work out the classification tags
    valid_class_tags = []
    for data in metadata.values():
        # Extract tags for each network
        for tag in data['Classification'].split():
            # Space seperated, break apart and add to list
            valid_class_tags.append(tag)
    # Remove any question marks, as Testbed? is same tag as Testbed
    valid_class_tags = [tag.replace("?","") for tag in valid_class_tags]
    # Also remove any stray commas
    valid_class_tags = [tag.replace(",","") for tag in valid_class_tags]
    # Unique
    valid_class_tags = list(set(valid_class_tags))

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
        graph = convert_to_undirected(graph)

       
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


        #*********************************
        # Remove graphics data 
        #*********************************
       
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
                        
                    # Split classification up into sub parts
                    #TODO: remove classification from final dict (leave now
                    # as Hung's stats scripts depend on it in full)
                    if key == "Classification":
                        network_tags = value.split()
                        for tag in valid_class_tags:
                            if tag in network_tags:
                                # Network has this tag
                                graph.graph[tag] = 1
                            else:
                                # Network doesn't have this tag
                                graph.graph[tag] = 0



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
        #Geocoding (optional)
        #*********************************
        if options.geocode:
            graph = geocode(graph)

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
