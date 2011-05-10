from pyec.distribution.ec.mutators import Crosser, Mutation

class Merger(Crosser):
   def __call__(self, nets):
      net = nets[0]
      if random.random_sample() < net.config.mergeProb:
         for net2 in nets[1:]:
            net.merge(net2, net.config.data)
         
class StructureMutator(Mutation):
   def __init__(self, config):
      super(StructureMutator, self).__init__(config)
      self.decay = 1.0

   def mutate(self, net):
      net.decay = self.decay
      return net.structureSearch(net.config.data)

   def update(self, n, population):
      self.decay = (self.n * self.config.varDecay) ** self.config.varExp
