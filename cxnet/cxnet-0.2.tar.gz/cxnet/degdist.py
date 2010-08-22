#!/usr/bin/env python
# coding: utf-8
from __future__ import division

try:
    import gettext
    transl = gettext.translation("packages", "/home/ha/num/complex_network/locale")
    # transl = gettext.translation("packages", "/usr/share/locale") #Ha rootként tudom elhelyezni.
    _ = transl.ugettext
except ImportError:
    _ = lambda str: str
except IOError:
    _ = lambda str: str

from math import log, sqrt
try:
    import pylab
except (ImportError, RuntimeError):
    pylab_module = False
else:
    pylab_module = True

import sys

split = lambda tl: ([x for x, y in tl], [y for x, y in tl])

def logarithmic_binning(dd, l=1, mult=2):
    if not isinstance(dd[0], tuple):
        dd = [(i, dd[i]) for i in range(len(dd)) if dd[i] != 0]
    n = dd[-1][0]
    start, stop = 1, l+1
    ebin = []
    osztopontok = [start]
    while start < n:
        summa = sum( p for k, p in dd if start<= k < stop )
        ebin.append(summa/(stop-start))
        osztopontok.append(stop)
        l = l*mult
        start=stop
        stop = stop+l
        #import pdb; pdb.set_trace()
       
    return ebin, osztopontok

class DegreeDistribution:
    """A degree distribution of a network.

    Input:
      network_or_degree_list: the investigated network (NetworkX or IGraph)
         or the list of degrees.
      direction [optional]: "in", "out", None [default]
         the direction of the connection to count.

    variables:
      dd: the degree distribution az a pair of (k, p_k) values
      dd_smeared: as the dd, but with bin smearing
      max_deg: maximum of degree
      number_of_vertices: the number of vertices in the network
      n_0: the number of vertices with zero degree

    functions:
      plot, loglog, semilogy, errorbar: Plotting functions as in pylab.
      summary: Write informations to screen or file about the distribution.
      bin_smearing: Return the bin smeared distribution.
      set_binning: Set the type of the binning.
         'all' will use all of the degrees,
         'log' is for logarithmic binning,
         'ondemand' is a special binning not described here.
         Return the bin smeared distribution.
      cumulative_distribution: Return the cumulative distribution.
      cumulative_plot: Plots the cumulative distribution.
    """

    def __init__(self, network_or_degree_list, verbose=True, **kwargs):
        """Make, analyse and plot the degree distribution.

        """

        self.verbose=verbose

        self.kwargs = kwargs
        self.gamma = None # The absolute value of exponent

        self.direction = kwargs.get("direction")

        # Argument can be a network or a degree list.
        # We create degree list self.deg
        if isinstance(network_or_degree_list, (tuple, list)):
            self.deg = network_or_degree_list
            network = None
        else:
            network = network_or_degree_list
            # We can use NetworkX or IGraph modules.
            use_networkx =  ("adj" in dir(network))
            if self.direction is None:
                self.deg = network.degree()
            elif self.direction == "in":
                if use_networkx:
                    self.deg = network.in_degree()
                else:
                    self.deg = network.indegree()
            elif self.direction == "out":
                if use_networkx:
                    self.deg = network.out_degree()
                else:
                    self.deg = network.outdegree()

        if self.direction is None:
            self.index = ""
            self.degree_type = "plain degree"
        elif self.direction == "in":
            self.index = "_in"
            self.degree_type = "in-degree"
        elif self.direction == "out":
            self.index = "_out"
            self.degree_type = "out-degree"

        self.max_deg = max(self.deg)

        self.dd=[(i, self.deg.count(i)) for i in range(self.max_deg+1)]
        self.n_0 = self.dd[0][1]
        self.dd=[(i, j) for i, j in self.dd if i > 0 and j > 0]
        self.number_of_vertices = len(self.deg)
        self.dd=[(i, j/self.number_of_vertices) for i, j in self.dd]

        self.binning = kwargs.get("binning") 
        if self.binning is not None:
            self.bin_smearing()

    def cumulative_distribution(self):
        """Return the cumulative degree distribution

        The distribution is a list of (k, P(>k)) pairs.
        """

        cum_dd = []
        sum_p = 0
        for k, p in reversed(self.dd):
            sum_p += p
            cum_dd.append((k, sum_p))
        return list(reversed(cum_dd))

    def cumulative_plot(self, **kwargs):
        """Plot the cumulative distribution."""
        x,y = split(self.cumulative_distribution())
        p = pylab.loglog(x,y, **kwargs)
        pylab.xlabel("k%s" % self.index)
        pylab.ylabel("P(k%s)" % self.index)
        pylab.title(u"Cumulative %s distribution" % self.degree_type)
        return p

    def exponent(self, k_min=None):
        """Return with exponent and sigma of exponent.
    
        Input:
         k_min [optional]: k_min in the equation referenced below, the
           minimal degree [default 5.5]

        The exponent end error are caculated with the equations written in [1]
        page 4.

        [1]
        @article{newman-2005-46,
          url = {http://arxiv.org/abs/cond-mat/0412004},
          author = {M.~E.~J. Newman},
          title = {Power laws, Pareto distributions and Zipf's law},
          journal = {Contemporary Physics},
          volume = {46},
          pages = {323},
          year = {2005},
        }

        [2]
        @misc{clauset-2007,
          url = {http://arxiv.org/abs/0706.1062},
          author = {Aaron Clauset and Cosma Rohilla Shalizi and M.~E.~J. Newman},
          title = {Power-law distributions in empirical data},
          year = {2007}
        }

        """

        if not k_min:
            k_min = 5.5
        deg = [d for d in self.deg if d > k_min]
        summa = sum(map(lambda x: log(x/k_min), deg))
        n = len(deg)
        gamma = 1 + n/summa
        sigma = sqrt(n+1) / summa

        self.gamma = gamma
        self.k_min = k_min

        return gamma, sigma

    def exponent_plot(self, k_mins=None, file="output.pdf"):
        """Plot the calculated exponents for several k_mins.

        Input:
          k_mins [optional, default None]: list of the k_mins or None
            for all of the k_min in the list k_mins calculate the exponent
            and the sigma and plot it.
          file [optional, default "output.pdf"]:
            the file for saving the plot
        """
        if k_mins == None:
            step = int(self.max_deg/20) if self.max_deg>20 else 1
            k_mins = range(1,self.max_deg,step)
            
        K=[]
        G=[]
        S=[]
        for k in k_mins:
            k_min = k - 0.5
            g,s = self.exponent(k_min)
            result =  "k_min=%.1f: %f+-%f" % (k,g,s)
            print result
            K.append(k)
            G.append(g)
            S.append(s)
        print "%f <= gamma%s <= %f" % (min(G), self.index, max(G))
        p = pylab.errorbar(K, G, yerr=S)
        pylab.xlabel("k_min")
        pylab.ylabel("gamma%s" % self.index)
        pylab.title(u"The dependence from k_min of the exponent (%s)" % \
                self.degree_type)
        #pylab.gca().set_yscale("log")
        #pylab.gca().set_xscale("log")
        pylab.savefig(file)
        return p

    def plot_powerlaw(self, **kwargs):
        """Plot a power law function with exponent self.gamma

        Keyword argumentums are forwarded to plot function.

        Return with the plot.
        """

        if not self.gamma:
            self.exponent()
        if "label" not in kwargs:
            kwargs["label"] = "$k^{-\gamma}$"
        x = pylab.linspace(self.k_min, self.max_deg, 1000)
        p = pylab.plot(x, x**(-self.gamma), "--", **kwargs)
        return p


    def plot(self, plot=None, **kwargs):
        """Plot the bin smeared degree distribution.

        """

        """
        There was an input earlier
          intervals: list of pairs of (min, max)
          fitted point are where min <= degree <= max.
          If you want to fit the whole, set min to 0 and
          max to bigger than the greatest degree.
          In this case fitting is from the smallest non zero
          degree to the largest degree.
        """

        try:
            dd = self.dd_smeared
        except AttributeError:
            print """You need to run dd.set_binning(b) first.
Examples:
    dd.set_binning()
    dd.set_binning('all')
    dd.set_binning('log')
    dd.set_binning('ondemand')
if your DegreeDistribution object is called dd.
The result of the first two examples are the same.
"""
            return
        if plot is None:
            plot=pylab.plot
        x,y = split(dd)
        x=pylab.array(x)
        if "label" not in kwargs:
            if self.direction in ["in", "out"]:
                index = "_{%s}" % self.direction 
            else:
                index = ""
            kwargs["label"] = "$p(k%s)$" % index
        p = plot(x,y,".", **kwargs)
        pylab.xlabel("k%s" % self.index)
        pylab.ylabel("p(k%s)" % self.index)
        title = u"%s distribution" % self.degree_type
        pylab.title(title.capitalize())
        pylab.show()
        return p

    def loglog(self, **kwargs):
        """Plot the bin smeared degree distribution
        with loglog scales (log scale in each axes).

        """
        return self.plot(plot=pylab.loglog, **kwargs)

    def semilogy(self, **kwargs):
        """Plot the bin smeared degree distribution
        with semilogy scales (log scale in y axis).

        """
        return self.plot(plot=pylab.semilogy, **kwargs)

    def errorbar(self, **kwargs):
        """Plot the degree distribution with the fits.

        """

        dd = self.dd_smeared

        if "label" not in kwargs:
            if self.direction in ["in", "out"]:
                index = "_{%s}" % self.direction 
            else:
                index = ""
            kwargs["label"] = "$p(k%s)$" % index
        if "marker" not in kwargs:
            kwargs["marker"] = ""

        x,y = split(dd)
        xerr_r = [ (self.osztopontok[i+1] - x[i]) for i in range(len(dd)) ]
        xerr_l = [ (x[i] - self.osztopontok[i])  for i in range(len(dd)) ]
        p = pylab.errorbar(x,y,xerr=[xerr_l, xerr_r], fmt=".", **kwargs)
        pylab.gca().set_yscale("log")
        pylab.gca().set_xscale("log")

        pylab.show()
        return p

    def summary(self, verbosity=0, file=None):
        """Write informations to screen or file about the distribution.
        
        Input:
        
          file: if string, it will be the name of the file,
                if None (default), it will write to screen (stdout).
          verbosity: integer (0,1,2), default 0
                The bigger the value is, the more information you get.
        """
        
        if type(file) == type(""):
            f=open(file, "w")
        else: f= sys.stdout

        f.write(_("The number of vertices is %d. ") % self.number_of_vertices)
        f.write(_("The largest %s is %d.\n") % (self.degree_type, self.max_deg))
        f.write(_("The number of vertices with zero %s is %d (%5.3f%%)\n") % \
            (self.degree_type, self.n_0, self.n_0/self.number_of_vertices*100))

        f.write("\nAdott fokszám esetén annak valószínűsége,\nhogy egy vertexet véletlenszerűen kiválasztva ekkora lesz a fokszáma:\n")
        column=1
        for degree, probability in self.dd:
            f.write(" %5d:%7.4f%%" % (degree, probability*100))
            if column == 5:
                f.write("\n")
                column=1
            else: column += 1
        f.write("\n")

    def bin_smearing(self):
        """Calculates the binned distribution."""
        x = [i for i, j in self.dd]
        if self.binning in ["all", None]:
            dd_smeared = self.dd
        elif self.binning in ["log", "logarithmic"]:
            # borders like 1,2,4,8,16
            probabilities, osztopontok = logarithmic_binning(self.dd, l=1, mult=2)
            self.osztopontok = osztopontok
            mean_degrees = [sqrt(osztopontok[i]*osztopontok[i+1]) for i in range(len(probabilities))]
            dd_smeared =  zip(mean_degrees, probabilities)
        elif self.binning == "ondemand":
            belso_osztopontok = [sqrt(x[i]*x[i+1])  for i in range(len(self.dd)-1)]
            elso_osztopont = x[0]**2/belso_osztopontok[0] 
            utolso_osztopont =  x[-1]**2/belso_osztopontok[-1]
            self.osztopontok = [elso_osztopont] + \
                belso_osztopontok + \
                [utolso_osztopont]
            dd_smeared = [
                (self.dd[i][0], self.dd[i][1]/(self.osztopontok[i+1]
                -self.osztopontok[i]))  for i in range(len(self.dd))
                ]
        else:
            print "There is no binning called '%s'" % self.binning
            return

        self.dd_smeared = dd_smeared
        return dd_smeared

    def set_binning(self, binning=None):
        """Sets the type of binning, and calculates the binned distribution."""
        if binning is not None and binning == self.binning:
            return
        self.binning = binning
        self.bin_smearing()

# I think it is half-ready.
class PowerLawDistribution:
    """Return a power-law distribution.
    
    Input:
        gamma: the exponent.
        xmin
        error
    
    Method:
        cumulative_distribution()
    """

    def __init__(self, gamma, xmin=1, error=1e-5):
        self.gamma = gamma
        self.xmin = xmin
        self.error = error
        x = pylab.exp(-pylab.log(error)/gamma) 
        xmax = int(x+1)
        zeta = 0.0
        cumdist = []
        for i in reversed(range(xmin, xmax+1)):
            value = i ** (-gamma)
            zeta += value
            cumdist.append([i, zeta])
        for i in range(len(cumdist)):
            cumdist[i][1] /= zeta
        self.cumdist = cumdist
        self.zeta = zeta

    def cumulative_distribution(self):
        return self.cumdist

def KolmogorovSmirnoff_statistics(dd1, dd2):
    """Return the Kolmogorov-Smirnoff statistic"""
    cum1 = dd1.cumulative_distribution()
    cum2 = dd2.cumulative_distribution()
    minimum = max(cum1[0][0],  cum2[0][0])
    maximum = max(cum1[-1][0], cum2[-1][0])
    index1 = len(cum1)-1
    index2 = len(cum2)-1
    summa1 = summa2 = 0

    for i in reversed(range(minimum, maximum+1)):
        if cum1[index1][0] == i:
            summa1 = cum1[index1][1]
            index1 -= 1
        if cum2[index2][0] == i:
            summa2 = cum2[index2][1]
            index2 -= 1
        if abs(summa1 - summa2) > difference:
            difference = abs(summa1 - summa2)
    return difference

#if False:
if __name__ == "__main__":
    sys.path.insert(0, ".")
    sys.path.insert(0, "..")
    import networkx
    g = networkx.barabasi_albert_graph(10000, 4)
    dd = DegreeDistribution(g)

    dd.summary()
    dd.summary("info.txt")
    print dd.exponent()
    dd.cumulative_plot()
    pylab.show()

    #dd.set_binning("ondemand")
    #dd.plot()
    #dd.loglog()
    #dd.errorbar()
