from numpy import *
from pyec.util.graphs import *
from pyec.util.benchmark import *

toShuffle = [i for i in xrange(29)]
random.shuffle(toShuffle)
print "shuffled: ", toShuffle
toShuffle = toShuffle[:25]



def exp2(f):
   def g(x):
      return (f(x)**(1./10.))
   g.center = f.center
   g.scale = f.scale
   g.name = f.name
   return g

def log2(f):
   def g(x):
      fx = f(x)
      return log(abs(fx))
   g.center = f.center
   g.scale = f.scale
   g.name = f.name
   return g

def neg(f):
   def g(x):
      return -f(x)
   g.center = f.center
   g.scale = f.scale
   g.name = f.name
   return g

def bound(f, b):
   def g(x): 
      return -f(x)
   g.center = f.center
   g.scale = b
   g.name = f.name
   return g
"""
plotBenchmarkContour(neg(sphere()), 5000)
plotBenchmarkContour(log2(rosenbrock()), 5000)
plotBenchmarkContour(neg(rastrigin()), 5000)
plotBenchmarkContour(neg(langerman()), 5000)
plotBenchmarkContour(bound(griewank(),50), 5000)
plotBenchmarkContour(neg(salomon()), 5000)
plotBenchmarkContour(neg(schwefel()), 5000)
plotBenchmarkContour(weierstrass(), 5000)
plotBenchmarkContour(neg(shekel2()), 5000)
plotBenchmarkContour(shekelsFoxholes(), 5000)
plotBenchmarkContour(neg(ackley()), 5000)
#plotBenchmarkContour(bound(exp2(whitley()), 1.0), 1000)
"""

algs = ["rea","reaTournament", "de","pso","cmaes", "ga", "boa"]
legend = ["REA-P", "REA-T", "DE", "PSO", "CMA-ES", "GA", "rBOA"]
format = [{"color":"black", "ls":"-", "lw":4}, 
          {"color":"#999999", "ls":"-", "lw":4}, 
          {"color":"black", "ls":"-", "lw":2},
          {"color":"#999999", "ls":"-", "lw":2},
          {"color":"black", "ls":"--", "lw":2},
          {"color":"#999999", "ls":"--", "lw":2},
          {"color":"black", "ls":"-.", "lw":2}]
algos = zip(algs, legend, format)

names = ["sphere", "whitley", "shekel2", "rosenbrock", "rastrigin", "salomon", "schwefel", "langerman", "weierstrass", "griewank", "ackley"]

for name in names:
   plotComparison(algos,name, plotEpsilons)
   plotComparison(algos,name, plotLogMaxComps)
   plotComparison(algos,name, plotAvgComps)
   plotComparison(algos,name, plotMaxComps)

#plotGathered(plotLogMax,'.*\.data')

