#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
#from __future__ import print_funcion

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
import pylab
from time import localtime, time, strftime
from math import sqrt
import os
import shelve

powerlaw = lambda x, exponent, amplitude: amplitude * (x ** exponent)
hms = lambda : ":".join("%2.2d" % i for i in localtime()[3:6])

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
            graph = get_graph_from_cache(package_names=package_names)
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


    def clustering_coefficient(self, package_name):
        """Returns with a tuple of (number_of_neighbours, edges, clustering_coefficient).

        See in:
        Réka Albert and Albert-László Barabasi:
        Statistical mechanics of complex networks,
        REVIEWS OF MODERN PHYSICS, VOLUME 74, JANUARY 2002
        Page 49

        But for directed graph there is two times as much edges
        in complete graph as in undirected. So there must not
        divide with two.

        """

        if self.direction == 'in':
            neighbors =self.predecessors
        elif self.direction == 'out':
            neighbors = self.successors
        elif self.direction in ['in_out', None]:
            neighbors = lambda node: self.successors(node) + self.predecessors(node)
        else:
            raise ValueError, "direction can be 'in', 'out', 'in_out' or None"

        neigh = neighbors(package_name)
        subgraph = self.subgraph(neigh)
        n = len(neigh)

        edges = subgraph.number_of_edges()

        max_edges = n*(n-1)
        if not self.is_directed():
            max_edges /= 2
        coefficient = 0 if n in [0,1] else edges / max_edges
        #if predessors == 0:
        #    coefficient = None
        #else coefficient = edges / max_edges
        return (n, edges, coefficient)

    def clustering(self):
        # TODO doc string
        clustering = []
        for node in self:
            neighbors, edges, clustering_coeff = self.clustering_coefficient(node)
            clustering.append((neighbors, clustering_coeff, node))
        clustering.sort(reverse=True)

        return clustering

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

def degree_distribution_from_degrees(degrees,
        savefig_file=None, savehist_file=None,
        direction=None,
        args={}):
    """From the list of degrees of nodes it draw the loglog graph of
    the degree distribution. If savefig_file is given, it save into
    image as well.

    """

    #TODO: get out the save part???

    #f=open("degree_distrib_data.txt", "a")

    cumulative = args.get("cumulative")
    fitting = args.get("fitting")
    my_adjusted = args.get("my_adjusted")
    fitting_parameters = args.get("fitting_parameters")
    try:
        fitting_intervals = fitting_parameters.get("intervals")
    except AttributeError:
        fitting_intervals = None
    labels =[]

    pylab.clf()
    pylab.hold(True)

    txt = "\n*** Direction: %s ***" % direction
    #print >>f, txt
    print txt

    degrees.sort()
    txt = _("20 largest degrees are %s.") % \
            ", ".join([str(deg) for deg in degrees[-20:]])
    #print >>f, txt
    print txt
    max_deg = degrees[-1]
    min_deg = degrees[0]
    hist = [degrees.count(i) for i in range(max_deg +1)]
    zerodeg = hist[0]
    if not cumulative:
        normalized = True
    if normalized:
        histsum = sum(hist)
        hist = [k/histsum for k in hist]
    if min_deg == 0:
        if direction in ['in', 'out']:
            dir_str = _(" (For %s-degree.)") % direction
        else: dir_str=""
        txt =  _("There is %d files with zero degree.%s") % (zerodeg, dir_str)
        #print >>f, txt
        print txt

    if not cumulative:
        labels.append("original distribution")
        pylab.loglog(range(min_deg, max_deg+1), hist[min_deg:], "b+",
            label="Degree distribution")

    hist_ = list(enumerate(hist))[min_deg:]
    xmin0 =   [ x for (x,y) in hist_ if y == 0 ][0]
    hist_x = [ x for (x,y) in hist_ if y > 0 ]
    hist_y = [ y for (x,y) in hist_ if y > 0 ]
    hist_y0 = hist_y[:]
    del hist_
    if savehist_file is not None:
        print _(" I will save file %s.") % savehist_file
        g = open(savehist_file, 'a')
        g.writelines( ['\n\n',
                       ("%d-%2d-%2d\n" % localtime()[:3]),
                       "degree, corrected_number, original_number\n"]+
                       ["%6d %18.8f %8d\n" % zip_ for  zip_ in zip(hist_x, hist_y, hist_y0)])
        g.close()

    if my_adjusted and not cumulative:
        labels.append("bin-smeared distribution")
        # An other histogram that is most appropriate for high x, I think

        x_lower = hist_x[xmin0-1] + 0.5
        for i in range(xmin0, len(hist_y)-1):  #????
            x_upper = sqrt(hist_x[i] * hist_x[i+1])
            hist_y[i] /= (x_upper - x_lower)
            x_lower = x_upper
        x_upper = hist_x[-1]** 2 / x_lower
        hist_y[-1] /= (x_upper - x_lower)

        pylab.loglog(hist_x, hist_y, "rx")

    if cumulative:
        labels.append("cumulative distribution")
        y_cum = []
        sum_ = 0
        hist.reverse()
        for y_ in hist:
            sum_ += y_
            y_cum.append(sum_)
        y_cum.reverse()
        hist.reverse()


        min = min_deg if min_deg > 0 else 1
        hist_x = range(min, max_deg+1)
        hist_y = y_cum[min:]

        pylab.loglog(hist_x, hist_y, "b+",
            label="Cumulative degree distribution")

    if fitting:
        if not fitting_intervals: #is None or length == 0
            li = 1 if min_deg == 0 else 0 # lowest index
            fitting_intervals = [(li, max_deg)]
        for start, stop, line, label in fitting_intervals:
            labels.append(label)
            if stop is None:
                stop = max_deg
            assert 1<= start < stop <= max_deg
            if not line:
                line = "k--"
            exponent, a, chi2 = fit_powerlaw(hist_x[start:stop+1], hist_y[start:stop+1])
            txt =  "Interval: [%d, %d], exponent: %f, chi^2: %f, chi^2/dof = %f" % (start, stop, exponent, chi2, chi2/(stop-start-1))
            #print >>f, txt
            print txt
            power_y = a*hist_x**exponent
            pylab.loglog(hist_x[start:stop+1], power_y[start:stop+1], line)
        f.close()

    if cumulative:
        ytxt = "Number of nodes with %sdegree > %s"
    else:
        ytxt = "$p(k_{%s})$"
    if direction in [None, 'in_out']:
        xtxt = "$k$"
        ytxt = ytxt % ("")
    elif direction in ['in', 'out']:
        xtxt = "$k_{%s}$" % direction
        ytxt = ytxt % (direction)
    pylab.ylabel(ytxt)
    pylab.xlabel( xtxt)
    pylab.legend(labels)
    if savefig_file is not None:
        print _(" I will save file %s.") % savefig_file
        pylab.savefig(savefig_file)

    f.close()
    pylab.hold(False)
    pylab.show()

def degree_distribution(graph, direction=None, save_as=None,
                        args={"cumulative" : True,
                              "fitted" : True,
                              "my_adjusted" : True}):
    """Makes and plot the degree distribution(s) of the file.

    graph: the graph

    direction: 'in', 'out', 'in_out', None or 'all'

    save_as: the name of the file,
      if direction is 'all' the direction will be included in the file name if
      save_as = "../dd.svg" one of the file will be ../dd_in.svg

    """

    cumulative = args["cumulative"] if "cumulative" in args.keys() \
          else None
    fitting = args["fitting"] if "fitting" in args.keys() \
          else None
    my_adjusted = args["my_adjusted"] if "my_adjusted" in args.keys() \
          else None

    if "fitting" in args.keys():
        fitting = args["fitting"]
    if "my_adjusted" in args.keys():
        my_adjusted = args["my_adjusted"]

    if direction == 'all':
        for dir in ['in', 'out', 'in_out']:
            fitting_parameters = args.get(dir)
            args["fitting_parameters"] = fitting_parameters
            head, tail = os.path.split(save_as)
            root, ext = os.path.splitext(tail)
            cum = "cumulative_" if cumulative else ""
            save_as_ = os.path.join(head, "%s%s_%s%s" % (cum, root, dir, ext))
            degree_distribution(graph, direction=dir, save_as = save_as_,
                                args=args)
        return
    elif direction == 'in':
        degree = graph.in_degree
    elif direction == 'out':
        degree = graph.out_degree
    elif direction in ['in_out', None]:
        degree = graph.degree
    else:
        raise ValueError, 'direction must be "all", "in" "out" or "in_out"'

    #print "\n".join([ "%5d %-20s" % (degree(i), i) for i in graph if degree(i) > 800 ])
    #limit=800
    #print "The degrees greater then %d are %s" % (limit,  graph.largest_degrees(limit=limit))

    degree_distribution_from_degrees(degree(), savefig_file=save_as,\
                        savehist_file = 'degree_distrib_%s.txt' % direction,
                        direction = direction,
                        args=args)

def cc_degree_diagram(clustering, savefig_name="cc_degree_diagram.png", cumulative=False):
    """Draw the clustering_coefficient - degree diagram"""
    degrees=[i for i,j,k in clustering]
    max_deg = max(degrees)
    x = []
    y = []
    for deg in xrange(2, max_deg+1):
        number = degrees.count(deg)
        if number != 0:
            clustering_coefficients=[j for i,j,k in clustering if i==deg]
            avg = sum(clustering_coefficients)/number
            if avg != 0:
                x.append(deg)
                y.append(avg)
            else:
                print _("The averaged clustering coefficient is zero for degree %d") % deg
    f = open("cc_degree_xy.dat", "w")
    for i, j in zip(x,y):
        print >>f, "%6d %18.10f" % (i,j)
    f.close()

    if cumulative:
        y_cum = []
        sum_ = 0
        #y.reverse()
        for y_ in y:
            sum_ += y_
            y_cum.append(sum_)
        y=y_cum
        #y.reverse()

    exponent, a, chi2 = fit_powerlaw(x,y)

    x=pylab.array(x)
    pylab.loglog(x,y,'b.')
    pylab.loglog(x,powerlaw(x, exponent,a),'k-', hold=True)
    pylab.ylabel("avg(clustering coefficient)")
    pylab.xlabel("degree")
    pylab.text(5, 4,
            'Fit: a = %5.2f, k = %5.2f' % (a, exponent))
    #pylab.legend(["clustering coeff", u"$a x^{k}$"])
    #pylab.title("Clustering coeff vs. degree (k=%5.2f)" % exponent)

    pylab.savefig(savefig_name)
    pylab.show()
    pylab.hold(False)

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
 G=get_graph("xxx.dot")
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

def fit_powerlaw(x, y):
    """Return with exponent and the *a* coefficient of the power.

    powerlaw_function(x) = amplitude * x ** exponent

    >> fit_powerlaw([1,2,3], [1,4,9])
    exponent 2.000000, amplitude=1.000000
    >> fit_powerlaw([1,2,3], [5,20,45])
    exponent 2.000000, amplitude=5.000000
    >> fit_powerlaw([1,2,3], [24, 12, 8])
    exponent -1.000000, amplitude=24.000000

    """
    from scipy import optimize

    for i in x:
        if i == 0:
            raise ValueError, "There is zero value in x"
    for i in y:
        if i == 0:
            raise ValueError, "There is zero value in y"

    logx = pylab.log10(x)
    logy = pylab.log10(y)

    fitfunc = lambda p, x: p[0] + p[1] * x
    errfunc = lambda p, x, y: y-fitfunc(p, x)
    pinit = [0, -1]
    out = optimize.leastsq(errfunc, pinit, args=(logx, logy),
                  full_output=False)

    p_final = out[0]
    exponent = p_final[1]
    amplitude = 10**p_final[0]
    print "exponent %f, amplitude=%f" % (exponent, amplitude)
    chi2 = sum([errfunc(p_final,logx_,logy_)** 2 for logx_, logy_ in zip(logx,logy)])
    return exponent, amplitude, chi2

def get_graph_from_dot(dot_file = 'ubuntu_packages.dot'):
    """Get the package dependency network from dot file."""

    print _("I get the graph from dot file '%s'.") % dot_file
    G = pygraphviz.AGraph(dot_file)
    G = MyDiGraph(G)
    G.name = "Ubuntu package dependency (directed) network"
    print _("Ready")
    return G

def get_graph( where_from=None,
               name = None,
               is_numbered = False):

    """Get the package dependency network from cache, dot file or shelf."""

    if where_from is None:
        if have_apt:
            where_from = 'cache'
        else:
            where_from = 'dot'

    if where_from == 'cache':
        G0 = get_graph_from_cache()
    elif where_from.endswith('dot'):
        if  where_from == 'dot':
            where_from = 'ubuntu_packages.dot'
        G0=get_graph_from_dot(dot_file = where_from)
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


def get_graph_from_cache(save_as=None, package_names=None):
    """Get package dependency network from cache.

    save_as:
      if it is a string save the network into that file.

    """

    if not have_apt:
        print _("""`apt` module is not loaded.
You can use dot files to get the graph
or install these modules.""")
        return None

    print _("I get the graph from apt cache.")
    #From /usr/lib/python2.5/site-packages/apt/package.py
    apt_pkg.init()
    cache = apt_pkg.GetCache()
    depcache = apt_pkg.GetDepCache(cache)
    records = apt_pkg.GetPkgRecords(cache)
    sourcelist = apt_pkg.GetPkgSourceList()

    G = MyDiGraph()
    G.name = "Ubuntu package dependence (directed) graph"
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
You can use dot files to get the graph
or install these modules.""")
        return None

    print _("I get the graph from apt cache.")
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
You can use dot files to get the graph
or install these modules.""")
        return None

    f=open(file, "w")
    print _("I get the graph from apt cache.")
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

def clustering_to_dat(clustering, dat_file="clustering.dat"):
    f = open(dat_file, "w")
    print >>f, "neigbours, cl. coeff, name"
    print >>f, '\n'.join(["%5d %18.12f %-10s" % i for i in clustering])
    f.close()
    print _("I have wrote the file '%s'.") % dat_file

def clustering_from_dat(dat_file="clustering.dat"):
    cl = []
    f = open(dat_file)
    lines = f.readlines()
    f.close()

    for line in lines[1:]:
        i,j,k = line.split()
        cl.append([int(i), float(j), k])
    print _("clustering cl has %d elements") % len(cl)
    print _("The first one is"), cl[0]
    return cl

def main():
    clustering_from_file = False
    clustering_from_file = True
    direction = 'in'
    if clustering_from_file is False:
        print _("Get package graph...")
        G=get_graph_from_dot()
        print _("Clustering...")
        G.direction = direction
        cl=G.clustering()
        print G.direction
        clustering_to_dat(cl, direction+"_clustering.dat")
    else:
        cl = clustering_from_dat(direction+"_clustering.dat")
        shelf = shelve.open("packages.db")
        shelf["clustering"] = cl
        shelf.close()

    print _("Draw diagram")
    cc_degree_diagram(cl, cumulative=False)

    #x = [ i for i,j,k in cl]
    #y = [ j for i,j,k in cl]
    #pylab.loglog(x,y,'.')
    #pylab.show()

def connected_components(G):
    Gu=G.to_undirected()
    Gcc = networkx.connected_component_subgraphs(Gu)
    return Gcc

def get_double_edges(imin=0, imax=None):
    """Get double edges of the graph, write and save it.

    imin and imax: If these are given, it makes only from the imin-th
        node to (imax-1)-th node.
    """

    G = get_graph(where_from = "packages.db", name='graph')
    G.info()
    return G.double_edges(imin=imin, imax=imax)

def get_near_edges(imin=0, imax=None):
    """Get near edges of the graph, write and save it.

    imin and imax: If these are given, it makes only from the imin-th
        node to (imax-1)-th node.
    """

    G = get_graph(where_from = "packages.db", name='graph')
    G.info()
    return G.near_edges(imin=imin, imax=imax)

def changes(dot1, dot2, to_shelf=True):
    """Get changes from two dot-files.

    dot1 and dot2: the two dot-files
    to_shelf: boolean, if True, it stores into the package.db.

    return with a dictionary with the keys "new nodes", "deleted nodes" and
    "new edges".

    """

    G1=get_graph_from_dot(dot1)
    G2=get_graph_from_dot(dot2)
    new_nodes=[str(i) for i in set(G2) - set(G1)]
    deleted_nodes=[str(i) for i in set(G1) - set(G2)]
    print _("New:"), ", ".join(new_nodes)
    print _("Deleted:"), ", ".join(deleted_nodes)

    new_edges = []
    counter = 0
    edges = G2.edges()
    del G2
    for edge in edges:
        if not G1.has_edge(edge):
            edge = [str(i) for i in edge]
            counter += 1
            new_edges.append(edge)
    print _("There is %d new edges. (%s->%s)") % (counter, dot1, dot2)

    changes = {}
    changes["new nodes"] = new_nodes
    changes["deleted nodes"] = deleted_nodes
    changes["new edges"] = new_edges

    if to_shelf:
        db= "packages.db"
        print _("I save changes into %s.") % db
        shelf = shelve.open(db)

        head, tail = os.path.split(dot1)
        root1, ext = os.path.splitext(tail)
        head, tail = os.path.split(dot2)
        root2, ext = os.path.splitext(tail)

        shelf["changes %s->%s" %(root1, root2)] = changes
        shelf.close()
    return changes

def analyze_changes(changes):
    new_edges = new_edges_between_old = changes['new edges'][:]
    new_nodes = changes['new nodes']

    for n1, n2 in new_edges:
        if n1 in new_nodes or n2 in new_nodes:
            new_edges_between_old.remove([n1,n2])
    return new_edges_between_old

if __name__ == "__main__":
    #main()
    #exit(0)
    starttime = time()
    print hms(), "start"
    #changes = changes("ubuntu_packages2008-07-23.dot","ubuntu_packages2008-08-06.dot") #"ubuntu_packages2008-07-23.dot",
    #print changes


    f=open("degree_distrib_data.txt", "a")
    f.write("".join(["\n", "*"*30, "\n"]))
    f.write(strftime("%Y/%m/%d %H:%M:%S\n", localtime()))
    f.close()
    G = get_graph()
    degree_distribution(G, 'all', save_as='degree_dist_fitted.pdf',
        args = {"cumulative":False,
          "fitting":True,
          "my_adjusted":True,
          "in":{"intervals":[(3,None,"k","power-law fit")]},
          "out":{"intervals":
             [(3,29,"k--",u"power-law fit, $k_{out}<30$"),
              (30,None,"k-.",u"power-law fit, $k_{out}>=30$"),
              (3,None,"k","power-law fit")]
              },
          "in_out":{"intervals":[(5,None,"k","power-law fit")]}  #, (41,None)
          })

    #get_near_edges(imax=1000)
    #print all_providers()

    #G30 = G.percented_graph(30)

    # fit_powerlaw([1,2,3], [1,4,9])
    # fit_powerlaw([1,2,3], [24, 12, 8])
    print hms(), "stop"
    time = time() - starttime
    print "It took %f seconds = %f minutes" % (time, time/60)
    exit(0)
    #_old_main(direction='in', dot_file='ubuntu_packages.dot', from_dotfile = from_dotfile)
