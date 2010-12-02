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
    
    output_path = path + "/output"
    if not os.path.isdir(output_path):
        os.mkdir(output_path)  

    summary_data = {}


    metadata = {}
    metadata_headings = ["Network", "GeoExtent", "GeoLocation", 
                         "Type", "Classification", "LastAccess",
                        "Source", "Layer", "DateObtained",
                        "NetworkDate"]
    for file in network_files:

        #TODO: remove this speed hack for generating html
        if len(summary_data) > 1000:
            print "html speed hack: stop at 5 networks"
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

        #TODO: remove following as should have been removed by merge script

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
        for n,data in G.nodes(data=True):
            if "graphics" in data and "type" in data["graphics"]:
                shape = data["graphics"]["type"]
                # Remove quotes from string
                shape = shape.replace("\"", "")
                #TODO: throw error if shape not in the allow mappings
                if shape not in category_mappings:
                    print "ERROR: Shape {0} for node {1} {2} not in allowed shapes".format(shape, n, data['label']) 
                category = category_mappings[shape]

                # Special case: if shape is octagon or hexagon, and has no label
                # then is used to represent a hyperedge central point
                if category == "Uncertain" and data['label'] == "":
                    category = "Hyperedge Node"

                # Note need to append to graph itself
                # quote as yEd requires quoted strings
                G.node[n]['category'] = category

        
        # First get the node x,y for use in plotting
        if options.plot:
            orig_pos = {}
            for n,data in G.nodes(data=True):
                if "graphics" in data:
                    x = data["graphics"]['x']
                    # Invert y axis as matplotlib uses Matlab co-ord system
                    y = -1 * data["graphics"]['y']
                    orig_pos[n] = (x,y)
 

        REMOVE_GRAPHICS = True 
        if REMOVE_GRAPHICS:
            for n,data in G.nodes(data=True):
                if "LabelGraphics" in data:
                    # Note we need to remove entry from graph itself
                    del G.node[n]["LabelGraphics"]

                if "graphics" in data:
                    # Note we need to remove entry from graph itself
                    del G.node[n]["graphics"]

        if REMOVE_GRAPHICS:
            for src ,dst, key, data in G.edges(data=True, keys=True):
                # Need key as may be multiple edges between same node pair
                # also remove for edge formatting
                if "graphics" in data:
                    # Note we need to remove entry from graph itself
                    del G[src][dst][key]["graphics"]
                if "LabelGraphics" in data:
                    # Note we need to remove entry from graph itself
                    del G[src][dst][key]["LabelGraphics"]
                if "edgeAnchor" in data:
                    # Note we need to remove entry from graph itself
                    del G[src][dst][key]["edgeAnchor"]
        

        # Correct Unicode handling problem when writing GraphML
        # refer https://networkx.lanl.gov/trac/ticket/474
        #pp.pprint(G.edges(data=True))
        #pp.pprint(G.nodes(data=True))
   
        if options.html:
            summary_data[network_name] = {} 

            for key, val in G.graph.items():
                # And also store in html data
                summary_data[network_name][key] = val

        ## Graphs
            # Create graphs
        #*********************************
        #Graphs - create different graphs for writing
        #*********************************
        # Graph with max one edge between any node pair
        G_single_edge = nx.Graph(G)

        # List of node pairs that have more than one edge between them
        #multi_edge_list = multi_edge_pairs(G)

        # categories which are internal nodes
        internal_categories = ["internal", "switch"]

        # List of internal nodes (defined by ellipse shape)
        internal_nodes = [ n for n in G.nodes()
                            if G.node[n]['category'] in internal_categories]
        
        # List of external nodes (defined by triangle shape)
        external_nodes = [ n for n in G.nodes()
                            if G.node[n]['category'] not in internal_categories]
       

        #print "external nodes {0}".format(external_nodes)
        #print "internal nodes {0}".format(internal_nodes)
        # Create internal graph by removing external nodes
        G_internal = G.copy();
        G_internal.remove_nodes_from(external_nodes);
    
        # Single edge version of internal nodes graph
        G_internal_single_edge = nx.Graph(G_internal);


        # ************
        # workaround for https://networkx.lanl.gov/trac/ticket/477
        #TODO: relabel nodes for writer
        # note that this will kill duplicate nodes
        labels_key = [n for n in G.nodes() ]
        labels_val = [ data['label'].strip("\"")
                      for n, data in G.nodes(data=True) ]
        mapping = dict(zip(labels_key, labels_val))
        G_write =nx.relabel_nodes(G,mapping)
        # and remove label
        for n,data in G_write.nodes(data=True):
            if "label" in data:
                # Note we need to remove entry from graph itself
                del G_write.node[n]["label"] 
        
        # ************

        #TODO: just append extension for files onto this, replace current format for out files
        out_file = "{0}/{1}".format(output_path, network_name)
        # Also append any custom options to filename
        if options.skip_type:
            #TODO Make sure only alphanumeric (safe file name)characters present in filename
            out_file += "_skip_" + options.skip_type.lower()

        #*********************************
        #OUTPUT - Write the graphs to files
        #*********************************
        if options.gml:
            #Add quotes
            gml_file =  out_file + ".gml"
            nx.write_gml(G, gml_file)
        #    write_graph(G, "gml", gml_out_file) 
   
        if options.graphml:
            graphml_file =  out_file + ".graphml"
            nx.write_graphml(G_write, graphml_file)
        
        if options.dot:
            dot_file =  out_file + ".dot"
            nx.write_dot(G_write, dot_file) 

        #TODO: remove repetition in output filenames

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
                                    

            for n in G_plot.nodes():
                G_plot.node[n]['a'] = 1
                G_plot.node[n]['b'] = 2
                G_plot.node[n]['category'] = 'internal' 
                G_plot.node[n]['id'] = 2
                
                #{'category': 'internal', u'id': 3} 
                #= {"a": 1, "b": 2}
                


            for s, t, index, data in G_plot.edges(data=True, keys=True):
                for k in [k for k in data]:
                    del G_plot[s][t][index][k]

            #pp.pprint(G_plot.nodes(data=True))
            #pp.pprint(G_plot.edges(data=True))

            #G_plot = nx.Graph()
            #G_plot.add_edge(1,2, data={'a': 1, 'b': 2})

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


            #Option to use original co-ordinates from GML file
            #pos = orig_pos


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
            mat_file = open("{0}/{1}.txt".format(output_path, network_name), "w")
            sparse_matrix = nx.to_numpy_matrix(G_internal_single_edge)

            # Write out manually (numpy.tofile() writes as all on one line)
            for line in sparse_matrix.tolist():
                # Convert list to a string, format numbers as integers not floats
                line = [ str(int(x)) for x in line]
                mat_file.write( " ".join(line) )
                mat_file.write("\n")
            mat_file.close()

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

if __name__ == "__main__":
    main()



