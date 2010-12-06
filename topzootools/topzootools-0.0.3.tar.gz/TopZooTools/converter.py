#! /usr/bin/env python

import networkx as nx

import os
import glob
import sys
import pyparsing
import numpy

import pprint as pp

import itertools
import unicodedata as ud

import matplotlib.pyplot as plt
import matplotlib.pylab as pylab

import optparse  

#TODO: run pylint across this script, aim for 10/10
#todo: write main function

def main():

    opt = optparse.OptionParser()
    opt.add_option('--file', '-f', 
                help="Load data from FILE")

    opt.add_option('--directory', '-d', 
                help="process directory")

    #TODO: see if cam remove dest if same as the switch

    # Output options
    opt.add_option('--matlab', action="store_true", dest="matlab",
                default=False, help="Write Matlab adjacency list format")
    opt.add_option('--gml',  action="store_true", dest="gml",
                default=False, help="Write GML format")
    opt.add_option('--graphml', action="store_true", dest="graphml", 
                default=False, help="Write Graphml format")
    opt.add_option('--dot', action="store_true", dest="dot", 
                default=False, help="Write GraphViz dot format")
    opt.add_option('--plot', action="store_true", dest="plot", 
                default=False, help="Plot graph")


    # Graph options
    opt.add_option('--single_edge', action="store_true", dest="single_edge", 
                   default=False, help="Reduce multi edges to single edge")
    opt.add_option('--internal_only', action="store_true", dest="internal_only",
                   default=False, help="Exclude external nodes")

    opt.add_option('--matlab_keys', action="store_true", dest="matlab_keys",
                   default=False, help="Generate list of keys for Matlab")

    #TODO: implement report
    opt.add_option('--report', action="store_true", dest="report", 
                default=False, help="Report on the graph")

    opt.add_option('--html', action="store_true", dest="html", 
                default=False, help="HTML summary")

    opt.add_option('--skip_type',  
                help="List of types to skip")
    options, arguments = opt.parse_args()


    network_files = []
    if options.file:
        network_files.append(options.file)

    if options.directory:
        network_files = glob.glob(options.directory + "*.gml")

    if len(network_files) == 0:
        print "No files found. Please specify a file or directory using -f or -d"
        sys.exit(0)


    if options.directory:
        path = options.directory
    elif options.file:
        path, filename = os.path.split(options.file)
    
    output_path = path + "/converted"
    if not os.path.isdir(output_path):
        os.mkdir(output_path)  

    summary_data = {}


    metadata = {}
    #TODO: look at scrapping these and just using keys present in graph
    metadata_headings = ["Network", "GeoExtent", "GeoLocation", 
                         "Type", "Classification", "LastAccess",
                        "Source", "Layer", "DateObtained",
                        "NetworkDate"]
    for file in network_files:

        #TODO: remove this speed hack for testing 
        if len(summary_data) > 150:
            print "testing speed hack: stop at 5 networks"
            break

        # Extract name of network from file path
        path, filename = os.path.split(file)
        network_name, extension = os.path.splitext(filename)

        print "Converting: {0}".format(network_name)

        G = nx.read_gml(file)
        G = G.to_undirected()
        G = nx.MultiGraph(G)

        if options.skip_type:
            skip_type = options.skip_type
            print "Skipping {0}".format(skip_type)
            # Search for nodes with this type set
            for n, data in G.nodes(data=True):
                if 'type' in data and data['type'] == skip_type:
                    G.remove_node(n)

        if options.html or options.matlab_keys:
            summary_data[network_name] = {} 

            for key, val in G.graph.items():
                # And also store in html data
                summary_data[network_name][key] = val

        ## Graphs
            # Create graphs

            #TODO: make this dependent on command line arguments
        #*********************************
        #Graphs - create different graphs for writing
        #*********************************
        if options.single_edge:
            # Graph with max one edge between any node pair
            G = nx.Graph(G)

        #TODO Update this to be true/false once netx fixes boolean quote bug
        if options.internal_only:
            external_nodes = [ n for n in G.nodes()
                              if G.node[n]['Internal'] == 0]
            G.remove_nodes_from(external_nodes)
        # ************

        out_file = "{0}/{1}".format(output_path, network_name)
        # Also append any custom options to filename
        if options.skip_type:
            #TODO Make sure only alphanumeric (safe file name)characters present in filename
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
            nx.write_gml(G, gml_file)
   
        if options.graphml:
            graphml_file =  out_file + ".graphml"
            nx.write_graphml(G, graphml_file)
        
        if options.dot:
            dot_file =  out_file + ".dot"
            nx.write_dot(G, dot_file) 

        if options.plot:
            #Testing pygraphviz
            G_plot = G_write.copy()
            
            keys = [x for x in G_plot.graph]
            for k in keys:
                del G_plot.graph[k]

            for n, data in G_plot.nodes(data=True):
                print data
                for k in [k for k in data]:
                    del G_plot.node[n][k]
                                    

            for s, t, index, data in G_plot.edges(data=True, keys=True):
                for k in [k for k in data]:
                    del G_plot[s][t][index][k]

            import pygraphviz as pgv
            A = nx.to_agraph(G_plot)
            print A.string()

        if options.plot and False:
            # set plot graph explicitly
            G_plot = G_internal_single_edge

            #pos=nx.graphviz_layout(G_plot ,prog='twopi', args='')
            #pos=nx.circular_layout(G_plot)
            #pos=nx.shell_layout(G_plot)
            pos=nx.spring_layout(G_plot, iterations=500)
            #pos=nx.pydot_layout(G_plot,prog='dot', args='-Grotate=90') 

            plt.figure()
            # Dictionary of format "node key": "node label"
            labels_key = [n for n in G_plot.nodes() ]
            labels_val = [ data['label'].strip("\"")
                          for n, data in G_plot.nodes(data=True) ]
            labels = dict(zip(labels_key, labels_val))

            nx.draw(G_plot, pos=pos, 
                    #nodes
                    node_size=400, node_color="0.8",
                    #node labels
                    with_labels=True, labels=labels, font_weight="normal",
                    font_size=10,
                    #edges
                    linewidths=(0,0),
                    edge_color="0.6")
           
            font = {'fontname'   : 'Helvetica',
            'color'      : 'k',
            'fontweight' : 'bold',
            'fontsize'   : 18}
           
            plt.title(network_name, font)
            plt.axis('off')

            plot_file_png = open("{0}/{1}.png".format(output_path, network_name), "w")
            plt.savefig( plot_file_png )
            plot_file_pdf = open("{0}/{1}.pdf".format(output_path, network_name), "w")
            plt.savefig( plot_file_pdf, format="pdf" )
            

        # Write as a sparse matrix
        if options.matlab:
            mat_file = open(out_file + ".txt", "w")
            sparse_matrix = nx.to_numpy_matrix(G)

            # Write out manually (numpy.tofile() writes as all on one line)
            for line in sparse_matrix.tolist():
                # Convert list to a string, format numbers as integers not floats
                line = [ str(int(x)) for x in line]
                mat_file.write( " ".join(line) )
                mat_file.write("\n")
            mat_file.close()


    if options.matlab_keys:
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
    
    if options.html:
        #TODO: if matlab, plot, gml, graphml etc set, then provide hyperlink to them

        from mako.lookup import TemplateLookup    
        lookup = TemplateLookup(directories=[ "templates" ],
            module_directory="/tmp/mako_modules")       
        html_template = lookup.get_template("html.mako")
        f_html = open("{0}/summary.html".format(output_path), "w")
        f_html.write(html_template.render(
            html_data = summary_data,
            metadata_headings = metadata_headings 
        ))    
        f_html.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass    
