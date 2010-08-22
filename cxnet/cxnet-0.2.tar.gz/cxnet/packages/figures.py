#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This file is for creating figures for articles.
I made eps files with it for an article written in LaTeX, but perhaps for
somebody else it is a good exapmle.

Arpad Horvath, 2008
"""

import packages
import os
import networkx

G=packages.get_graph()

def package_pairs_large_p():
    x = linspace(0.2,1,33)
    numbers =[]
    for x_ in x:
	num=0
	for i,j,k in N:
	    if k>=x_:
		num += 1
	numbers.append((x_,num))
    
    y=[y for x_, y in numbers]
    
    plot(x,y,"rv")
    xlabel("x")
    ylabel("Number of package pairs with p >= x")
    title("Connection between the package number and the p")
    savefig("number_p_predecessor.png")

def save_neighbor_graph(graph, packages):
    if type(packages) == type(""):
	packages = [packages]
    all = []
    for package in packages:
	all.extend(graph.predecessors(package))
	all.extend(graph.successors(package))
	all.append(package)
    subgraph = graph.subgraph(all)
    networkx.write_dot(subgraph, "%s-neighbors.dot" % "-".join(packages))
    return subgraph

def graph_to_dot_eps(graph, basename="graph", prog="neato"):
    networkx.write_dot(graph, "%s.dot" % basename)
    os.system("%s -Tfig -o %s.fig %s.dot" % (prog, basename, basename))
    os.system("fig2dev -L eps %s.fig %s.eps" % (basename, basename))
    print "You can use xfig to change fig an save as eps.\n(transfig package needed)"


##################################
# Figures in articles

def vim_neighbors(graph):
    save_neighbor_graph(graph, "vim")
    os.system("dot -Tfig -o vim-neighbors.fig vim-neighbors.dot")
    os.system("fig2dev -L eps vim-neighbors.fig vim-neighbors.eps")
    print "You can use xfig to change fig an save as eps.\n(transfig package needed)"

def pkg_properties():
    import apt
    c=apt.Cache()
    types = set([c[pkg].priority for pkg in c.keys()])
    return types

def cc_diagrams(graph):
    for namepart, priorities in [("required", "szükséges"),
		("required+important", ["szükséges", "fontos"]),
		("all", None)]:
	names = packages.pkg_names(priorities)
	Gsub=G.subgraph(names)
	cl=Gsub.clustering()
	filename = "../doc/cn_edu/cc_degree_diagram_%s.eps" % namepart
	packages.cc_degree_diagram(cl, filename)
	#print "Files %s.* written." % basename

def gnustep_graph():
    Gsub = G.subgraph("""libgnustep-base1.14 gnustep-back0.12 gnustep-gui-runtime gnustep-base-runtime libgnustep-gui0.12 gnustep-gpbs""".split())
    print Gsub.info()
    graph_to_dot_eps(Gsub, basename="gnustep_circo", prog="circo")

#print pkg_properties()
#cc_diagrams(G)
#vim_neighbor(G)

gnustep_graph()


