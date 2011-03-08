##############################################################################
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""Unit tests for Structure class.
"""

__id__ = "$Id: TestStructure.py 2825 2009-03-09 04:33:12Z juhas $"

from numpy.ma.testutils import assert_almost_equal, assert_array_almost_equal
import os, sys
import unittest
import numpy

# useful variables
thisfile = locals().get('__file__', 'TestStructure.py')
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, 'testdata')

sys.path.insert(0,os.path.abspath('..'))# this should put the source code first on the path
from matter.Structure import Structure
from matter.Lattice import Lattice
from matter.Atom import Atom#, StructureFormatError

##############################################################################
class TestStructure(unittest.TestCase):
    """test methods of Structure class"""

    def setUp(self):
#        at1 = Atom('C', [0.333333333333333, 0.666666666666667, 0])
#        at2 = Atom('C', [0.666666666666667, 0.333333333333333, 0])
        at1 = Atom('C', [0, 0, 0])
        at2 = Atom('C', [1, 1, 1])
        self.stru = Structure( [ at1, at2], lattice=Lattice(1, 1, 1, 90, 90, 120) )
        
        ciffile = os.path.join(testdata_dir, 'PbTe.cif')
        self.stru2 = Structure()
        self.stru2.read(ciffile)
        
        ciffile = os.path.join(testdata_dir, 'graphite.cif')
        self.stru3 = Structure()
        self.stru3.read(ciffile)
        
        at1 = Atom('Al', [0.0, 0.0, 0.0])
        at2 = Atom('Al', [0.0, 0.5, 0.5])
        at3 = Atom('Al', [0.5, 0.0, 0.5])
        at4 = Atom('Al', [0.5, 0.5, 0.0])
        self.stru4 = Structure( [ at1, at2, at3, at4], 
                               lattice=Lattice(4.05, 4.05, 4.05, 90, 90, 90),
                               sgid = 225 )
        
        self.places = 12
        
    def assertListAlmostEqual(self, l1, l2, places=None):
        """wrapper for list comparison"""
        if places is None: places = self.places
        self.assertEqual(len(l1), len(l2))
        for i in range(len(l1)):
            self.assertAlmostEqual(l1[i], l2[i], places)


    def testChemicalFormulaPositionsSymbols(self):
        at1 = Atom('C', [0.333333333333333, 0.666666666666667, 0])
        at2 = Atom('C', [0.666666666666667, 0.333333333333333, 0])
        #at3 = Atom('H', [0, 0, 0])
        
        stru = Structure( [ at1, at2], lattice=Lattice(3.8, 3.8, 5.6, 90, 90, 120) )
        assert stru.getChemicalFormula()=='C_2'
        #self.assertListAlmostEqual(stru.xyz, [[0.33333333333333298, 0.66666666666666696, 0.0], [0.66666666666666696, 0.33333333333333298, 0.0]])
        #self.assertListAlmostEqual(stru.xyz_cartn,[[1.0969655114602876, 1.9000000000000017, 0.0], [2.1939310229205784, -2.0020877317117325e-15, 0.0]])
        #self.assertListAlmostEqual(stru.symbols, ['C', 'C'])
        #print "here's the lattice", stru.lattice.base
        return
    
    def test_writeStr(self):
        """check Structure.writeStr()"""
        print self.stru3.writeStr('xyz')
        return
    
    # FIXME move into TestAtom
    def test_cartesian(self):
        """check conversion to Cartesian coordinates"""
        from math import sqrt
        stru = self.stru
        s_rc0 = stru[0].xyz_cartn
        f_rc0 = 3*[0.0]
        s_rc1 = stru[1].xyz_cartn
        f_rc1 = [sqrt(0.75), 0.5, 1.]
        self.assertListAlmostEqual(s_rc0, f_rc0)
        self.assertListAlmostEqual(s_rc1, f_rc1)

#   def test___init__(self):
#       """check Structure.__init__()
#       """
#       return
#
#   def test___str__(self):
#       """check Structure.__str__()
#       """
#       return
#
#   def test_addNewAtom(self):
#       """check Structure.addNewAtom()
#       """
#       return
#
#   def test_getLastAtom(self):
#       """check Structure.getLastAtom()
#       """
#       return

#    def test_getAtom(self):
#        """check Structure.getAtom()
#        """
#        a0 = self.stru[0]
#        a1 = self.stru[1]
#        # check execeptions for invalid arguments
#        self.assertRaises(ValueError, self.stru.getAtom, 300)
#        self.assertRaises(ValueError, self.stru.getAtom, -44)
#        self.assertRaises(ValueError, self.stru.getAtom, "Na")
#        # check returned values
#        self.failUnless(a0 is self.stru.getAtom(0))
#        self.failUnless(a1 is self.stru.getAtom(1))
#        self.failUnless(a0 is self.stru.getAtom("C1"))
#        self.failUnless(a1 is self.stru.getAtom("C2"))
#        # check if labels get properly updated
#        cdsefile = os.path.join(testdata_dir, 'CdSe_bulk.stru')
#        cdse = Structure(filename=cdsefile)
#        self.stru[1:1] = cdse
#        self.failUnless(a0 is self.stru.getAtom("C1"))
#        self.failUnless(a1 is self.stru.getAtom("C2"))
#        self.failUnless(self.stru[1] is self.stru.getAtom("Cd1"))
#        return


    def test_getLabels(self):
        """check Structure.getLabels()
        """
        self.assertEqual(["C1", "C2"], self.stru.getLabels())
        pbtefile = os.path.join(testdata_dir, 'PbTe.cif')
        self.stru.read(pbtefile, format='cif')
        labels = self.stru.getLabels()
        #TODO need to fix these tests
        #self.assertEqual("Pb2+1", labels[0])
        #self.assertEqual("Pb2+4", labels[3])
        self.assertEqual("Te1", labels[4])
        self.assertEqual("Te4", labels[-1])
        return


    def test_distance(self):
        """check Structure.distance()
        """
        from math import sqrt
        self.assertRaises(ValueError, self.stru.distance, 333, "C1")
        self.assertRaises(ValueError, self.stru.distance, "C", "C1")
        self.assertAlmostEqual(sqrt(2.0),
                self.stru.distance(0, 1), self.places)
        self.assertAlmostEqual(sqrt(2.0),
                self.stru.distance("C1", "C2"), self.places)
        self.assertEqual(0, self.stru.distance(0, "C1"))
        return

#   def test_angle(self):
#       """check Structure.angle()
#       """
#       return

    def test_placeInLattice(self):
        """check Structure.placeInLattice() -- conversion of coordinates
        """
        stru = self.stru
        new_lattice = Lattice(.5, .5, .5, 90, 90, 60)
        stru.placeInLattice(new_lattice)
        a0 = stru[0]
        self.assertListAlmostEqual(a0.xyz, 3*[0.0])
        a1 = stru[1]
        self.assertListAlmostEqual(a1.xyz, [2.0, 0.0, 2.0])
        
    def test_forces(self):
        forces = [[0.0, 0.61, 0.7], [1.8, 0.9, 1.1]]
        self.stru.forces = forces
        self.assertListAlmostEqual(self.stru[0].force, forces[0])
        
    def test_spaceGroupQuery(self):

        sg = self.stru2.sg
        assert sg.number is 225
        assert sg.num_sym_equiv is 192
        assert sg.num_primitive_sym_equiv is 48
        assert sg.short_name=='Fm-3m'
        assert sg.alt_name=='F M 3 M'
        assert sg.point_group_name=='PGm3barm'
        assert sg.crystal_system=='CUBIC'
        assert sg.pdb_name=='F 4/m -3 2/m'
        assert_array_almost_equal(sg.symop_list[1].R, numpy.identity(3))
        assert_array_almost_equal(sg.symop_list[1].t, numpy.array([ 0. ,  0.5,  0.5]))
#        for symmop in sg.symop_list:
#            print symmop

    def test_symConsistent(self):
        
        result = self.stru2.symConsistent()
        assert result[0] is True
        
        self.stru3.sg = 225
        result,badAtomPos,badSymOp = self.stru3.symConsistent()
        assert result is False
        #print badAtomPos,badSymOp
        
    def test_PrimCellFind(self):
        ""
        #print 'PbTe 225'
        #print self.stru2.primitive_unitcell
        #print 'graphite'
        #print self.stru3.primitive_unitcell
        #print
        
    def test_bravais_crystalsystem_centering(self):
        
        assert self.stru2.centering is 'F'
        assert self.stru2.centering_description=='face centered'
        assert self.stru2.crystal_system is 'CUBIC'
        assert self.stru2.bravais_type=='face centered cubic'

    def test_species(self):
        ""
        #print self.stru2.getChemicalFormula()
        #print
        #print self.stru3.getChemicalFormula()
        #print
 
#    not fully functional
#    def test_distanceCalc(self):
#        print self.stru.computeDistances()


#   def test_read(self):
#       """check Structure.read()
#       """
#       return
#
#   def test_readStr(self):
#       """check Structure.readStr()
#       """
#       return
#
#   def test_write(self):
#       """check Structure.write()
#       """
#       return
#
#
#   def test_append(self):
#       """check Structure.append()
#       """
#       return
#
#   def test_insert(self):
#       """check Structure.insert()
#       """
#       return
#
#   def test_extend(self):
#       """check Structure.extend()
#       """
#       return
#
#   def test___setitem__(self):
#       """check Structure.__setitem__()
#       """
#       return
#
#   def test___setslice__(self):
#       """check Structure.__setslice__()
#       """
#       return
#
#   def test__get_lattice(self):
#       """check Structure._get_lattice()
#       """
#       return
#
#   def test__set_lattice(self):
#       """check Structure._set_lattice()
#       """
#       return
#
#   def test__update_labels(self):
#       """check Structure._update_labels()
#       """
#       return
#
#   def test__uncache(self):
#       """check Structure._uncache()
#       """
#       return

# End of class TestStructure

if __name__ == '__main__':
    unittest.main()

# End of file
