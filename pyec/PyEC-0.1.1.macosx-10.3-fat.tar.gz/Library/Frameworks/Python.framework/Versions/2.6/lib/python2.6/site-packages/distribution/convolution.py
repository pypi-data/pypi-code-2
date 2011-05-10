from basic import PopulationDistribution



class Convolution(PopulationDistribution):
   def __init__(self, subs, initial = None):
      super(Convolution, self).__init__(subs[0].config)
      self.subs = subs
      self.population = None
      self.initial = initial
      self.generation = 1
      self.scoreDict = {}

   def score(self, population):
      return [(x,self.scoreDict.get(str(x), None)) for x in population]

   def batch(self, popSize):
      if self.population is None:
         return self.initial.batch(popSize)
      population = [x for x,s in self.population]
      scoredPopulation = self.population
      for sub in self.subs:
         sub.update(self.generation, scoredPopulation)
         population = sub.batch(popSize)
         scoredPopulation = self.score(population)
      return population

   def update(self, generation, population):
      self.generation = generation
      self.population = population
      self.scoreDict = dict([(str(x), s) for x,s in population])
