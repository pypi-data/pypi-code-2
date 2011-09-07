#!/usr/bin/env python
# encoding: utf-8
import unittest
from pprint import pprint
from rdflib import Variable, Namespace, Literal
from rdflib.Graph import Graph
from cStringIO import StringIO
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Syntax.InfixOWL import OWL_NS
from FuXi.Horn.HornRules import HornFromN3
from FuXi.Horn.PositiveConditions import BuildUnitermFromTuple
from FuXi.SPARQL.BackwardChainingStore import *

EX = Namespace('http://example.org/')

FACTS=\
"""
@prefix ex: <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#>.

ex:foo ex:x "xxxx";
       owl:sameAs ex:bar .
ex:bar ex:y "yyyy" .
"""

RULES=\
"""
@prefix owl: <http://www.w3.org/2002/07/owl#>.

{ ?x owl:sameAs ?y . ?x ?p ?o } => { ?y ?p ?o } .
"""

QUERY = "SELECT ?pred ?obj { ex:foo ?pred ?obj }"

FACTS2=\
"""
@prefix ex: <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#>.

ex:Socrates a ex:Man """

RULES2=\
"""
@prefix ex: <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#>.

{ ?x a ex:Man } => { ?x a ex:Mortal } .
"""

QUERY2 = "SELECT ?kind { ex:Socrates a ?kind }"

nsMap = {u'ex' :EX,
         u'owl': OWL_NS }

class test_sameAs(unittest.TestCase):
    def setUp(self):
        self.rule_store, self.rule_graph, self.network = SetupRuleStore(makeNetwork=True)
        self.graph = Graph().parse(StringIO(FACTS2), format='n3')
        self.rules=HornFromN3(StringIO(RULES2))
        
    # def testSmushing(self):
    #     factGraph = Graph().parse(StringIO(FACTS),format='n3')
    #     topDownStore=TopDownSPARQLEntailingStore(
    #                     factGraph.store,
    #                     factGraph,
    #                     idb=self.rules,
    #                     DEBUG=True,
    #                     # derivedPredicates=[],
    #                     nsBindings=nsMap,
    #                     decisionProcedure = BFP_METHOD,
    #                     identifyHybridPredicates = True)
    #     targetGraph = Graph(topDownStore)
    #     # self.failUnless((EX.foo,EX.y,Literal('yyyy')) in targetGraph.query(QUERY,initNs=nsMap))
    #     pprint(list(self.rules))
    #     for ans in targetGraph.query(QUERY,initNs=nsMap):
    #         print ans

    def testClassInstanceMembership(self):
        factGraph = self.graph
        topDownStore=TopDownSPARQLEntailingStore(
                        factGraph.store,
                        factGraph,
                        idb=self.rules,
                        DEBUG=True,
                        derivedPredicates=[EX.Mortal],
                        nsBindings=nsMap,
                        decisionProcedure = BFP_METHOD,
                        identifyHybridPredicates = False)
        targetGraph = Graph(topDownStore)
        # self.failUnless((EX.foo,EX.y,Literal('yyyy')) in targetGraph.query(QUERY,initNs=nsMap))
        pprint(list(self.rules))
        for ans in targetGraph.query(QUERY2,initNs=nsMap):
            print ans



if __name__ == '__main__':
	unittest.main()