import sys


if len(sys.argv) < 3:
  raise Exception, """

   Usage:
      
      python benchmark.py <algorithm_code> <benchmark_name> <opts>

   Where opts includes, in any order:

      --pop=<int>           Size of population
      --gens=<int>          # of generations
      --dim=<int>           # of dimensions

      --seg=<name>          Choose a name for the Segment for this run
      --memory              Run in memory SQLite
      --sqlite=<path>       Path to sqlite database (must exist)!
      --db=<name>           Name of the database, default "evo" (must exist)!
      --backend=<module>    Qualified path to Django backend (postgres default, or SQLite if --memory or --sqlite are present)
"""

algorithm = sys.argv[1]
benchmark = sys.argv[2]

populationSize = 100
generations = 100
dimension = 5
segment = 'test'
setupParams = {}
for arg in sys.argv[3:]:
   if arg[:6] == '--pop=':
      populationSize = int(arg[6:])
   elif arg[:7] == '--gens=':
      generations = int(arg[7:])
   elif arg[:6] == '--dim=':
      dimension = int(arg[6:])
   elif arg == '--memory':
      setupParams['inmemory'] = True
   elif arg[:10] == '--backend=':
      setupParams['backend'] = arg[10:]
   elif arg[:9] == '--sqlite=':
      setupParams['sqlite'] = arg[9:]
   elif arg[:5] == '--db=':
      setupParams['db'] = arg[5:]
   elif arg[:6] == '--seg=':
      segment = arg[6:]

from pyec.config import setup_environment, shutdown_environment
setup_environment(**setupParams)      
      
from pyec.util.registry import ALGORITHMS, BENCHMARKS

alg = ALGORITHMS.load(algorithm)
alg = alg.configure(generations, populationSize, dimension, benchmark)
model = alg.run(segment)


if algorithm == 'mixture':
   if benchmark == 'randomrbmdata':
      print "base: ", model.base.w
      print "learned: ", model.model.w

   # test the distribution
   from numpy import *
   from pyec.db.models import ScoreTree
   from pyec.distribution.ec.selectors import ProportionalAnnealing
   from pyec.util.TernaryString import TernaryString
   from pyec.util.kldiv import KullbackLeiblerDivergence
   kl = KullbackLeiblerDivergence(50)
   
   size = 10000
   Z = model.partition()
   print "got partition: ", Z
   alg.config.varInit = 0.1
   #alg.config.crossoverProb = 0.0
   #alg.config.taylorDepth = 1
   #alg.generation -= 1
   #segment = alg.selectors[-1].segment
   #alg.selectors[-1] = ProportionalAnnealing(alg.config)
   #alg.subs[0] = alg.selectors[-1]
   #alg.selectors[-1].segment = segment
   #alg.selectors[-1].n = alg.generation
   #ScoreTree.objects.resetTaylor(alg.selectors[-1].segment, 1.0, alg.config)
   #alg.selectors[-1].temp = 1.0
   mix = alg.batch(size)
   print "got mixture sample"
   gibbs = model.swendsenwang(size)
   print "got swendsen-wang sample"
   st = model.simulatedTempering(size)
   print "got simulated tempering sample"
   mix = [x.toArray(alg.config.dim) for x in mix]
   gibbs = [x.toArray(alg.config.dim) for x in gibbs]
   st = [x.toArray(alg.config.dim) for x in st]
   
   klmixrbm = kl.approximateOneBits(mix, lambda x: exp(model(TernaryString.fromArray(x))), alg.config.dim) + log(Z)
   klgibbsrbm = kl.approximateOneBits(gibbs, lambda x: exp(model(TernaryString.fromArray(x))), alg.config.dim) + log(Z)
   klstrbm = kl.approximateOneBits(st, lambda x: exp(model(TernaryString.fromArray(x))), alg.config.dim) + log(Z)
   # klmixgibbs = kl.approximate(mix, gibbs)
   # klgibbsmix = kl.approximate(gibbs,mix)
   # klsanity = kl.approximate(mix, mix)
      
   
   print "KL, mixture || rbm : ", klmixrbm
   print "KL, sw || rbm : ", klgibbsrbm
   print "KL, st || rbm : ", klstrbm
   #print "KL, mixture || gibbs : ", klmixgibbs
   #print "KL, gibbs || mixture : ", klgibbsmix
   
   print "KL diff, mixture - sw", klmixrbm - klgibbsrbm
   print "KL diff, mixture - st", klmixrbm - klstrbm
   #print "KL diff, sanity : ", klsanity
   
   
   """
   
   xs = []
   x = 0L
   known = (1L << alg.config.dim) - 1L
   for i in xrange(1 << alg.config.dim):
      xs.append(TernaryString(x, known))
      x += 1L
   ds = alg.density(xs)
   realds = array([model(x) for x in xs])
   realds = exp(realds)
   realds /= realds.sum()
   
   
   
   i = 0L
   for model, rbm in zip(ds, realds):
      print i, ": ", model, rbm
      i += 1L
   
   kl1 = (ds * (log(ds) - log(realds))).sum()  
   print "KL, mixture || rbm : ", kl1
   kl2 = (realds * (log(realds) - log(ds))).sum()
   print "KL, rbm || mixture : ", kl2
   
   print "average diff: ", average(abs(ds - realds))
   
   import pylab
   pylab.plot(maximum((ds),-50), 'g-')
   pylab.plot(maximum((realds), -50), 'b-')
   pylab.show()
   
   """
   
   
   
shutdown_environment(**setupParams)       

