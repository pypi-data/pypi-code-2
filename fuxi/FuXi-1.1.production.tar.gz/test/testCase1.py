import unittest, os, time, sys 
from pprint import pprint
from cStringIO import StringIO 
from rdflib import RDF, URIRef 
from FuXi.Rete import * 
from FuXi.Rete.Util import generateTokenSet
from FuXi.Rete.Magic import MagicSetTransformation, PrettyPrintRule
from FuXi.Rete.RuleStore import N3RuleStore, SetupRuleStore 
from FuXi.Rete.Util import renderNetwork, generateTokenSet 
from FuXi.Horn.PositiveConditions import Uniterm, BuildUnitermFromTuple 
from FuXi.DLP import PrepareHornClauseForRETE
from FuXi.Horn.HornRules import HornFromN3 
from FuXi.Syntax.InfixOWL import *
from cStringIO import StringIO
from rdflib import plugin, Namespace, Variable
from rdflib.store import Store 
from rdflib.Graph import Graph 
N3_PROGRAM=\
""" 
@prefix m: <http://example.com/#>. 
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . 
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . 

_:1 a ptrec:Event_morbidity_renal_failure_requiring_dialysis;
  ptrec:hasEventPlace ptrec:EventPlace_ccf_main_campus;
  csqr:hasHospitalization _12:fb8dfdd-d695-4750-9da9-33d2112a9433;
  fztime:startsNoEarlierThan "2010-03-07T15:51:00"^^<http://www.w3.org/2001/XMLSchema#dateTime>;
  fztime:startsNoLaterThan "2010-03-07T15:51:00"^^<http://www.w3.org/2001/XMLSchema#dateTime>. 

""" 
N3_FACTS=\
""" 
@prefix m: <http://example.com/#>. 
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . 
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . 
m:Detection a rdfs:Class. 
m:Inference a rdfs:Class. 
:det1 a m:Detection. 
:det1 m:name "Inference1". 
:det2 a m:Detection. 
:det2 m:name "Inference2". 
""" 
class ExistentialInHeadTest(unittest.TestCase): 
    def testExistentials(self): 
        store = plugin.get('IOMemory',Store)() 
        store.open('') 
        ruleStore = N3RuleStore() 
        ruleGraph = Graph(ruleStore) 
        ruleGraph.parse(StringIO(N3_PROGRAM),format='n3') 
        factGraph = Graph(store) 
        factGraph.parse(StringIO(N3_FACTS),format='n3') 
        deltaGraph = Graph(store) 
        network = ReteNetwork(ruleStore, 
                              initialWorkingMemory=generateTokenSet(factGraph), 
                              inferredTarget = deltaGraph) 
        inferenceCount = 0 
        for inferredFact in network.inferredFacts.subjects(
                                       predicate=RDF.type, 
                                       object=URIRef('http://example.com/#Inference')): 
            inferenceCount = inferenceCount + 1
        print network.inferredFacts.serialize(format='n3') 
        self.failUnless(inferenceCount > 1,  'Each rule firing should introduce a new BNode!') 
        cg = network.closureGraph(factGraph, store=ruleStore) 
        #print cg.serialize(format="n3") 

FACTS=\
""" 
@prefix ex: <http://example.com/#>. 
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . 
@prefix cpr:  <http://purl.org/cpr/> . 
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . 
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:evt1 a ex:RenalFailureRequiringDialysis;
    cpr:startsNoEarlierThan "2010-03-07T15:51:00"^^xsd:dateTime .

ex:evt2 a cpr:therapeutic-procedure, ex:QualifyingOperation .
ex:evt2 cpr:startsNoEarlierThan "2010-03-05T10:32:00"^^xsd:dateTime .

ex:evt3 ex:intervalContains ex:evt1, ex:evt2 .  
  
""" 

N3_RULES=\
"""
@prefix ex: <http://example.com/#>. 
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . 
@prefix cpr:  <http://purl.org/cpr/> . 
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . 
@prefix str:    <http://www.w3.org/2000/10/swap/string#>.

{ ?IDX_OP a ex:QualifyingOperation;
          cpr:startsNoEarlierThan ?IDX_OP_START .
 ?HOSP  ex:intervalContains  ?IDX_OP, ?EVENT .
 ?EVENT a cpr:therapeutic-procedure ;
        cpr:startsNoEarlierThan ?EVT_START .
 ?EVT_START str:greaterThan ?IDX_OP_START  } => { ?EVENT a ex:PostOpInHospitalEvent } .
"""

EX_NS  = Namespace('http://example.com/#')
EX     = ClassNamespaceFactory(EX_NS)
CPR_NS = Namespace('http://purl.org/cpr/')
CPR    = ClassNamespaceFactory(CPR_NS)             
             
derivedPredicate = [EX_NS.PostOpInHospitalEvent,EX_NS.RenalFailure]                         
             
class SkolemMachine(unittest.TestCase):
    def setUp(self):
        ruleStore,ruleGraph,network=SetupRuleStore(makeNetwork=True)
        self.network= network
        self.factGraph = Graph().parse(StringIO(SKOLEM_MACHINE_FACTS),format='n3')
        for rule in HornFromN3(StringIO(SKOLEM_MACHINE_RULES)):
            self.network.buildNetworkFromClause(rule)
        self.network.feedFactsToAdd(generateTokenSet(self.factGraph))
            
if __name__ == "__main__": 
    ontGraph = Graph()
    ontGraph.bind('ex' , EX_NS)
    ontGraph.bind('cpr', CPR_NS)
    Individual.factoryGraph = ontGraph
    renalFailure = EX.RenalFailure
    conjunct = EX.PostOpInHospitalEvent & EX.RenalFailureRequiringDialysis
    renalFailure += conjunct
    rules = set()
    rules.update(HornFromN3(StringIO(N3_RULES)))
    store, graph, network = SetupRuleStore(StringIO(N3_RULES),makeNetwork=True)
    rules.update(network.setupDescriptionLogicProgramming(
                    ontGraph,
                    derivedPreds=derivedPredicate,
                    addPDSemantics=False,
                    classifyTBox=False))
    pprint(list(rules))
    varX = Variable('x')
    goals = [(varX,RDF.type,_class) for _class in derivedPredicate]
    for rule in MagicSetTransformation(None,
                                       rules,
                                       goals,
                                       derivedPreds=derivedPredicate):
        PrepareHornClauseForRETE(rule)
        network.buildNetworkFromClause(rule)  
        PrettyPrintRule(rule)
    facts = Graph().parse(StringIO(FACTS),format='n3')
    network.feedFactsToAdd(generateTokenSet(facts))          
    print network.inferredFacts.serialize(format='turtle')
    print facts.serialize(format='turtle')
    
    # unittest.main() 