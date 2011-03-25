from itaps import iBase, iGeom
from .. import testhelper as unittest
import numpy
import tempfile

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

    def tearDown(self):
        self.geom.deleteAll()

    def testMinimal(self):
        root = self.geom.rootSet

        self.assertEqual(len(self.geom.tolerance), 2)
        self.assertEqual(self.geom.boundBox.shape, (2,3))
        self.assert_(isinstance(self.geom.parametric, bool))
        self.assert_(isinstance(self.geom.topoLevel, int))

        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 0)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 0)

    def testType(self):
        self.geom.createSphere(1)

        faces = self.geom.getEntities(iBase.Type.face)
        self.assertEqual(self.geom.getEntType(faces[0]), iBase.Type.face)
        self.assert_((self.geom.getEntType(faces) == [iBase.Type.face]*12).
                     all())
        self.geom.getFaceType(faces[0])

    def testMeasure(self):
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.all)
        self.assert_((self.geom.measure(ents) == [1]*(1+6+12+8)).all())

    def testParametric(self):
        self.geom.createBrick(1, 1, 1)
        faces = self.geom.getEntities(iBase.Type.face)
        verts = self.geom.getEntities(iBase.Type.vertex)

        self.assertEqual(self.geom.isEntParametric(faces[0]), True)
        self.assert_((self.geom.isEntParametric(faces) == [True]*6).all())
        self.assertEqual(self.geom.isEntParametric(verts[0]), False)
        self.assert_((self.geom.isEntParametric(verts) == [False]*8).all())

    def testPeriodic(self):
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.face)

        self.assert_((self.geom.isEntPeriodic(ents[0]) == [False]*2).all())
        self.assert_((self.geom.isEntPeriodic(ents)    == [[False]*2]*6).all())

    def testTolerance(self):
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.all)

        self.assert_(isinstance(self.geom.getEntTolerance(ents[0]), float))
        self.assertEqual(self.geom.getEntTolerance(ents).dtype, numpy.double)

    def testSave(self):
        self.geom.createBrick(1, 1, 1)
        file = tempfile.NamedTemporaryFile(suffix=".sat")

        self.geom.save(file.name)
        self.geom.deleteAll()
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 0)
        
        self.geom.load(file.name)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 1)
