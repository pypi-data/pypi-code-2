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

EX   = Namespace('http://example.org/')
LIST = Namespace('http://www.w3.org/2000/10/swap/list#')

FACTS=\
"""
@prefix ex: <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#>.
@prefix list: <http://www.w3.org/2000/10/swap/list#>.

( ex:Fred ex:Wilma ex:Barney ) .
( ex:Carl ) .
list:follows a owl:TransitiveProperty .

"""

RULES=\
"""
@prefix owl: <http://www.w3.org/2002/07/owl#>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix list: <http://www.w3.org/2000/10/swap/list#>.
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
@prefix : <http://www.w3.org/2000/10/swap/list#>.

{ ?L rdf:first ?I }          => { ?I in ?L }.
{ ?L rdf:rest ?R. ?I in ?R } => { ?I in ?L }.
{ ?M1 in ?L1 .
  ?M2 in ?L2 .
  ?L1 rdf:rest ?L2 .
  ?M2 log:notEqualTo rdf:nil, ?M1 }         => { ?M2 follows ?M1 }. """

QUERY  = "SELECT ?M1 ?M2 { ?M1 list:follows ?M2 }"
QUERY2 = "SELECT ?M1 ?M2 { ?M1 list:follows ex:Fred }"

nsMap = {u'ex'   : EX,
         u'list' : LIST,
         u'owl'  : OWL_NS }

class testOpenQuery(unittest.TestCase):
    def setUp(self):
        self.rule_store, self.rule_graph, self.network = SetupRuleStore(makeNetwork=True)
        self.graph = Graph().parse(StringIO(FACTS), format='n3')
        self.rules=list(HornFromN3(StringIO(RULES)))

        self.rules.extend(self.network.setupDescriptionLogicProgramming(
                                                     self.graph,
                                                     addPDSemantics=False,
                                                     constructNetwork=False))
    def testClassInstanceMembership(self):
        factGraph = self.graph
        topDownStore=TopDownSPARQLEntailingStore(
                        factGraph.store,
                        factGraph,
                        idb=self.rules,
                        DEBUG=True,
                        derivedPredicates=[ LIST['in'], LIST.follows ],
                        nsBindings=nsMap,
                        decisionProcedure = BFP_METHOD)
        targetGraph = Graph(topDownStore)
        # self.failUnless((EX.foo,EX.y,Literal('yyyy')) in targetGraph.query(QUERY,initNs=nsMap))
        pprint(list(self.rules))
        for ans in targetGraph.query(QUERY,initNs=nsMap):
            print ans

if __name__ == '__main__':
	unittest.main()