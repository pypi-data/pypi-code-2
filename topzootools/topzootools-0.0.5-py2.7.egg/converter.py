#! /usr/bin/env python

import networkx as nx

import os
import glob
import sys
from time import strftime

import optparse  

from mako.lookup import TemplateLookup    
import zipfile

def matlab_keys(summary_data, output_path):
    matlab_keys = {}

    keys_to_use = ["Classification", "Type", "Layer", "GeoExtent",
                    "GeoLocation", "Developed", "Dataset", "NetworkData"]

    # Index of this network in the directory listing. Note: starting at 1
    network_index = 1
    file_index = {}
    for network, data in sorted(summary_data.items()):

        file_index[network_index] = network
        # look at each item
        for key, val in data.items():
        
            if key not in keys_to_use:
                # Not interested (eg source, version, etc), skip
                continue

            if key not in matlab_keys:
                matlab_keys[key] = {}
            
            if val not in matlab_keys[key]:
                matlab_keys[key][val] = []

            matlab_keys[key][val].append(network_index) 
        network_index += 1
    
    f_matlab_keys = open("{0}/matlab_keys.txt".format(output_path), "w")
    
    f_matlab_keys.write("*File Index\n")
    for key, val in sorted(file_index.items()):
        f_matlab_keys.write("{0} {1}\n".format(key, val))
    for heading, data in matlab_keys.items():
        f_matlab_keys.write("\n*" + heading + "\n")
        # do keys with names at end so can copy paste first bit into matlab
        keys_with_names = '\nNamed:\n'
        for key, values in data.items():
            if key == '':
                key = "No value"
            # Also list with names for double checking
            values_named = [file_index[x] for x in values]
            f_matlab_keys.write("{0} {1}\n".format(key, values))
            keys_with_names += "{0} [{1}]\n".format(key, 
                                                    ','.join(values_named))
        f_matlab_keys.write(keys_with_names)
    f_matlab_keys.close()


def main():
    opt = optparse.OptionParser()
    opt.add_option('--file', '-f', help="Load data from FILE")
    opt.add_option('--directory', '-d', help="process directory")
    opt.add_option('--output_dir', '-o', help="process directory")
    opt.add_option('--geoplot_dir', help="geoplot directory for gallery")
    # Graph options
    opt.add_option('--single_edge', action="store_true",
                   default=False, help="Reduce multi edges to single edge")
    opt.add_option('--internal_only', action="store_true",
                   default=False, help="Exclude external nodes")
    opt.add_option('--matlab_keys', action="store_true",
                   default=False, help="Generate list of keys for Matlab")
    # Output options
    opt.add_option('--matlab', action="store_true", default=False,
                   help="Write Matlab adjacency list Format")
    opt.add_option('--gml',  action="store_true", default=False, 
                   help="Write GML Format")
    opt.add_option('--graphml', action="store_true", default=False,
                   help="Write Graphml Format")
    opt.add_option('--dot', action="store_true", default=False, 
                   help="Write GraphViz dot Format")
    opt.add_option('--gexf', action="store_true", default=False,
                   help="Write GEXF Format")
    opt.add_option('--plot', action="store_true", default=False,
                   help="Plot graph")
    opt.add_option('--gallery', action="store_true", default=False,
                   help="Render gallery HTML")
    opt.add_option('--pickle', action="store_true", default=False,
                   help="Write NetworkX Pickle Format")
    opt.add_option('--archive', action="store_true", default=False,
                   help="Archive converted files")
    opt.add_option('--html', action="store_true", default=False, 
                   help="HTML summary")
    opt.add_option('--skip_type',  help="List of types to skip")
    options = opt.parse_args()[0]

    network_files = []
    if options.file:
        network_files.append(options.file)

    if options.directory:
        network_files = glob.glob(options.directory + "*.gml")

    if len(network_files) == 0:
        print "No files found. Please specify -f file or -d directory"
        sys.exit(0)

    if options.directory:
        path = options.directory
    elif options.file:
        path, filename = os.path.split(options.file)

    if options.output_dir:
        output_path = options.output_dir 
    else:
        output_path = path + "/converted"
    
    if not os.path.isdir(output_path):
        os.mkdir(output_path)  

    summary_data = {}

    archive_file =  None
    if options.archive:
        archive_filelist = []
        archive_file = "archive.zip"

    #These headings are used in HTML template, if not present then set to "" 
    metadata_headings = ["Network", "GeoExtent", "GeoLocation", 
                         "Type", "Classification", "LastAccess",
                        "Source", "Layer", "DateObtained",
                        "NetworkDate", "Note"]
    for net_file in network_files:

        # Extract name of network from file path
        path, filename = os.path.split(net_file)
        network_name = os.path.splitext(filename)[0]

        print "Converting: {0}".format(network_name)

        #if network_files.index(net_file) > 10:
        #    break

        graph = nx.read_gml(net_file)
        graph = graph.to_undirected()
        graph = nx.MultiGraph(graph)

        if options.skip_type:
            skip_type = options.skip_type
            print "Skipping {0}".format(skip_type)
            # Search for nodes with this type set
            for node, data in graph.nodes(data=True):
                if 'type' in data and data['type'] == skip_type:
                    graph.remove_node(node)

        if options.html or options.matlab_keys or options.gallery:
            summary_data[network_name] = {} 

            for key, val in graph.graph.items():
                # And also store in html data
                summary_data[network_name][key] = val

        #*********************************
        #Graphs - create different graphs for writing
        #*********************************
        if options.single_edge:
            # Graph with max one edge between any node pair
            graph = nx.Graph(graph)

        #TODO Update this to be true/false once netx fixes boolean quote bug
        if options.internal_only:
            external_nodes = [ n for n in graph.nodes()
                              if graph.node[n]['Internal'] == 0]
            graph.remove_nodes_from(external_nodes)
        # ************

        out_file = "{0}/{1}".format(output_path, network_name)
        # Append any custom options to filename
        if options.skip_type:
            #TODO Make sure only alphanumeric (safe file name) chars in filename
            out_file += "_skip_" + options.skip_type.lower()
        if options.single_edge:
            out_file += "_se" 
        if options.internal_only:
            out_file += "_int"

        #*********************************
        #OUTPUT - Write the graphs to files
        #*********************************
        if options.gml:
            #Add quotes
            gml_file =  out_file + ".gml"
            # workaround for bug where gml writer removes label from node
            #TODO: see if this is needed
            graph2 = graph.copy()
            nx.write_gml(graph2, gml_file)
            if options.archive:
                archive_filelist.append(gml_file)
   
        if options.graphml:
            graphml_file =  out_file + ".graphml"
            nx.write_graphml(graph, graphml_file)
            if options.archive:
                archive_filelist.append(graphml_file) 
     
        if options.dot:
            dot_file =  out_file + ".dot"
            nx.write_dot(graph, dot_file) 
            if options.archive:
                archive_filelist.append(dot_file)
        
        if options.gexf:
            gexf_file =  out_file + ".gexf"
            nx.write_gexf(graph, gexf_file) 
            if options.archive:
                archive_filelist.append(gexf_file)

        if options.pickle:
            pickle_file =  out_file + ".pickle"
            nx.write_gpickle(graph, pickle_file) 
            if options.archive:
                archive_filelist.append(pickle_file)

        #TODO: merge options.plot with geoplot
        # make geoplot part of this

        if options.matlab:
            # Write as a sparse matrix
            mat_file =  out_file + ".mat"
            mat_fh = open(out_file + ".txt", "w")
            if options.archive:
                archive_filelist.append(mat_file)
            sparse_matrix = nx.to_numpy_matrix(graph)

            # Write out manually (numpy.tofile() writes as all on one line)
            for line in sparse_matrix.tolist():
                # Convert list to a string format numbers as integers not floats
                line = [ str(int(x)) for x in line]
                mat_fh.write( " ".join(line) )
                mat_fh.write("\n")
            mat_fh.close()

    if options.matlab_keys:
        matlab_keys(summary_data, output_path)
            
    if options.html:
        #TODO: if matlab, plot, gml, graphml etc set, then provide hyperlink 
        date = strftime("%A %d %B %Y")
        # Set any missing entries to blank
        for network, data in summary_data.items():
            for key in metadata_headings:
                if key not in data:
                    summary_data[network][key] = ""
        lookup = TemplateLookup(directories=[ "templates" ],
                                module_directory="/tmp/mako_modules")       
        html_template = lookup.get_template("html.mako")
        f_html = open("{0}/dataset.html".format(output_path), "w")
        f_html.write(html_template.render(
            html_data = summary_data,
            metadata_headings = metadata_headings,
            archive_file = archive_file,
            date = date,
        ))    
        f_html.close()
       
    if options.gallery:
        #TODO: if matlab, plot, gml, graphml etc set, then provide hyperlink 
        # Set any missing entries to blank
        lookup = TemplateLookup(directories=[ "templates" ],
                                module_directory="/tmp/mako_modules")       
        gallery_template = lookup.get_template("gallery.mako")
        f_html = open("{0}/gallery.html".format(output_path), "w")
        f_html.write(gallery_template.render(
            html_data = summary_data
        ))    
        f_html.close()


    if options.archive:
        archive_fh = zipfile.ZipFile(
            "{0}/{1}".format(output_path, archive_file), "w")
        for name in archive_filelist:
            archive_fh.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
        archive_fh.close()
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass    
