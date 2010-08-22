#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creates the dependency network of the deb files of Linux distributions based on
Debian distribution like:
    - Debian itself
    - Ubuntu variants (Ubuntu, Kubuntu, Xubuntu...)

The generated network can be transform into IGraph or NetworkX Graph object.
"""

from __future__ import with_statement
#from __future__ import division
#from __future__ import print_function
from apt import Cache
import apt_pkg

note_about_dependencies = """
Packages can depend from not existing packages.

Three type of examples:

1.
twiki depends on apache | apache2 | apache2.2
| means one of the three is enough to satisfy the dependency
There is no apache package, but there is apache2,
so we can install twiki.

2.
python-psycopg2da depends on zope3
There is no zope3, so python-psycopg2da can not installed.

3.
xpaint depends on editor
editor is not a real package, but several packages can provide editor
such as vim, nano, emacs,
so xpaint can be installed.
This type of package is called virtual package.
"""

def sources_list():
    """Returns the sources from the /etc/apt/sources.list file.
    
    Just returns with the lines beginning with .deb '.

    """
    with open("/etc/apt/sources.list") as f:
        lines = f.readlines()
        lines = [line for line in lines if line.startswith("deb ")]

    return " " + " ".join(lines)

def get_deps(pkg):
    """Get the dependencies for a given apt.Package object.
    Works with the oldest and newest versions of apt_pkg.
    It does not work with version <=0.6.46.
    """
    deps = None
    try:
        "This works with python-apt versions >= 0.7.23"
        cand = pkg.candidate
    except AttributeError:
        "This works with python-apt versions <= 0.7.14"
        deps = pkg.candidateDependencies
    else:
        if cand:
            deps = cand.dependencies
    return deps

class CommonDebNetwork:
    """Common class to create igraph.Graph or networkx.Graph.
    Before conversion you should use self.purge_edges().
    """
    def __init__(self):
        self.create()
        self.has_purged_edges = False
    def __len__(self):
        return len(self.vertices)

    # Creating from cache and dot file.
    def create(self):
        """Creates the lists of package names and edges of the
        package dependency network from the apt cache.
        """

        print """Getting package names and dependencies."""
        cache=Cache()
        pkg_list = [pkg for pkg in cache]
        pkg_names = [pkg.name for pkg in cache]

        edges = set()
        for pkg in pkg_list:
            depnames = set()
            deps = get_deps(pkg)
            if not deps:
                continue
            for dep in deps:
                or_deps = dep.or_dependencies
                if len(or_deps) > 1:
                    name == ""
                    for or_dep in or_deps:
                        dep_name = or_dep.name
                        if dep_name in pkg_names:
                            name = dep_name
                            break
                else:
                    name = or_deps[0].name
                depnames.add(name)
            name = pkg.name
            for depname in depnames:
                edges.add((name, depname))
        self.vertices = pkg_names
        self.edges = edges
        self.sources_list = sources_list()
        return pkg_names, edges

    def from_dot(self, file):
        import pygraphviz
        a=pygraphviz.AGraph(file)
        self.vertices = a.nodes()
        self.edges = a.edges()

    def summary(self):
        # print "{0:5} vertices, {1:6} edges".format(len(self.vertices), len(self.edges))
        # Does work with 2.5 used in Debian Lenny.
        print "%5s vertices, %6s edges" % (len(self.vertices), len(self.edges))

    def targets(self):
        targets = [t for s,t in self.edges]
        return set(targets)
    def extra_targets(self):
        """Targets not in vertices."""
        targets=self.targets()
        et = [t for t in targets if not t in self.vertices]
        return set(et)
    def sources(self):
        sources = [s for s,t in self.edges]
        return set(sources)
    def purge_edges(self):
        """Remove edges, which target is not in self.vertices."""
        print """Removing edges, which target is not in self.vertices."""
        extra_targets = self.extra_targets()
        new_edges = [edge for edge in self.edges if not edge[1] in extra_targets]
        self.edges = new_edges
        self.has_purged_edges = True

    def to_networkx(self):
        import networkx
        if not self.has_purged_edges:
            self.purge_edges()
        print "Transforming to networkx."
        g=networkx.DiGraph()
        g.add_nodes_from(self.vertices)
        g.add_edges_from(self.edges)
        return g

def commondebnetwork(type="igraph"):
    """debnetwork() -> Graph object
Return the package dependency network of the
debian packages.
"""
    cn =  CommonDebNetwork()
    if type == "igraph":
        return cn.to_igraph()
    elif type == "networkx":
        return cn.to_networkx()

if __name__ == "__main__":
    print "apt_pkg version: {0}, date: {1}".format(apt_pkg.Version, apt_pkg.Date)
    network = CommonDebNetwork()
    network.summary()
