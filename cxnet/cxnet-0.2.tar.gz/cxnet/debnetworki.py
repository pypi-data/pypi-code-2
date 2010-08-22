from __future__ import with_statement
from __future__ import division

import igraph
try:
    from debnetworkc import CommonDebNetwork
except ImportError:
    print """I could not import debnetworkc. Perhaps there is no apt module.
You can not create deb dependency network."""

from degdist import DegreeDistribution
from time import strftime, gmtime
try:
    from platform import linux_distribution
except ImportError:
    linux_distribution = None

class CXNet(igraph.Graph):
    """Complex Network, Igraph version

    Derived from the igraph.Graph class.
    Methods defined here start with "cx" to find them easier.

    It includes the plot function.

    """

    def plot(self, target=None, **kwargs):
        """It is almost same az igraph.plot().
        
        But it has not a graph argument, and margin is set to 50 default.

        """
        if not kwargs.get("layout"):
            kwargs["layout"] = self.layout_kamada_kawai()
        if kwargs.get("margin") is None:
            kwargs["margin"] = 50

        if not kwargs.get("named"):
            self.vs["label"] = self.vs["name"]
        igraph.plot(self, target, **kwargs)

    def cxlargest_degrees(self, direction=None, limit=None):
        """Returns with the vertices with the largest degrees.

        Arguments
        ---------
        direction: default None
            Can be 'in', 'out', or None, it will be use indegree, outdegree
            or (plain) degree respectively.

        limit: integer or None, default None
           Only the packages with the degree < limit will listed.
           If None, a limit will be set (good for debian package dependency network):
           - plain: 500
           - in: 300
           - out: 50

        Returns
        -------
        hd: a list of pairs of (degree, package name)

        Example
        -------

        cn.cxlargest_degree(direction='in', limit=500)

        """

        if direction is None:
            if limit is None:
                limit = 500
            vs = self.vs(_degree_ge=limit)
            degree = self.degree
            direction = "" # for the file name
        elif direction == 'in':
            if limit is None:
                limit = 300
            vs = self.vs(_indegree_ge=limit)
            degree = self.indegree
        elif direction == 'out':
            if limit is None:
                limit = 50
            vs = self.vs(_outdegree_ge=limit)
            degree = self.outdegree
        else:
            raise ValueError, 'Argument direction must be "in", "out" or None.'
        list = [ (degree(v), v["name"]) for v in vs]
        list.sort(reverse=True)

        lines = ["%6d %-20s\n" % pair for pair in list]
        for line in lines:
            print line[:-1]  # \n not printed
        with open("largest_%sdegree.txt" % direction, "w") as f:
            f.writelines(lines)
        return list

    def cxneighbors(self, pkg_name):
        """Returns with the successors and predecessors ("out and inneighbors")
        if it is a directed networks. Neighbors otherwise.

        Parameters
        ----------
        pkg_name: string
            The name of the package. (You can find it with cxfind method.)

        Returns
        -------
            In a directed network
            returns a tuple of (predecessors, successors) where
            - predecessors are list of neighbors on incoming edges,
            - successors are list of neighbors on outcoming edges.
            In an undirected network
            returns a tuple of (neighbors, None) where
            - neighbors are list of neighbors,

        """

        if pkg_name not in self.vs["name"]:
            find = self.cxfind(pkg_name)
            if len(find) == 1:
                print """There is no package name %s.\nI will use %s instead.""" %\
                      (pkg_name, find[0])
                pkg_name = find[0] 
            else:
                print """There is no package name %s,\nbut the package names below include it.\n """ % pkg_name,\
                        "\n ".join(find)
                return (None,None)
        ix = self.vs["name"].index(pkg_name)
        if self.is_directed():
            pred = self.vs[self.predecessors(ix)]["name"]
            succ = self.vs[self.successors(ix)]["name"]
        else:
            pred = self.vs[self.neighbors(ix)]["name"]
            succ = None

        return (pred, succ)

    def cxneighborhood(self, pkg_name, plot=False, **kwargs):
        """Returns with the successors and predecessors and the package itself.

        Parameters
        ----------
        pkg_name: string
            The name of the package.
        plot: boolean or string, default False
            If it is "pdf", the output will be a file like pkg_name.pdf.
            If other string, the output will be a file named in the string. 
            If True, plot to the screen.
            If False, do not plot.

        Returns
        -------
            In a directed network
            returns a tuple of (predecessors, successors) where
            - predecessors are list of neighbors on incoming edges,
            - successors are list of neighbors on outcoming edges.
            In an undirected network
            returns a tuple of (neighbors, None) where
            - neighbors are list of neighbors,

        """
        if pkg_name not in self.vs["name"]:
            find = self.cxfind(pkg_name)
            if len(find) == 1:
                print """There is no package name %s.\nI will use %s instead.""" %\
                      (pkg_name, find[0])
                pkg_name = find[0] 
            else:
                print """There is no package name %s,\nbut the package names below include it.\n """ % pkg_name,\
                        "\n ".join(find)
                return []
        ix = self.vs["name"].index(pkg_name)
        p = self.predecessors(ix)
        s = self.successors(ix)
        neighborhood = [ix]
        neighborhood.extend(p)
        neighborhood.extend(s)
        vs = self.vs(neighborhood)
        #TODO Should return with a subgraph, not with VertexSeq?

        if plot:
            coords = [(0,0)]
            colors = ["red"]
            if p:
                delta = 1/(len(p)-.99)
                y=-0.5
                for i in range(len(p)):
                    coords.append((-.8,y))
                    colors.append("skyblue")
                    y+=delta
            if s:
                delta = 1/(len(s)-.99)
                y=-0.5
                for i in range(len(s)):
                    coords.append((.8,y))
                    colors.append("yellow")
                    y+=delta
            vs["coord"] = coords
            vs["color"] = colors
            subnetwork = vs.subgraph()
            if plot == "pdf":
                print "%s.%s" % (pkg_name,plot)
                subnetwork.plot("%s.%s" % (pkg_name,plot), layout=subnetwork.vs["coord"], **kwargs)
            elif isinstance(plot, str):
                subnetwork.plot(plot, layout=subnetwork.vs["coord"], **kwargs)
            else:
                subnetwork.plot(layout=subnetwork.vs["coord"], **kwargs)

        return vs

    def cxdegdist(self, **kwargs):
        """Returns with a DegreDistribution class analyzing and plotting distribution.

        Parameter
        ---------
        kwargs:
            parameters to the DegreeDistribution class
            Eg. direction {"in", "out", None}
        
        Returns
        -------
        dd: DegreeDistribution class object (see help(dd) )
        """
        return DegreeDistribution(self,**kwargs)

    def cxfind(self, namepart):
        """Returns the ordered list of package names containing the given part.

        Parameter
        ---------
        namepart: string
            A part of the package name.

        Returns
        -------
        names: ordered list of strings
            The ordered list of package names containing namepart.
        """
        names = [name for name in self.vs["name"] if namepart in name]
        names.sort()
        return names

    def cxwrite(self, archiver=None):
        """Returns 
        """
        date = strftime("%Y-%m-%d", gmtime())
        _time = strftime("%H:%M:%S", gmtime())
        if linux_distribution is None:
            d1,d2,d3 = ["unknown"] * 3
            print """I can not get the distribution name from the platform modul.
            Platform modul is too old."""
        else:
            d1,d2,d3 = linux_distribution()
        name0 = "-".join([d1.lower(),d2,"packages",date])
        self.write("%s.gml" % name0)
        with open("%s.txt" % name0, "w") as f:
            if "sources_list" in dir(self):
                print >>f, "Distribution:\n %s\n" % " ".join([d1,d2,d3])
                print >>f, "Repositories (the lines beginning with deb from /etc/apt/sources.list):"
                print >>f, self.sources_list
            print >>f, "Date of archiving:\n %s %s GMT\n" % (date, _time)
            if archiver:
                print >>f, "Archiver:\n %s\n" % archiver
        print "See file(s) %s.*" % name0
        return name0

def debnetwork():
    cdn = CommonDebNetwork()
    if not cdn.has_purged_edges:
        cdn.purge_edges()
    print "Transforming to numbered graph."
    idgen = igraph.UniqueIdGenerator()
    edgelist = [(idgen[x], idgen[y]) for x, y in cdn.edges]
    print "Transforming to igraph."
    debnet = CXNet(edgelist, directed=True)
    debnet.sources_list = cdn.sources_list
    debnet.vs["name"] = idgen.values()
    debnet.type = "igraph"
    return debnet


