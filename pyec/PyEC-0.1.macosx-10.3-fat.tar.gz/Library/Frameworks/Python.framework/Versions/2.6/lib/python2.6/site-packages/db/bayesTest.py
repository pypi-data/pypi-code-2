from evo.util.distribution.bayes.net import BayesNet
from evo.util.distribution.bayes.structure.proposal import (StructureProposal, ProbDecayEdgeRatio)
from evo.util.distribution.bayes.structure.greedy import GreedyStructureSearch
from evo.util.distribution.bayes.sample import BinaryRandomizer
from evo.util.distribution.bayes.variables import BinaryVariable
from evo.util.distribution.bayes.score import (BayesianDirichletScorer, BayesianInformationCriterion)
from evo.util.distribution.mixture import BayesMixture
from evo.util.distribution.sa import SimulatedAnnealing
from evo.util.trainer import Config, Trainer

from evo.grid.models import GridSegment, GridPoint, GridPartition

from numpy import *

cfg = Config()
cfg.numVariables = 10
cfg.learningRate = 1.0
BayesMixture.config(cfg)
cfg.mergeProb = 1.0
cfg.varExp = 0.25
cfg.populationSize = 25
cfg.generations = 250
cfg.variableGenerator = BinaryVariable
cfg.randomizer = BinaryRandomizer()
cfg.initialDistribution = StructureProposal(cfg)


# generate a random net
cmp = cfg.initialDistribution()
for i in xrange(cfg.numVariables):
   cmp.structureSearch(None)

cmp.computeEdgeStatistics()
print "cmp: ", cmp.edges
   
data = []
for i in xrange(1000):
   data.append(cmp())
cfg.data = data
#print "data:", str(cfg.data)
print "data likelihood: ", cmp.likelihood(data)



cfg.segment = 'bayes.test'
scorerGen = BayesianInformationCriterion() 
#scorerGen = BayesianDirichletScorer()
scorer = lambda x: scorerGen(x, cfg.data)
logscorer = lambda x: -log(abs(scorerGen(x, cfg.data)))

print "ref score: ", scorer(cmp), scorerGen(cmp, cfg.data)

mixture = BayesMixture(cfg)
trainer = Trainer(scorer, mixture, cfg)
trainer.train()


print "testing SA"
cfg.segment = 'bayes.sa.test'
cfg.initial = cfg.proposal = cfg.initialDistribution
cfg.generations = 12500
cfg.populationSize = 1
cfg.usePrior=True
cfg.varInit=1
cfg.divisor = 100.
cfg.restartProb = .01
sa = SimulatedAnnealing(cfg)
trainer = Trainer(scorer, sa, cfg)
trainer.train()

print "testing greedy"
greedy = BayesNet(cfg.numVariables, cfg.variableGenerator, GreedyStructureSearch(3,scorerGen), cfg.randomizer)
greedy.structureSearch(cfg.data)
sc = scorer(greedy)
print "greedy score: ", sc

sasegment = GridSegment.objects.get(name=cfg.segment)
sanet = GridPoint.objects.filter(segment=sasegment).order_by('-score')[0].bayes


cfg.segment = 'bayes.test'

segment = GridSegment.objects.get(name=cfg.segment)
net = GridPoint.objects.filter(segment=segment).order_by('-score')[0].bayes

sanet.computeEdgeStatistics()
net.computeEdgeStatistics()
print "EA score: ", scorer(net), logscorer(net)
print "SA score: ", scorer(sanet), logscorer(sanet)
print "EA likelihood: ", net.likelihood(data)
print "SA likelihood: ", sanet.likelihood(data)
print "base likelihood: ", cmp.likelihood(data)
print "EA: ", net.edges
print "SA: ", sanet.edges

"""
testpoints = []
for i in xrange(100):
   pt = cfg.randomizer(net)
   netp = net.density(pt)
   cmpp = cmp.density(pt)
   #print "probs: ", netp, cmpp
   kl = netp * log(netp/cmpp)
   testpoints.append(kl)

print "KL: ", array(testpoints).sum() / len(testpoints)
"""
