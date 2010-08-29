#!/usr/bin/env python
"""Original NetworkX graph tests"""
import copy
from nose.tools import *
import networkx
import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti

from historical_tests import HistoricalTests

class TestDiGraphHistorical(HistoricalTests):

    def setUp(self):
        HistoricalTests.setUp(self)
        self.G=nx.DiGraph


    def test_in_degree(self):
        G=self.G()
        G.add_nodes_from('GJK')
        G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), 
                          ('B', 'C'), ('C', 'D')])

        assert_equal(sorted(G.in_degree().values()),[0, 0, 0, 0, 1, 2, 2])
        assert_equal(G.in_degree(),
                     {'A': 0, 'C': 2, 'B': 1, 'D': 2, 'G': 0, 'K': 0, 'J': 0})
        assert_equal(sorted([v for k,v in G.in_degree_iter()]),
                     [0, 0, 0, 0, 1, 2, 2])
        assert_equal(dict(G.in_degree_iter()),
                    {'A': 0, 'C': 2, 'B': 1, 'D': 2, 'G': 0, 'K': 0, 'J': 0})


    def test_out_degree(self):
        G=self.G()
        G.add_nodes_from('GJK')
        G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), 
                          ('B', 'C'), ('C', 'D')])
        assert_equal(sorted(G.out_degree().values()),[0, 0, 0, 0, 1, 2, 2])
        assert_equal(G.out_degree(),
                     {'A': 2, 'C': 1, 'B': 2, 'D': 0, 'G': 0, 'K': 0, 'J': 0})
        assert_equal(sorted([v for k,v in G.in_degree_iter()]),
                     [0, 0, 0, 0, 1, 2, 2])
        assert_equal(dict(G.out_degree_iter()),
             {'A': 2, 'C': 1, 'B': 2, 'D': 0, 'G': 0, 'K': 0, 'J': 0})


    def test_degree_digraph(self):
        H=nx.DiGraph()
        H.add_edges_from([(1,24),(1,2)])
        assert_equal(sorted(H.in_degree([1,24]).values()),[0, 1])
        assert_equal(sorted(H.out_degree([1,24]).values()),[0, 2])
        assert_equal(sorted(H.degree([1,24]).values()),[1, 2])


    def test_neighbors(self):
        G=self.G()
        G.add_nodes_from('GJK')
        G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), 
                          ('B', 'C'), ('C', 'D')])

        assert_equal(sorted(G.neighbors('C')),['D'])
        assert_equal(sorted(G['C']),['D'])
        assert_equal(sorted(G.neighbors('A')),['B', 'C'])
        assert_equal(sorted(G.neighbors_iter('A')),['B', 'C'])
        assert_equal(sorted(G.neighbors_iter('C')),['D'])
        assert_equal(sorted(G.neighbors('A')),['B', 'C'])
        assert_raises(nx.NetworkXError,G.neighbors,'j')
        assert_raises(nx.NetworkXError,G.neighbors_iter,'j')

    def test_successors(self):
        G=self.G()
        G.add_nodes_from('GJK')
        G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), 
                          ('B', 'C'), ('C', 'D')])
        assert_equal(sorted(G.successors('A')),['B', 'C'])
        assert_equal(sorted(G.successors_iter('A')),['B', 'C'])
        assert_equal(sorted(G.successors('G')),[])
        assert_equal(sorted(G.successors('D')),[])
        assert_equal(sorted(G.successors_iter('G')),[])
        assert_raises(nx.NetworkXError,G.successors,'j')
        assert_raises(nx.NetworkXError,G.successors_iter,'j')
        

    def test_predecessors(self):
        G=self.G()
        G.add_nodes_from('GJK')
        G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), 
                          ('B', 'C'), ('C', 'D')])
        assert_equal(sorted(G.predecessors('C')),['A', 'B'])
        assert_equal(sorted(G.predecessors_iter('C')),['A', 'B'])
        assert_equal(sorted(G.predecessors('G')),[])
        assert_equal(sorted(G.predecessors('A')),[])
        assert_equal(sorted(G.predecessors_iter('G')),[])
        assert_equal(sorted(G.predecessors_iter('A')),[])
        assert_equal(sorted(G.successors_iter('D')),[])

        assert_raises(nx.NetworkXError,G.predecessors,'j')
        assert_raises(nx.NetworkXError,G.predecessors,'j')



    def test_reverse(self):
        G=nx.complete_graph(10)
        H=G.to_directed()
        HR=H.reverse()
        assert_true(nx.is_isomorphic(H,HR))
        assert_equal(sorted(H.edges()),sorted(HR.edges()))

    def test_reverse2(self):
        H=nx.DiGraph()
        foo=[H.add_edge(u,u+1) for u in range(0,5)]
        HR=H.reverse()
        for u in range(0,5):
            assert_true(HR.has_edge(u+1,u))

    def test_reverse3(self):
        H=nx.DiGraph()
        H.add_nodes_from([1,2,3,4])
        HR=H.reverse()
        assert_equal(sorted(HR.nodes()),[1, 2, 3, 4])

