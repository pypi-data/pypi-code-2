import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pyec.settings'
os.environ['EVO_DATABASE'] = ':memory:'
os.environ['EVO_SQLITE'] = ''

from pyec.db.models import *
from numpy import *
from numpy.lib.index_tricks import nd_grid
import pylab
import math
import os.path
import cPickle
import re

import matplotlib

opts = {
   "sphere": (0.0, 0.001, 10),
   "rosenbrock": (0.0, 0.001, 10),
   "ackley": (13.37957500565419, .1, 100),
   "whitley": (0.0, .01, 10000),
   "shekelsFoxholes": (10.40561723899245, 5, 12),
   "griewank": (0.0, .001, 10),
   "langerman": (0.964999919793, .001, 10),
   "rastrigin": (0.0, .001, 10),
   "salomon": (0.0, .001, 10),
   "weierstrass": (0.0, .001, 10),
   "schwefel": (418.982887272434, .001, 10)
}

def plotGathered(plotterFunc, pattern):
   #find the /data/ directory
   utildir = os.path.dirname(__file__)
   evodir = os.path.dirname(utildir)
   phdwebdir = os.path.dirname(evodir)
   datadir = os.path.join(phdwebdir, 'data2')
   names = os.listdir(datadir)
   for name in names:
      if re.match(pattern, name):
         f = open(os.path.join(datadir, name))
         data = cPickle.load(f)
         f.close()
         plotterFunc(name, data)

class makePrintMax:
   total = 0
   successes = 0
   errtot = 0
   errcount = 0
   errors = []
   
   def __init__(self, opt, eps):
      self.opt = opt
      self.eps = eps
   
   def __call__(self, name, data):
      mx = -1e300
      gen = 10000
      for d in data:
         if d[2] > mx:
            mx = d[2]
            if abs(self.opt - mx) < self.eps and gen > 9999:
                gen = d[0]
                self.total += gen
                self.successes += 1
      self.errtot += log(abs(mx - self.opt))
      self.errcount += 1
      self.errors.append(abs(mx - self.opt))
      print name, " final: ", mx, " error: ", abs(mx - self.opt), " success: ", gen, " avg: ", self.avgSuccess(), " avgerr: ", self.avgError()
   
   def avgError(self):
      return exp(self.errtot / self.errcount)
    
   def avgSuccess(self):
      return (self.total /( self.successes + 1e-10))

def plotAvgAndMax(name, data):
   a = [d[1] for d in data]
   m = [d[2] for d in data]
   pylab.clf()
   pylab.plot(a)
   pylab.plot(m)
   pylab.axis([0, len(a), min(a), max(m)])
   pylab.savefig(os.join('graphs', name[:-5] + '.avgmax.png'))

def plotLogMax(name, data):
   global opts
   for nme, optimum in opts.iteritems():
      if nme in name:
         opt, low, high = optimum
         break 
   a = [d[1] for d in data]
   m = [d[2] for d in data]
   growth = []
   best = m[0]
   for mx in m:
      if mx > best:
         best = mx
      growth.append(opt - best)
   pylab.clf()
   pylab.semilogy()
   pylab.plot(growth)
   pylab.axis([0, 250, low, high])
   pylab.savefig(os.path.join('graphs', name[:-5] + '.logmax.png'))

class aggregator(object):
   def __init__(self, opt=None, shuffled = None, eps = 0.2):
      self.avgs = 0
      self.maxs = 0
      self.count = 0
      self.epsilons = array([10 ** (2 - i / 256.0) for i in xrange(1792)])
      self.errors = 0
      self.opt = opt
      self.shuffled = shuffled
      self.rawAvg = []
      self.rawMax = []
      self.rawErr = []

   def __call__(self, name, data):
      while self.avgs is not 0 and len(data) < len(self.avgs):
         data.append(data[-1])
      self.count += 1
      a = array([d[1] for d in data])
      m = array([d[2] for d in data])
      self.avgs = self.avgs + a
      self.maxs = self.maxs + m
      self.rawAvg.append(a)
      self.rawMax.append(m)
      if self.opt is not None:
         mx = m.max()
         error = self.opt - mx
         adjust = error < self.epsilons
         self.errors = self.errors + adjust
         self.rawErr.append(adjust)
         
      else:
         self.errors = self.avgs
      #print shape(self.avgs)

   def getAvg(self):
      if self.shuffled and len(self.shuffled) < len(self.rawAvg):
         ret = array([self.rawAvg[i] for i in self.shuffled]).sum(axis=0) / len(self.shuffled)
         print ret
         print shape(self.rawAvg)
         return ret
      else:
         return self.avgs / self.count
      
   def getMax(self):
      if self.shuffled and len(self.shuffled) < len(self.rawMax):
         return array([self.rawMax[i] for i in self.shuffled]).sum(axis=0) / len(self.shuffled)
      else:
         return self.maxs / self.count
      
   def getErrors(self):
      if self.shuffled and len(self.shuffled) < len(self.rawErr):
         return 100 * array([self.rawErr[i] for i in self.shuffled]).sum(axis=0) / len(self.shuffled)   
      else:
         return 100 * self.errors / self.count
   

def savePlot(name):
   pylab.get_current_fig_manager().canvas.resize(300, 300)
   ax = pylab.gca()
   fontsize = 18
   for label in ax.get_xticklabels():
      label.set_fontsize(fontsize)
   for label in ax.get_yticklabels():
      label.set_fontsize(fontsize)
   pylab.savefig(name, bbox_inches='tight', padding_inches=0)

def plotLogMaxComps(data, benchmark):
   global opts
   for nme, optimum in opts.iteritems():
      if nme == benchmark:
         opt, low, high = optimum
         break 
   a = [[d[1] for d in dat[1]] for dat in data]
   m = [[d[2] for d in dat[1]] for dat in data]
   cmps = []
   for cmp in m:
      growth = []
      best = cmp[0]
      #print len(cmp)
      for mx in cmp:
         if mx > best:
            best = mx
         growth.append(opt - best)
      #print len(growth)
      cmps.append(growth)
   pylab.clf()
   pylab.semilogy()
   lines = []
   idx = 0
   for cmp in cmps:
      ft = data[idx][2]
      lines.append(pylab.plot(cmp, **ft))
      idx += 1
   pylab.legend(lines, [d[0] for d in data], 'upper right')
   pylab.axis([0, 250, low, high])
   pylab.xlabel("Number of generations", fontsize=18)
   pylab.ylabel("Error from optimum, |opt - max|", fontsize=18)
   savePlot(os.path.join('graphs', benchmark + '_logmax.pdf'))

def plotAvgComps(data, benchmark):
   global opts
   for nme, optimum in opts.iteritems():
      if nme == benchmark:
         opt, low, high = optimum
         break 
   a = [[opt - d[1] for d in dat[1]] for dat in data]
   m = [[opt - d[2] for d in dat[1]] for dat in data]
   pylab.clf()
   pylab.semilogy()
   lines = []
   idx = 0
   for idx in xrange(len(data)):
      ft = data[idx][2]
      lines.append(pylab.plot(a[idx], **ft))
      idx += 1
   pylab.legend(lines, [d[0] for d in data], 'upper right')
   pylab.axis([0, 250, low, high])
   pylab.xlabel("Number of generations", fontsize=18)
   pylab.ylabel("Error from optimum, |opt - max|", fontsize=18)
   savePlot(os.path.join('graphs', benchmark + '_avgcmp.pdf'))

def plotMaxComps(data, benchmark):
   global opts
   for nme, optimum in opts.iteritems():
      if nme == benchmark:
         opt, low, high = optimum
         break 
   a = [[opt - d[1] for d in dat[1]] for dat in data]
   m = [[opt - d[2] for d in dat[1]] for dat in data]
   pylab.clf()
   pylab.semilogy()
   lines = []
   idx = 0
   for idx in xrange(len(data)):
      ft = data[idx][2]
      lines.append(pylab.plot(m[idx], **ft))
      idx += 1
   pylab.legend(lines, [d[0] for d in data], 'upper right')
   pylab.axis([0, 250, low, high])
   pylab.xlabel("Number of generations", fontsize=18)
   pylab.ylabel("Error from optimum, |opt - max|", fontsize=18)
   savePlot(os.path.join('graphs', benchmark + '_maxcmp.pdf'))


def plotEpsilons(data, benchmark):
   epsilons = [dat[3] for dat in data]
   pylab.clf()
   lines = []
   idx = 0
   for idx in xrange(len(data)):
      ft = data[idx][2]
      lines.append(pylab.plot(epsilons[idx], **ft))
      idx += 1
   pylab.legend(lines, [d[0] for d in data], 'upper right')
   pylab.axis([0, 14, 0, 100])
   pylab.xticks([256*i+256 for i in xrange(7)], ["1e%d" % (1 - i) for i in xrange(7)])
   pylab.xlabel("Accuracy, epsilon = |opt - max|", fontsize=18)
   pylab.ylabel("% of trials within accuracy", fontsize=18)
   savePlot(os.path.join('graphs', benchmark + '_epsilons.pdf'))

def plotComparison(algs, benchmark, plotter, shuffled = None):
   global opts
   for nme, optimum in opts.iteritems():
      if nme == benchmark:
         opt, low, high = optimum
         break 
   comps = []
   for alg, legend, fmt in algs:      
      agg = aggregator(opt, shuffled)
      plotGathered(agg, alg + '.' + benchmark + '\..*\.data')
      print alg, benchmark, agg.count
      comp = zip(agg.getAvg(), agg.getAvg(), agg.getMax())
      comps.append((legend, comp, fmt, agg.getErrors()))
   plotter(comps, benchmark)
   
   
def plotBenchmarkContour(benchmark, res):
   low,high = (benchmark.center - benchmark.scale, benchmark.center + benchmark.scale)
   mgrid = nd_grid()
   X = mgrid[low:high:res+0j,low:high:res+0j]
   Y = zeros((res,res))
   for i in xrange(res):
      for j in xrange(res):
         Y[i,j] = benchmark(X[:,i,j])
   pylab.clf()
   #pylab.xticks(linspace(low, high, num=5), ["%.2f" % (low + i*((high-low)/5)) for i in xrange(5)])      
   #pylab.yticks(linspace(low, high, num=5), ["%.2f" % (low + i*((high-low)/5)) for i in xrange(5)])      
   pylab.imshow(Y, cmap=pylab.cm.PuBu, origin="lower", extent=(low,high,low,high))
   savePlot(os.path.join('graphs',benchmark.name + '_contour.pdf'))
   
   
def printSuccesses(alg, func1, func, eps=0.1):
   plotGathered(makePrintMax(opts[func1][0], eps), '%s.%s.*.data' % (alg, func))
      
