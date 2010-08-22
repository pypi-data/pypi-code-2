#!/usr/bin/env python
# coding: utf-8
from __future__ import division

try:
    import gettext
    transl = gettext.translation("packages", "../locale")
    # transl = gettext.translation("packages", "/usr/share/locale") #Ha rootként tudom elhelyezni.
    _ = transl.ugettext
except ImportError:
    _ = lambda str: str

import pylab
import lknegyzetek

# TODO  a lknegyzetekbe kellene rakni?
def power_law_fitting(xy_pairs):
    """Hatványfüggvénnyel közelíti a fokszámeloszlást.

    A hatványfüggvény alakja y=A*x^k.
    """

    x=[i for i,j in xy_pairs if j!=0 and i!=0]
    y=[j for i,j in xy_pairs if j!=0 and i!=0]
    lgx=pylab.log10(x)
    lgy=pylab.log10(y)
    k,lgA = lknegyzetek.linearis(lgx,lgy)
    return k, 10**lgA

class DegreeDistribution:
    """A degree distribution of a graph.

    variables:
      dd: the degree distribution az a pair of (k, p_k) values
      dd_smeared: as the dd, but with bin smearing
      max_deg: maximum of degree
      number_of_nodes: the number of nodes in the graph
      n_0: the number of nodes with zero degree

    functions:
      plot, loglog, semilogy: plotting functions as in pylab
      info: write informations to screen or file about the distribution
    """

    def __init__(self, graph, direction=None, verbose=True):
        """Make the degree distribution.

        Input:
          graph: the investigated graph (MyDiGraph)
          bin_smearing (boolean): whether to apply bin smearing
        """

        self.verbose=verbose

        if direction is None:
            degree = graph.degree
        if direction == "in":
            degree = graph.in_degree
        if direction == "out":
            degree = graph.out_degree

        deg=degree()
        self.max_deg = max(deg)
        self.dd=[(i, deg.count(i)) for i in range(self.max_deg+1)]
        self.n_0 = self.dd[0][1]

        self.dd=[(i, j) for i, j in self.dd if i > 0 and j > 0]

        self.number_of_nodes = graph.number_of_nodes()
        self.dd=[(i, j/self.number_of_nodes) for i, j in self.dd]

        # bin smearing
        x = [i for i, j in self.dd]
        belso_osztopontok = [pylab.sqrt(x[i]*x[i+1])  for i in range(len(self.dd)-1)]
        elso_osztopont = x[0]**2/belso_osztopontok[0] 
        utolso_osztopont =  x[-1]**2/belso_osztopontok[-1]
        self.osztopontok = [elso_osztopont] + belso_osztopontok + [utolso_osztopont]
        self.dd_smeared = [(self.dd[i][0], self.dd[i][1]/(self.osztopontok[i+1]-self.osztopontok[i]))  for i in range(len(self.dd))]

    def plot(self, intervals=None, plot=pylab.plot):
        """Plot the degree distribution with the fits.

        Input:
          intervals: list of pairs of (min, max)
            fitted point are where min <= degree <= max.
            If you want to fit the whole, set min to 0 and
            max to bigger than the greatest degree.
            In this case fitting is from the smallest non zero
            degree to the largest degree.
        """

        dd = self.dd_smeared

        x=[i for i,j in dd]
        y=[j for i,j in dd]
        plot(x,y,".")
        if intervals:
            pylab.hold(True)
            for min, max in intervals:
                if max > self.max_deg:
                    max = self.max_deg
                if min <= 0:
                    min = dd[0][0]
                dd_part = [ (i,j) for i,j in dd if min <= i <= max ]
                k, A = power_law_fitting(dd_part)
                if self.verbose:
                    print "exponent: %f" % k
                x = pylab.linspace(min, max)
                plot(x, A*x**k)
            pylab.hold(False)
        pylab.show()

    def loglog(self, intervals=None):
        self.plot(intervals, plot=pylab.loglog)

    def semilogy(self, intervals=None):
        self.plot(intervals, plot=pylab.semilogy)

    def errorbar(self, intervals=None):
        """Plot the degree distribution with the fits.

        Input:
          intervals: list of pairs of (min, max)
            fitted point are where min <= degree <= max.
            If you want to fit the whole, set min to 0 and
            max to bigger than the greatest degree.
            In this case fitting is from the smallest non zero
            degree to the largest degree.
        """

        dd = self.dd_smeared

        x=[i for i,j in dd]
        y=[j for i,j in dd]
        xerr_r = [ (self.osztopontok[i+1] - x[i]) for i in range(len(dd)) ]
        xerr_l = [ (x[i] - self.osztopontok[i])  for i in range(len(dd)) ]
        pylab.errorbar(x,y,xerr=[xerr_l, xerr_r], fmt=".")
        pylab.gca().set_yscale("log")
        pylab.gca().set_xscale("log")

        if intervals:
            pylab.hold(True)
            for min, max in intervals:
                if max > self.max_deg:
                    max = self.max_deg
                if min <= 0:
                    min = dd[0][0]
                dd_part = [ (i,j) for i,j in dd if min <= i <= max ]
                k, A = power_law_fitting(dd_part)
                if self.verbose:
                    print "exponent: %f" % k
                x = pylab.linspace(min, max)
                pylab.loglog(x, A*x**k)
            pylab.hold(False)
        pylab.show()

    def info(self, file=None):
        """Write informations to screen or file about the distribution.

      Input:
          file: if string, it will be the name of the file,
                if None (default), it will write to screen (stdout).
    """

        if type(file) == type(""):
            f=open(file, "w")
        else: f= sys.stdout

        f.write(_("The number of nodes is %d. ") % self.number_of_nodes)
        f.write(_("The biggest degree is %d.\n") % self.max_deg)
        f.write(_("The number of nodes with zero degree is %d (%5.3f%%)\n") % (self.n_0, self.n_0/self.number_of_nodes*100))

        f.write("\nAdott fokszám esetén annak valószínűsége,\nhogy egy csomópontot véletlenszerűen kiválasztva ekkora lesz a fokszáma:\n")
        column=1
        for degree, probability in self.dd:
            f.write(" %5d:%7.4f%%" % (degree, probability*100))
            if column == 5:
                f.write("\n")
                column=1
            else: column += 1
        f.write("\n")

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "..")
    # import packages
    # G=packages.get_graph()
    import networkx
    G = networkx.barabasi_albert_graph(10000, 4)
    DD = DegreeDistribution(graph=G)
    #print "Osztópontok", DD.osztopontok

    DD.info()
    DD.info("info.txt")

    #DD.plot()
    #DD.loglog([(1,100), (101, 20000), (0,100000)])
    try:
	DD.errorbar([(1,100), (101, 20000), (0,100000)])
    except:
	print "Nem tudtam kirajzolni a grafikont. Nincs grafikus felület?"
