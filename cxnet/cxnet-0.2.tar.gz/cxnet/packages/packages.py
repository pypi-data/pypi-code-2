#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
#from __future__ import print_function

""" Get and analyze the package dependency network of deb packages.

It investigate the degree distribution and the clustering coefficient
distribution as the function of the degree.

"""

# These three modules should be loaded in the inner part of the program:

try:
    import gettext
    transl = gettext.translation("packages", "locale")
    # transl = gettext.translation("packages", "/usr/share/locale") #Ha rootként tudom elhelyezni.
    _ = transl.ugettext
except ImportError:
    _ = lambda str: str
except IOError:
    _ = lambda str: str

import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)
warnings.simplefilter("ignore", DeprecationWarning)
try:
    import apt
    import apt_pkg
    have_apt = True
except ImportError:
    have_apt = False
    print _("""apt module can not been loaded.
You can not load dependency network from cache.
You should install this module or use dot files.
""")

try:
    import pygraphviz
except ImportError:
    print _("""pygraphviz module can not been loaded.
You can not load dependency network from dot file.
""")

import networkx
import os
import shelve
#TODO It is not in usage.
if have_apt:
    class Cache(apt.Cache):
        """Helper to getget providers for virtual packages.

        Thanks for GDebi (Cache.py) for the camelCase functions!

        """

        def isVirtualPkg(self, pkgname):
            """ this function returns true if pkgname is a virtual
                pkg """
            try:
                virtual_pkg = self._cache[pkgname]
            except KeyError:
                return False

            if len(virtual_pkg.VersionList) == 0:
                return True
            return False

        def getProvidersForVirtual(self, virtual_pkg):
            providers = []
            try:
                vp = self._cache[virtual_pkg]
                if len(vp.VersionList) != 0:
                    return providers
            except IndexError:
                return providers
            for pkg in self:
                v = self._depcache.GetCandidateVer(pkg._pkg)
                if v == None:
                    continue
                for p in v.ProvidesList:
                    if virtual_pkg == p[0]:
                        providers.append(pkg)
            return providers

        def get_providers(self, package_names):
            """Get providers for a package or packages.

            package_name: a package name (string) or a list of package names

            :Returns:
            A dictionary with the keys of virtual packages, and as values the
            provider packages.
            """
            providers = {}
            if type(package_names) == type(""):
                package_names = [package_names]
            for pkg in package_names:
                prov =  self.getProvidersForVirtual(pkg)
                if prov:
                    prov =  [package.name for package in prov]
                    prov.sort()
                    providers[pkg] =  prov
            return providers

    def all_providers(graph=None):
        """Get all the provider packages."""

        c=Cache()
        package_names = pkg_names(with_summary=False)
        package_name_set=set(package_names)
        if graph is None:
            graph = package_network_from_cache(package_names=package_names)
        all_names = set(graph.nodes())
        print _("I will search for provider files for virtual packages.")
        virtual_packages = list(all_names - package_name_set)
        pr = c.get_providers(virtual_packages)
        print _("I have found provider packages.")
        return pr

class PackageNetwork(networkx.DiGraph):
    def __init__():
        pass

class MyDiGraph(networkx.DiGraph):
    direction = None
    percent = None

    def _double_edges_old(self, file="double_edges.txt", imin=0, imax=None):
        """Return and save double edges.

         It is a variant of double_edges() but I don't know why it is so slow.

        """

        print _("I will found the double edges between nodes.")
        print hms()
        node_num = len(self.nodes())
        edges = self.edges()
        print _("There is %d nodes.") % node_num
        double_list = []
        if os.path.isfile(os.path.abspath(file)):
            head, ext = os.path.splitext(file)
            os.rename(file, "".join([head, "_old", ext]))
        f = open(file, "w")
        print _("I opened the file '%s'") % file
        print hms()
        if imax is None:
            imax = node_num
        for i in xrange(imin, imax):
            if True: #i%10 == 0:
                print "%s: %d" % (hms(),i)
            for j in xrange(i+1, node_num):
                if (j,i) in edges and (i,j) in edges:
                    namei = self.node_names[i]
                    namej = self.node_names[j]
                    names = (namei, namej)
                    print _("\n%s <-> %s double edges") % names
                    print >>f, "%s <-> %s"  % names
                    double_list.append(names)
        f.close()
        print hms()
        return double_list

    def to_numbered(self):
        """It returns with the numbered version of the graph.

        In numbered version the nodes are numbers.

        """

        print _("I made the numbered graph, which has numbers as node names.")
        G = networkx.empty_graph(len(self.nodes()), create_using=MyDiGraph())
        print _(" - I created the empty graph.")
        G.name = self.name
        for n1, n2 in self.edges():
            G.add_edge((nodes.index(n1), nodes.index(n2)))
        G.node_names = [str(node) for node in nodes]
        return G

    def double_edges(self, file="double_edges.txt", imin=0, imax=None):
        """Return and save double edges.

        file:
          the file where to save the double edges

        imin and imax:
          If these are given, it makes only
          from the imin-th node to (imax-1)-th node.

        """

        print hms(), _("I will found the double edges between nodes.")
        nodes = self.nodes()
        node_num = len(nodes)
        edges = self.edges()
        print _("There is %d nodes.") % node_num
        double_list = []
        if os.path.isfile(os.path.abspath(file)):
            head, ext = os.path.splitext(file)
            os.rename(file, "".join([head, "_old", ext]))
        f = open(file, "w")
        print hms(), _(" I opened the file '%s'") % file

        if imax is None or imax > node_num:
            print _("For imax should be: imax <= number of nodes. I use imax = imax = number of nodes.")
            imax = node_num
        if not 0 <= imin < imax:
            print _("For imin should be: 0 <= imin < imax. I use imin = 0.")
            imin = 0

        for i in nodes[imin: imax]:
            if i%10 == 0:
                print "%s Node %d" % (hms(),i)
            for j in nodes:
                if j<i: continue
                if self.has_edge((j,i)) and self.has_edge((i,j)):
                    namei = self.node_names[i]
                    namej = self.node_names[j]
                    names = (namei, namej)
                    print "%s <-> %s" % names
                    print >>f, "%s <-> %s"  % names
                    double_list.append(names)
        f.close()
        print hms(), _("I saved the file '%s'. At next run I will rewrite it.") % file
        return double_list

    def near_edges(self, percent_limit=20, imin=0, imax=None):
        """Returns and saves the edge list where nodes are connected or near.

        For all the possible edges it will be in it:
        - if there is edge between them or
        - if they are *near to each other*, it means ``isec/uni >= percent/100``,
               where
           - isec is the number of common predeceesors for the nodes
           - uni is the union of predecessors.
        """

        # print hms(),\
        #    _("I will found the pairs of packages are near each other. Percent=%d" % percent_limit)
        print hms(),\
           _("I will get the intersection/union for the packages")
        percent_limit_ = percent_limit/100
        nodes = self.nodes()
        node_num = len(nodes)
        edges = self.edges()
        print _("There is %d nodes.") % node_num
        print hms(), _("I will store the sets of predecessors.")

        pred = {}
        for i in nodes:
            if i%1000 == 0:
                print "%s Node %d" % (hms(),i)
            predec = set(self.predecessors(i))
            pred[i] = (predec, len(predec))

        edge_list = []
        #if os.path.isfile(os.path.abspath(file)):
        #    head, ext = os.path.splitext(file)
        #    os.rename(file, "".join([head, "_old", ext]))
        #f = open(file, "w")
        #print hms(), _(" I opened the file '%s'") % file

        if imax is None or imax > node_num:
            print _("For imax should be: imax <= number of nodes. I use imax = imax = number of nodes.")
            imax = node_num
        if not 0 <= imin < imax:
            print _("For imin should be: 0 <= imin < imax. I use imin = 0.")
            imin = 0

        print _("I begin the main cycle.")
        for i in nodes[imin: imax]:
            if i%10 == 0:
                print "%s Node %d" % (hms(),i)
            ipred, iprednum = pred[i]
            for j in nodes:
                if j<=i: continue
                jpred, jprednum = pred[j]
                isect = len(ipred.intersection(jpred))
                union = iprednum + jprednum - isect
                if union == 0:
                    continue
                percent=isect/union
                if percent >= percent_limit_:

                    #namei = self.node_names[i]
                    #namej = self.node_names[j]
                    #names = (namei, namej)
                    #print "%s <-> %s" % names
                    #print >>f, "%s <-> %s"  % names
                    edge_list.append((i, j, percent))

        #f.close()
        #print hms(), _("I saved the file '%s'. Do not forget to save it to another file.") % file

        shelf = shelve.open("packages.db")
        if imin == 0 and imax == node_num:
            shelf["Near edges"] = edge_list
        else:
            shelf["Near edges %d..%d" % (imin, imax)] = edge_list
        shelf.close()

        return edge_list

    def _percented_graph_old(self, percent, dotfile=None):
        """Returns a modified version of this graph for investigate clustering properties.

        It takes too many time: on intel core 2 duo 1.73 GHz it took 263 of 25500 in 12 hours.

        For all the possible edges it will be in it:
        - if there is edge between them or
        - if ``isec/uni >= percent/100``, where
           - isec is the number of common predeceesors for the nodes
           - uni is the union of predecessors.
        """

        G2 = self.copy()
        print _("I will make the %d-percent-copy of the original.\nIt might take very long time.") % percent
        G2.percent = percent
        percent_ = percent / 100
        nodes = self.nodes()
        edges = self.edges()
        for i in nodes:
            ipred = self.predecessors(i)
            inum = len(ipred)
            if inum == 0: continue
            ipred = set(ipred)
            for j in nodes:
                if j>i: continue
                if (j,i) in edges and (i,j) in edges:
                    G2.delete_edge((j,i))
                    print _("Double edges between %s and %s. I delete one.") % (i,j)
                    continue
                if (j,i) in edges or (i,j) in edges: continue
                jpred = self.predecessors(j)
                jpred = set(jpred)
                uni =  len(jpred.union(ipred))
                isect = len(jpred.intersection(ipred))
                if isect/uni >= percent_:
                    G2.add_edge((i,j))
        if dotfile is None:
            dotfile = "%d-percent-copy.dot" % percent
        networkx.write_dot(G2, dot_file)
        return G2


    def largest_degrees(self, limit=800):
        """Returns and print the packages has the more dependent package.

        limit: only the packages with number of dependent packages < limit
           will listed

        The direction (degree, in-degree or out-degree) use the graph
        property *direction*. If you want the in-degree, you should set it
        to 'in', for out degree to 'out'. If it is None or 'in_out',
        then the plain degree is used::

          G.direction = 'in'
          G.largest_degrees(limit=50)

        """

        if self.direction == 'in':
            degree = self.in_degree
        elif self.direction == 'out':
            degree = self.out_degree
        elif self.direction in ['in_out', None]:
            degree = self.degree
        else:
            raise ValueError, 'direction must be "in" "out" or "in_out"'
        list = [ (degree(i), i) for i in self if degree(i) > limit ]
        list.sort(reverse=True)

        lines = ["%6d %-20s\n" % pair for pair in list]
        for line in lines:
            print line[:-1]  # \n not printed
        f=open("most_frequent.txt", "w")
        f.writelines(lines)
        f.close()
        return list

    def save_graph(self, file='packages.db', name=None, as_numbered=False):
        """Save the graph into a shelve or dot file.

        The file name is get from the string *file*.

        If it ends with .db it save it as a shelve file
        with the name 'graph' or if *name* is given with that name.

        If it ends with .dot it saves into dot file.

        as_numbered: (default is False)
          If True then it converts to numbered graph first.

        """

        if as_numbered:
            G = self.to_numbered()
        else:
            G = self
        if file.endswith(".db"):
            db = shelve.open(file)
            if name is None:
                name = 'graph'
            db[name] = G
            db.close()
        if file.endswith(".dot"):
            networkx.write_dot(G, file)

def pkg_names(priorities=None, with_summary = False):
    """ Returns with the package names in the cache.

    :Arguments:

    priorities: default: None
      It can be string or list of strings.
      if not None, it lists only the packages with the given priorities.
      The priorities are in national languages.
    with_summary: default: False
      if True, the list will containe tuples (name, summary).

    :Returns:

    List of names, or with list of tuples described above.

    """

    if not have_apt:
        print _("""'apt' module is not loaded in this program.
You are not able to list the names in the cache.
If you have dot file, you can import it, and list its nodes:
 G=package_network("xxx.dot")
 print G.nodes()
""")
        return []

    c = Cache()


    if priorities is None:
        names = [c[pkg].name for pkg in c.keys()]
    else:
        if type(priorities) == type(""):
            priorities = [priorities]
        names = [c[pkg].name for pkg in c.keys() if c[pkg].priority in priorities]

    print _("There is %d packages") % len(names)
    if with_summary:
        summary = [c[pkg].summary for pkg in c.keys()]
        names = zip(names, summary)
        print _("The first 5 names with summary\n%s") \
              % "\n".join(["%-20s: %-60s" % item for item in names[:10]])
    else:
        print _("The first 7 names %s") % ", ".join(names[:7])
    return names

def package_network_from_dot(dot_file = 'ubuntu_packages.dot'):
    """Get the package dependency network from dot file."""

    print _("I get the network from dot file '%s'.") % dot_file
    G = pygraphviz.AGraph(dot_file)
    G = MyDiGraph(G)
    G.name = "Ubuntu package dependency (directed) network"
    print _("Ready")
    return G

def package_network( where_from=None,
               name = None,
               is_numbered = False):

    """Get the package dependency network from cache, dot file or shelf."""

    if where_from is None:
        if have_apt:
            where_from = 'cache'
        else:
            where_from = 'dot'

    if where_from == 'cache':
        G0 = package_network_from_cache()
    elif where_from.endswith('dot'):
        if  where_from == 'dot':
            where_from = 'ubuntu_packages.dot'
        G0=package_network_from_dot(dot_file = where_from)
    elif where_from.endswith(".db"):
        db = shelve.open(where_from)
        if type(name) != type(""):
            name = 'graph'
        G0 = db[name]
    else:
        raise ValueError, \
              "where_from should be 'cache' or ends with '.dot' or '.db'"

    nodes = G0.nodes()

    if is_numbered is True:
        G = G0.to_numbered()
    else:
        G = G0
    print _(" - The graph is ready.")

    return G


def package_network_from_cache(save_as=None, package_names=None):
    """Get package dependency network from cache.

    save_as:
      if it is a string save the network into that file.

    """

    if not have_apt:
        print _("""`apt` module is not loaded.
You can use dot files to get the network
or install these modules.""")
        return None

    print _("I get the network from apt cache.")
    #From /usr/lib/python2.5/site-packages/apt/package.py
    apt_pkg.init()
    cache = apt_pkg.GetCache()
    depcache = apt_pkg.GetDepCache(cache)
    records = apt_pkg.GetPkgRecords(cache)
    sourcelist = apt_pkg.GetPkgSourceList()

    G = MyDiGraph()
    G.name = "Ubuntu package dependence (directed) network"
    if package_names is None:
        package_names = pkg_names()
    for name in package_names:
        #print "*** %s" % name
        pkgiter = cache[name]
        pkg = apt.Package(cache, depcache, records, sourcelist, None, pkgiter)
        #pkg = apt.Package(cache, pkgiter)
        #print "Name: %s " % pkg.name
        #print "ID: %s " % pkg.id
        #print "Priority (Candidate): %s " % pkg.priority
        #print "Priority (Installed): %s " % pkg.installedPriority
        #print "Installed: %s " % pkg.installedVersion
        #print "Candidate: %s " % pkg.candidateVersion
        #print "CandidateDownloadable: %s" % pkg.candidateDownloadable
        #print "CandidateOrigins: %s" % pkg.candidateOrigin
        #print "SourcePkg: %s " % pkg.sourcePackageName
        #print "Section: %s " % pkg.section
        #print "Summary: %s" % pkg.summary
        #print "Description (formated) :\n%s" % pkg.description
        #print "Description (unformated):\n%s" % pkg.rawDescription
        #print "InstalledSize: %s " % pkg.installedSize
        #print "PackageSize: %s " % pkg.packageSize
        #print "Dependencies: %s" % pkg.installedDependencies
        dependencies = []
        for dep in pkg.candidateDependencies:
            dependencies.extend([o.name for o in dep.or_dependencies])
            #print ",".join(["%s (%s) (%s) (%s)" % (o.name,o.version,o.relation, o.preDepend) for o in dep.or_dependencies])
        if not dependencies:
            #print "No candidateDependencies in '%s'" % name
            G.add_node(name)
        dependencies = set(dependencies)
        for dependency in dependencies:
            G.add_edge(name, dependency)
        #print "arch: %s" % pkg.architecture
        #print "homepage: %s" % pkg.homepage
        #print "rec: ",pkg.candidateRecord

    if type(save_as) == type(""):
        G.save_graph(file=save_as)

    return G

# TODO Why is it much slower as the previous function?
def get_igraph_from_cache(save_as=None, package_names=None):
    """Get package dependency network from cache.

    save_as:
      if it is a string save the graph into that file.

    """

    if not have_apt:
        print _("""`apt` module is not loaded.
You can use dot files to get the network
or install these modules.""")
        return None

    print _("I get the network from apt cache.")
    #From /usr/lib/python2.5/site-packages/apt/package.py
    apt_pkg.init()
    cache = apt_pkg.GetCache()
    depcache = apt_pkg.GetDepCache(cache)
    records = apt_pkg.GetPkgRecords(cache)
    sourcelist = apt_pkg.GetPkgSourceList()

    import igraph
    G = igraph.Graph()
    #G.name = "Ubuntu package dependence (directed) graph"
    if package_names is None:
        package_names = pkg_names()
    N = len(package_names)
    #print N
    package_index = zip(package_names, range(N))
    print package_index[:20]
    package_index = dict(package_index)
    G.add_vertices(N-1)
    G.vs["label"] = package_names
    #return G
    for name in package_names:
        source_index = package_index[name]
        print source_index
        #print "*** %s" % name
        pkgiter = cache[name]
        pkg = apt.Package(cache, depcache, records, sourcelist, None, pkgiter)
        #print "Name: %s " % pkg.name
        #print "ID: %s " % pkg.id
        #print "Priority (Candidate): %s " % pkg.priority
        #print "Priority (Installed): %s " % pkg.installedPriority
        #print "Installed: %s " % pkg.installedVersion
        #print "Candidate: %s " % pkg.candidateVersion
        #print "CandidateDownloadable: %s" % pkg.candidateDownloadable
        #print "CandidateOrigins: %s" % pkg.candidateOrigin
        #print "SourcePkg: %s " % pkg.sourcePackageName
        #print "Section: %s " % pkg.section
        #print "Summary: %s" % pkg.summary
        #print "Description (formated) :\n%s" % pkg.description
        #print "Description (unformated):\n%s" % pkg.rawDescription
        #print "InstalledSize: %s " % pkg.installedSize
        #print "PackageSize: %s " % pkg.packageSize
        #print "Dependencies: %s" % pkg.installedDependencies
        dependencies = []
        for dep in pkg.candidateDependencies:
            dependencies.extend([o.name for o in dep.or_dependencies])
            #print ",".join(["%s (%s) (%s) (%s)" % (o.name,o.version,o.relation, o.preDepend) for o in dep.or_dependencies])
        dependencies = set(dependencies)
        for dependencie in dependencies:
            dep_index = package_index.get(dependencie)
            if dep_index:
                #print (source_index, package_index[dependencie])
                G.add_edges((source_index, dep_index))
        #print "arch: %s" % pkg.architecture
        #print "homepage: %s" % pkg.homepage
        #print "rec: ",pkg.candidateRecord

    return G

def from_cache_to_gml(file="new_package_network.gml", package_names=None):
    """Get package dependency network from cache.

    save_as:
      if it is a string save the graph into that file.

    """

    if not have_apt:
        print _("""`apt` module is not loaded.
You can use dot files to get the network
or install these modules.""")
        return None

    f=open(file, "w")
    print _("I get the network from apt cache.")
    print >>f, "graph [\n  directed = 1"
    #From /usr/lib/python2.5/site-packages/apt/package.py
    apt_pkg.init()
    cache = apt_pkg.GetCache()
    depcache = apt_pkg.GetDepCache(cache)
    records = apt_pkg.GetPkgRecords(cache)
    sourcelist = apt_pkg.GetPkgSourceList()

    #G.name = "Ubuntu package dependence (directed) graph"
    if package_names is None:
        package_names = pkg_names()
    N = len(package_names)
    #print N
    package_index = zip(package_names, range(N))
    print package_index[:20]
    package_index = dict(package_index)
    for name in package_names:
        print >>f, """  node [
    id=%d
    label="%s"
    ]""" % (package_index[name], name)
    for name in package_names:
        source_index = package_index[name]
        pkgiter = cache[name]
        pkg = apt.Package(cache, depcache, records, sourcelist, None, pkgiter)
        #print "Name: %s " % pkg.name
        #print "ID: %s " % pkg.id
        #print "Priority (Candidate): %s " % pkg.priority
        #print "Priority (Installed): %s " % pkg.installedPriority
        #print "Installed: %s " % pkg.installedVersion
        #print "Candidate: %s " % pkg.candidateVersion
        #print "CandidateDownloadable: %s" % pkg.candidateDownloadable
        #print "CandidateOrigins: %s" % pkg.candidateOrigin
        #print "SourcePkg: %s " % pkg.sourcePackageName
        #print "Section: %s " % pkg.section
        #print "Summary: %s" % pkg.summary
        #print "Description (formated) :\n%s" % pkg.description
        #print "Description (unformated):\n%s" % pkg.rawDescription
        #print "InstalledSize: %s " % pkg.installedSize
        #print "PackageSize: %s " % pkg.packageSize
        #print "Dependencies: %s" % pkg.installedDependencies
        dependencies = []
        for dep in pkg.candidateDependencies:
            dependencies.extend([o.name for o in dep.or_dependencies])
            #print ",".join(["%s (%s) (%s) (%s)" % (o.name,o.version,o.relation, o.preDepend) for o in dep.or_dependencies])
        dependencies = set(dependencies)
        for dependencie in dependencies:
            dep_index = package_index.get(dependencie)
            if dep_index is not None:
                #print (source_index, package_index[dependencie])
                print >>f, """  edge [
    source %d
    target %d
    ]""" % (source_index, dep_index)
        #print "arch: %s" % pkg.architecture
        #print "homepage: %s" % pkg.homepage
        #print "rec: ",pkg.candidateRecord

    print >>f, "]"

