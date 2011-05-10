from django.utils.importlib import import_module
from pyec.config import ConfigBuilder
# from pyec.distribution.basic import PopulationDistribution

class RegistryCodeNotFound(Exception):
   pass
   
class BadRegistryEntry(Exception):
   pass

class Registry(object):
   registry = {}
   def __init__(self, parentCls):
      self.parentCls = parentCls
   
   def update(self, code, path):
      self.registry.update({code:path})

   def load(self, code):
      if self.registry.has_key(code):
         try:
            path = self.registry[code]
            pkg,cls = path.rsplit('.',1)
            mod = import_module(pkg)
            cls = getattr(mod, cls)
            #if not issubclass(cls, self.parentCls):
            #   raise BadRegistryEntry, "Item registered at code " + str(code) + " is not a subclass of " + parentCls.__name__
            return cls()
         except:
            raise BadRegistryEntry, "Could not load " + str(path) + " associated to code " + str(code)
      else:
         raise RegistryCodeNotFound, "Could not find code " + str(code)

BENCHMARKS = Registry(object)
BENCHMARKS.registry = {
   'sphere':'pyec.util.benchmark.sphere',
   'ellipsoid':'pyec.util.benchmark.ellipsoid',
   'rotatedEllipsoid':'pyec.util.benchmark.rotatedEllipsoid',
   'rosenbrock':'pyec.util.benchmark.rosenbrock',
   'rastrigin':'pyec.util.benchmark.rastrigin',
   'miscaledRastrigin':'pyec.util.benchmark.miscaledRastrigin',
   'schwefel':'pyec.util.benchmark.schwefel',
   'salomon':'pyec.util.benchmark.salomon',
   'whitley':'pyec.util.benchmark.whitley',
   'ackley':'pyec.util.benchmark.ackley',
   'ackley2':'pyec.util.benchmark.ackley2',
   'langerman':'pyec.util.benchmark.langerman',
   'shekelsFoxholes':'pyec.util.benchmark.shekelsFoxholes',
   'shekel2':'pyec.util.benchmark.shekel2',
   'rana':'pyec.util.benchmark.rana',
   'griewank':'pyec.util.benchmark.griewank',
   'weierstrass':'pyec.util.benchmark.weierstrass',
   'randomrbm':'pyec.util.benchmark.randomrbm',
   'randomrbmdata':'pyec.util.benchmark.randomrbmdata'
}     

ALGORITHMS = Registry(object) # PopulationDistribution)
ALGORITHMS.registry = {
   'rga':'pyec.distribution.ec.ga.RGAConfigurator',
   'ga':'pyec.distribution.ec.ga.GAConfigurator',
   'rboa':'pyec.distribution.eda.RBoaConfigurator',
   'boa':'pyec.distribution.eda.BoaConfigurator',
   'de':'pyec.distribution.de.DEConfigurator',
   'sa':'pyec.distribution.sa.SAConfigurator',
   'bea':'pyec.distribution.ec.evoanneal.BEAConfigurator',
   'rea':'pyec.distribution.ec.evoanneal.REAConfigurator',
   'reaTournament':'pyec.distribution.ec.evoanneal.REATournamentConfigurator',
   'cmarea': 'pyec.distribution.ec.evoanneal.CMAREAConfigurator',
   'crossrea': 'pyec.distribution.ec.evoanneal.CrossedREAConfigurator',
   'bayesea': 'pyec.distribution.ec.evoanneal.BayesEAConfigurator',
   'pso':'pyec.distribution.pso.PSOConfigurator',
   'cmaes':'pyec.distribution.ec.evoanneal.ESConfigurator',
   'mixture':'pyec.distribution.ec.evoanneal.MixtureSamplerConfigurator'
}


__all__ = ['BENCHMARKS','ALGORITHMS']
