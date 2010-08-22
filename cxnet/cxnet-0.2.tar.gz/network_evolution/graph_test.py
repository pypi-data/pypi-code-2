#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import glob
sys.path.pop(0)
print sys.path
import shelve
import networkx

def graph_test(run=None, node=None, directory="proba"):
    if run is None:
        dotfiles = glob.glob(os.path.join(directory, "*.dot"))
        dotfiles.sort()
        dotfile = dotfiles[-1]
        run = int(dotfile[-7:-4])
    else:
        dotfile = os.path.join(directory, "%03d.dot" % run)

    G= networkx.read_dot(dotfile)
    if node is None:
        node_list = G.nodes()
    else:
        node_list = [node]

    for node in node_list:
        neigh = G.neighbors(node)
        Gn = G.subgraph(neigh)
        print "%5s %4d %4d" % (node, len(Gn.nodes()), len(Gn.edges())),

        if node[0]=='"':
            node = node[1:-1]
        s=shelve.open(os.path.join(directory, "run.db"))
        print s[str(run)]["clustering_coefficient_dict"][int(node)]


if __name__ == '__main__':
    graph_test()
