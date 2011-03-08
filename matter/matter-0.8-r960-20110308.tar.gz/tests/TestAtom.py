



import sys,os
import unittest

sys.path.insert(0,os.path.abspath('..'))
print sys.path

from matter import Atom

class TestCase( unittest.TestCase ):
    

    def test_isotope_ctor(self):
        "Atom: isotope ctor"
        Fe57 = Atom( 'Fe', mass=57 )
        print "- Z=%s" % Fe57.Z
        print "- mass=%s" % Fe57.mass
        return
    
    def test_xyz(self):
        "Atom: xyz cartesian attribute"
        from matter import Lattice
        C = Atom( 'C', [0.1, 0.2, 0.3], lattice = Lattice(2,2,2,90,90,90))
        print "fractional pos=%s" % C.xyz
        print "cartesian pos=%s" % C.xyz_cartn
        return


    def test_undefined_state(self):
        "Atom: undefined state"
        Fe57 = Atom( 'Fe', mass=57 )
        self._assertRaises( AttributeError , "Fe57.velocity", locals() )
        return

    
    def test_setable_state(self):
        "Atom: setable state"
        Fe57 = Atom( 'Fe', mass=57 )
        v = (0,0,1)
        print '- Set velocity to %s ... ' % (v,), 
        Fe57.velocity = v
        print ' velocity = %s ' % (Fe57.velocity,)
        print "- velocity's documentation: %s " % Atom.velocity.doc
        return


#    def test_arbitrary_prop(self):
#        "Atom: set an arbitrary property"
#        Fe57 = Atom( 'Fe', mass=57 )
#        self._assertRaises(
#            AttributeError, "Fe57.some_very_very_strange_property = 'hello'",
#            locals() )
#        return


    def test_del_state(self):
        "Atom: delete state"
        Fe57 = Atom( 'Fe', mass=57 )
        Fe57.velocity = (0,0,1)
        del Fe57.velocity
        self._assertRaises( AttributeError, 'Fe57.velocity', locals())
        return


    def test_del_ctorarg(self):
        "Atom: delete ctor arg"
        Fe57 = Atom( 'Fe', mass=57 )
        self._assertRaises( AttributeError, "del Fe57.Z" , locals())
        return
        

    def test_str(self):
        "Atom: __str__"
        Fe57 = Atom( 'Fe', mass=57 )
        Fe57.velocity = (0,0,1)
        print Fe57
        return


    def test_natural_element(self):
        "Atom: natural element ctor"
        Fe = Atom( 'Fe' )
        print Fe
        return


    def _assertRaises(self, exceptionType, expression, locals):
        try:
            exec expression in locals
        except exceptionType:
            return
        
        raise AssertionError , "%s does not raise exception %s" % (
            expression, exceptionType)

    pass # end of TestCase


#def main():
#    testsuite = unittest.makeSuite( TestCase )
#    unittest.TextTestRunner(verbosity=2).run(testsuite)
#    return 

if __name__ == "__main__": 
    unittest.main()

