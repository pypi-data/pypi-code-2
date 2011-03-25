from itaps import iBase, iMesh, iGeom, iRel
from .. import testhelper as unittest
import numpy

class TestRelation(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.geom = iGeom.Geom()
        self.rel  = iRel.Rel()

    def tearDown(self):
        self.geom.deleteAll()

    def testEntEntRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        mesh_ent = self.mesh.createVtx([0, 0, 0])
        geom_ent = self.geom.createBrick(2, 2, 2)
        pair.setRelation(mesh_ent, geom_ent)

        self.assertEqual(pair.getEntRelation(first=mesh_ent),  geom_ent)
        self.assertEqual(pair.getEntRelation(mesh_ent, False), geom_ent)
        self.assertEqual(pair.getEntRelation(second=geom_ent), mesh_ent)
        self.assertEqual(pair.getEntRelation(geom_ent, True),  mesh_ent)

    def testEntEntArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        mesh_ent = self.mesh.createVtx([0, 0, 0])
        self.geom.createBrick(2, 2, 2)
        geom_ents = self.geom.getEntities(iBase.Type.vertex)
        pair.setRelation(mesh_ent, geom_ents)

        assoc = pair.getEntArrRelation(first=mesh_ent)
        # TODO: finish this test

    def testEntArrEntRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        mesh_ents = self.mesh.createVtx([[0, 0, 0]]*8)
        geom_ent = self.geom.createBrick(2, 2, 2)
        pair.setRelation(mesh_ents, geom_ent)
        # TODO: finish this test

    def testEntArrEntArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        mesh_ents = self.mesh.createVtx([[0, 0, 0]]*8)
        self.geom.createBrick(2, 2, 2)
        geom_ents = self.geom.getEntities(iBase.Type.vertex)
        pair.setRelation(mesh_ents, geom_ents)

        assoc = pair.getEntRelation(first=mesh_ents)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == geom_ents).all())

        assoc = pair.getEntRelation(mesh_ents, False)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == geom_ents).all())

        assoc = pair.getEntRelation(second=geom_ents)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == mesh_ents).all())

        assoc = pair.getEntRelation(geom_ents, True)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == mesh_ents).all())

    def testEntSetRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.set)

        mesh_ent = self.mesh.createVtx([0, 0, 0])
        geom_set = self.geom.createEntSet(False)
        pair.setRelation(mesh_ent, geom_set)

        self.assertEqual(pair.getSetRelation(first=mesh_ent),  geom_set)
        self.assertEqual(pair.getSetRelation(mesh_ent, False), geom_set)
        self.assertEqual(pair.getEntRelation(second=geom_set), mesh_ent)
        self.assertEqual(pair.getEntRelation(geom_set, True),  mesh_ent)

    def testEntSetArrRel(self):
        pass

    def testEntArrSetRel(self):
        pass

    def testEntArrSetArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.set)

        mesh_ents = self.mesh.createVtx([[0, 0, 0]]*3)
        geom_sets = iBase.Array([ self.geom.createEntSet(False),
                                  self.geom.createEntSet(False),
                                  self.geom.createEntSet(False) ])
        pair.setRelation(mesh_ents, geom_sets)

        assoc = pair.getSetRelation(first=mesh_ents)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrRelation(first=mesh_ents)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getSetRelation(mesh_ents, False)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrRelation(mesh_ents, False)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getEntRelation(second=geom_sets)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == mesh_ents).all())
        assoc = pair.getEntArrRelation(second=geom_sets)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == mesh_ents).all())

        assoc = pair.getEntRelation(geom_sets, True)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == mesh_ents).all())
        assoc = pair.getEntArrRelation(geom_sets, True)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.data == mesh_ents).all())

    def testSetEntRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.entity)

        mesh_set = self.mesh.createEntSet(False)
        geom_ent = self.geom.createBrick(2, 2, 2)
        pair.setRelation(mesh_set, geom_ent)

        self.assertEqual(pair.getEntRelation(first=mesh_set),  geom_ent)
        self.assertEqual(pair.getEntRelation(mesh_set, False), geom_ent)
        self.assertEqual(pair.getSetRelation(second=geom_ent), mesh_set)
        self.assertEqual(pair.getSetRelation(geom_ent, True),  mesh_set)

    def testSetEntArrRel(self):
        pass

    def testSetArrEntRel(self):
        pass

    def testSetArrEntArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.entity)

        mesh_sets = iBase.Array([ self.mesh.createEntSet(False),
                                  self.mesh.createEntSet(False),
                                  self.mesh.createEntSet(False) ])
        self.geom.createBrick(2, 2, 2)
        geom_ents = self.geom.getEntities(iBase.Type.vertex)[0:3]
        pair.setRelation(mesh_sets, geom_ents)

        assoc = pair.getEntRelation(first=mesh_sets)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.data == geom_ents).all())
        assoc = pair.getEntArrRelation(first=mesh_sets)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.data == geom_ents).all())

        assoc = pair.getEntRelation(mesh_sets, False)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.data == geom_ents).all())
        assoc = pair.getEntArrRelation(mesh_sets, False)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.data == geom_ents).all())

        assoc = pair.getSetRelation(second=geom_ents)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrRelation(second=geom_ents)
        self.assert_((assoc == mesh_sets).all())

        assoc = pair.getSetRelation(geom_ents, True)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrRelation(geom_ents, True)
        self.assert_((assoc == mesh_sets).all())

    def testSetSetRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.set)

        mesh_set = self.mesh.createEntSet(False)
        geom_set = self.geom.createEntSet(False)
        pair.setRelation(mesh_set, geom_set)

        self.assertEqual(pair.getSetRelation(first=mesh_set),  geom_set)
        self.assertEqual(pair.getSetRelation(mesh_set, False), geom_set)
        self.assertEqual(pair.getSetRelation(second=geom_set), mesh_set)
        self.assertEqual(pair.getSetRelation(geom_set, True),  mesh_set)

    def testSetSetArrRel(self):
        pass

    def testSetArrSetRel(self):
        pass

    def testSetArrSetArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.set)

        mesh_sets = iBase.Array([ self.mesh.createEntSet(False),
                                  self.mesh.createEntSet(False),
                                  self.mesh.createEntSet(False) ])
        geom_sets = iBase.Array([ self.geom.createEntSet(False),
                                  self.geom.createEntSet(False),
                                  self.geom.createEntSet(False) ])
        pair.setRelation(mesh_sets, geom_sets)

        assoc = pair.getSetRelation(first=mesh_sets)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrRelation(first=mesh_sets)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getSetRelation(mesh_sets, False)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrRelation(mesh_sets, False)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getSetRelation(second=geom_sets)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrRelation(second=geom_sets)
        self.assert_((assoc == mesh_sets).all())

        assoc = pair.getSetRelation(geom_sets, True)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrRelation(geom_sets, True)
        self.assert_((assoc == mesh_sets).all())

    def testInfer(self):
        pass

    def testInferAll(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        self.geom.createBrick(2, 2, 2)
        geom_verts = self.geom.getEntities(iBase.Type.vertex)
        coords = self.geom.getVtxCoords(geom_verts)
        mesh_verts = self.mesh.createVtx(coords)

        pair.inferAllRelations()
