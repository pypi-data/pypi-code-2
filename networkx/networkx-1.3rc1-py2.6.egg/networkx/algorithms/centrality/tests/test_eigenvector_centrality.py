#!/usr/bin/env python
import math
from nose import SkipTest
from nose.tools import *
import networkx

class TestEigenvectorCentrality(object):
    @classmethod
    def setupClass(cls):
        global np
        try:
            import numpy as np
        except ImportError:
            raise SkipTest('NumPy not available.')
        
    def test_K5(self):
        """Eigenvector centrality: K5"""
        G=networkx.complete_graph(5)
        b=networkx.eigenvector_centrality(G)
        v=math.sqrt(1/5.0)
        b_answer=dict.fromkeys(G,v)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        b=networkx.eigenvector_centrality_numpy(G)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n],places=3)

    def test_P3(self):
        """Eigenvector centrality: P3"""
        G=networkx.path_graph(3)
        b_answer={0: 0.5, 1: 0.7071, 2: 0.5}
        b=networkx.eigenvector_centrality_numpy(G)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n],places=4)


class TestEigenvectorCentralityDirected(object):
    @classmethod
    def setupClass(cls):
        global np
        try:
            import numpy as np
        except ImportError:
            raise SkipTest('NumPy not available.')

    def setUp(self):
    
        G=networkx.DiGraph()

        edges=[(1,2),(1,3),(2,4),(3,2),(3,5),(4,2),(4,5),(4,6),\
               (5,6),(5,7),(5,8),(6,8),(7,1),(7,5),\
               (7,8),(8,6),(8,7)]

        G.add_edges_from(edges,weight=2.0)
        self.G=G
        self.G.evc=[0.25368793,  0.19576478,  0.32817092,  0.40430835,  
                    0.48199885, 0.15724483,  0.51346196,  0.32475403]

        H=networkx.DiGraph()

        edges=[(1,2),(1,3),(2,4),(3,2),(3,5),(4,2),(4,5),(4,6),\
               (5,6),(5,7),(5,8),(6,8),(7,1),(7,5),\
               (7,8),(8,6),(8,7)]

        G.add_edges_from(edges)
        self.H=G
        self.H.evc=[0.25368793,  0.19576478,  0.32817092,  0.40430835,  
                    0.48199885, 0.15724483,  0.51346196,  0.32475403]



    def test_eigenvector_centrality_weighted(self):
        G=self.G
        p=networkx.eigenvector_centrality_numpy(G)
        for (a,b) in zip(list(p.values()),self.G.evc):
            assert_almost_equal(a,b)

    def test_eigenvector_centrality_unweighted(self):
        G=self.H
        p=networkx.eigenvector_centrality_numpy(G)
        for (a,b) in zip(list(p.values()),self.G.evc):
            assert_almost_equal(a,b)
