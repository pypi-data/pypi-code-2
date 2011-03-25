from itaps import iBase, iGeom
from .. import testhelper as unittest

class TestAdj(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

        self.volume = self.geom.createBrick(2, 2, 2)
        self.faces  = self.geom.getEntities(iBase.Type.face)
        self.edges  = self.geom.getEntities(iBase.Type.edge)
        self.verts  = self.geom.getEntities(iBase.Type.vertex)

    def tearDown(self):
        self.geom.deleteAll()

    def testAdj(self):
        adj = self.geom.getEntAdj(self.volume, iBase.Type.face)
        self.assert_((adj == self.faces).all())

        adj = self.geom.getEntAdj(self.faces, iBase.Type.edge)

        self.assertEqual(len(adj), len(self.faces))
        for i in range( len(adj) ):
            self.assertEqual(adj.length(i), 4)
            curr = adj[i]
            for j in curr:
                self.assert_(j in self.edges)

            for j in range(adj.length(i)):
                self.assert_(adj[i,j] in self.edges)

        self.assertRaises(IndexError, adj.__getitem__, (0,4))

    def test2ndAdj(self):
        adj = self.geom.getEnt2ndAdj(self.volume, iBase.Type.face,
                                     iBase.Type.edge)
        self.assertEqual(len(adj), len(self.edges))
        for i in adj:
            self.assert_(i in self.edges)

        adj = self.geom.getEnt2ndAdj(self.faces, iBase.Type.edge,
                                     iBase.Type.vertex)

        self.assertEqual(len(adj), len(self.faces))
        for i in range( len(adj) ):
            self.assertEqual(adj.length(i), 4)
            curr = adj[i]
            for j in curr:
                self.assert_(j in self.verts)

            for j in range(adj.length(i)):
                self.assert_(adj[i,j] in self.verts)

        self.assertRaises(IndexError, adj.__getitem__, (0,4))

    def testIsAdj(self):
        self.assert_(self.geom.isEntAdj(self.volume, self.faces[0]))
        self.assert_(self.geom.isEntAdj([self.volume], self.faces[0:1]).all())
        self.assert_(self.geom.isEntAdj(self.volume, self.faces).all())
        self.assert_(self.geom.isEntAdj(self.faces, self.volume).all())
        self.assert_(self.geom.isEntAdj([self.volume]*6, self.faces).all())
