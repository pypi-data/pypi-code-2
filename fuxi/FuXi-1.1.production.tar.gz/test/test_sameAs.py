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
from FuXi.Rete.TopDown import PrepareSipCollection, SipStrategy
from FuXi.Rete.Magic import SetupDDLAndAdornProgram
from FuXi.Rete.SidewaysInformationPassing import SIPRepresentation

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

{ ?x owl:sameAs ?y } => { ?y owl:sameAs ?x } .
{ ?x owl:sameAs ?y . ?x ?p ?o } => { ?y ?p ?o } .
"""

GOALS = [
    (EX.foo,EX.y,Variable('o')),
]

class test_sameAs(unittest.TestCase):
    def setUp(self):
        self.rule_store, self.rule_graph, self.network = SetupRuleStore(makeNetwork=True)
        self.graph = Graph().parse(StringIO(FACTS), format='n3')
        adornedProgram = SetupDDLAndAdornProgram(
                                       self.graph,
                                       HornFromN3(StringIO(RULES)),
                                       GOALS,
                                       derivedPreds=[OWL_NS.sameAs])
        pprint(list(self.graph.adornedProgram))
    def testSmushing(self):
        sipCollection = PrepareSipCollection(self.graph.adornedProgram)
        print self.graph.serialize(format='n3')
        for arc in SIPRepresentation(sipCollection):
            print arc
        success = False
        for goal in GOALS:
            goalLiteral = BuildUnitermFromTuple(goal)
            print "Query / goal: ", goalLiteral
            for ans,node in SipStrategy(
                        goal,
                        sipCollection,
                        self.graph,
                        [OWL_NS.sameAs],
                        debug = False):
                if ans[Variable('o')] == Literal('yyyy'):
                    success = True
                    print "Found solution!", ans
                    break
        self.failUnless(success,"Unable to proove %s"%(repr((EX.foo,EX.y,Literal('yyyy')))))

if __name__ == '__main__':
	unittest.main()