#
# Unit Tests for Param() Objects
#
# PyomoModel                Base test class
# SimpleParam                Test singleton parameter
# ArrayParam1                Test arrays of parameters
# ArrayParam2                Test arrays of parameter with explicit zero default
# ArrayParam3                Test arrays of parameter with nonzero default
# TestIO                Test initialization from an AMPL *.dat file
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
from coopr.pyomo import *

class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = Model()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class SimpleParam(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.A = Param(initialize=3.3)
        self.instance = self.model.create()

    def tearDown(self):
        if os.path.exists("param.dat"):
           os.remove("param.dat")

    def test_simplify(self):
        """Check the parameter can be simplified"""
        tmp = self.instance.A.simplify(self.instance)
        self.failUnlessEqual( isinstance(tmp,NumericConstant), True)
        self.failUnlessEqual( tmp.value, 3.3 )

    def test_value(self):
        """Check the value of the parameter"""
        tmp = value(self.instance.A)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = float(self.instance.A)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = int(self.instance.A)
        self.failUnlessEqual( type(tmp), int)
        self.failUnlessEqual( tmp, 3 )

    def test_getattr(self):
        """Check the use of the __getattr__ method"""
        self.failUnlessEqual( self.instance.A.value, 3.3)

    def test_setattr_value(self):
        """Check the use of the __setattr__ method"""
        self.instance.A = 3.3
        self.failUnlessEqual( self.instance.A.value, 3.3)
        self.instance.A.value = 4.3
        self.failUnlessEqual( self.instance.A.value, 4.3)
        try:
          self.instance.A.value = 'A'
        except ValueError:
          self.fail("fail test_setattr_value")
        else:
          #
          # NOTE: we can set bad values into a NumericValue object
          #
          pass

    def test_setattr_default(self):
        """Check the use of the __setattr__ method"""
        self.model.A = Param()
        self.model.A.default = 4.3
        self.instance = self.model.create()
        self.failUnlessEqual( self.instance.A.value, 4.3)

    def test_dim(self):
        """Check the use of dim"""
        self.failUnlessEqual( self.instance.A.dim(), 0)

    def test_keys(self):
        """Check the use of keys"""
        self.failUnlessEqual( len(self.instance.A.keys()), 1)

    def test_len(self):
        """Check the use of len"""
        self.failUnlessEqual( len(self.instance.A), 1)

    def test_getitem(self):
        """Check the use of getitem"""
        import coopr.pyomo.base.param
        self.failUnless(isinstance(self.instance.A[None], coopr.pyomo.base.param._ParamValue))
        self.failUnlessEqual( self.instance.A[None], 3.3)

    def test_check_values(self):
        """Check the use of check_values"""
        self.instance.A.check_values()


class ArrayParam1(SimpleParam):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3})
        self.instance = self.model.create()

    def test_simplify(self):
        """Check the parameter can be simplified"""
        try:
          tmp = self.instance.A.simplify(self.instance)
        except ValueError:
          pass
        else:
          self.fail("test_simplify")

    def test_value(self):
        try:
          tmp = value(self.instance.A)
        except ValueError:
          pass
        else:
          self.fail("test_value")
        try:
          tmp = float(self.instance.A)
        except ValueError:
          pass
        else:
          self.fail("test_value")
        try:
          tmp = int(self.instance.A)
        except ValueError:
          pass
        else:
          self.fail("test_value")
        tmp = value(self.instance.A[1])
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 1.3 )
        tmp = float(self.instance.A[1])
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 1.3 )
        tmp = int(self.instance.A[1])
        self.failUnlessEqual( type(tmp), int)
        self.failUnlessEqual( tmp, 1 )

    def test_call(self):
        """Check the use of the __call__ method"""
        try:
          tmp = self.instance.A()
        except TypeError:
          pass
        else:
          self.fail("test_call")

    def test_getattr(self):
        """Check the use of the __getattr__ method"""
        try:
          tmp = self.instance.A.value
        except AttributeError:
          pass
        else:
          self.fail("test_call")

    def test_setattr_value(self):
        """Check the use of the __setattr__ method"""
        import coopr.pyomo.base.param
        self.instance.A.value = 4.3
        self.instance.A = 4.3
        if self.instance.A.mutable:
            self.instance.A[1].value = 4.3
            self.failUnlessEqual( type(self.instance.A[1]), coopr.pyomo.base.param._ParamValue)
        self.instance.A[1] = 4.3
        if self.instance.A.mutable:
            self.failUnlessEqual( type(self.instance.A[1]), coopr.pyomo.base.param._ParamValue)
        else:
            self.failUnlessEqual( type(self.instance.A[1]), float)


    def test_setitem(self):
        """Check the use of the __setattr__ method"""
        self.instance.A[3] = 4.3
        self.failUnlessEqual( self.instance.A[3], 4.3)
        self.instance.A[1] = 4.3
        self.failUnlessEqual( self.instance.A[1], 4.3)
        try:
          self.instance.A[3] = 'A'
        except ValueError:
          self.fail("fail test_setitem")

    def test_keys(self):
        """Check the use of keys"""
        self.failUnlessEqual( len(self.instance.A.keys()), 1)

    def test_dim(self):
        """Check the use of dim"""
        self.failUnlessEqual( self.instance.A.dim(), 1)

    def test_len(self):
        """Check the use of len"""
        self.instance.A[3] = 4.3
        self.failUnlessEqual( len(self.instance.A), 2)

    def test_getitem(self):
        """Check the use of getitem"""
        import coopr.pyomo.base.param
        try:
          self.failUnlessEqual( self.instance.A[None], 1.3)
        except KeyError:
          pass
        else:
          self.fail("test_getitem")
        if self.instance.A.mutable:
            self.failUnlessEqual(type(self.instance.A[1]), coopr.pyomo.base.param._ParamValue)
        else:
            self.failUnlessEqual(type(self.instance.A[1]), float)
        self.failUnlessEqual( self.instance.A[1], 1.3)
        try:
          self.failUnlessEqual( self.instance.A[3], 0)
        except KeyError:
          pass
        else:
          self.fail("test_getitem")


class ArrayParam2(ArrayParam1):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3}, default=0.0)
        self.instance = self.model.create()

    def test_setattr_default(self):
        """Check the use of the __setattr__ method"""
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z)
        self.model.A.default = 4.3
        self.instance = self.model.create()
        self.failUnlessEqual( self.instance.A[3], 4.3)

    def test_keys(self):
        """Check the use of keys"""
        self.failUnlessEqual( len(self.instance.A.keys()), 2)

    def test_len(self):
        """Check the use of len"""
        self.failUnlessEqual( len(self.instance.A), 2)

    def test_getitem(self):
        """Check the use of getitem"""
        try:
          self.failUnlessEqual( self.instance.A[None], 0.0)
        except KeyError:
          pass
        else:
          self.fail("test_getitem")
        self.failUnlessEqual( self.instance.A[1], 1.3)
        self.failUnlessEqual( self.instance.A[3], 0)


class ArrayParam3(ArrayParam2):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3},default=99.0)
        self.instance = self.model.create()

    def test_len(self):
        """Check the use of len"""
        self.failUnlessEqual( len(self.instance.A), 2)

    def test_getitem(self):
        """Check the use of getitem"""
        try:
          self.failUnlessEqual( self.instance.A[None], 0.0)
        except AssertionError:
          print self.instance.A._paramval
        except KeyError:
          pass
        else:
          self.fail("test_getitem")
        self.failUnlessEqual( self.instance.A[1], 1.3)
        self.failUnlessEqual( self.instance.A[3], 99.0)


class ArrayParam4(ArrayParam3):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize=1.3)
        self.instance = self.model.create()

    def test_len(self):
        """Check the use of len"""
        self.failUnlessEqual( len(self.instance.A), 2)

    def test_getitem(self):
        """Check the use of getitem"""
        try:
          self.failUnlessEqual( self.instance.A[None], 0.0)
        except KeyError:
          pass
        else:
          self.fail("test_getitem")
        self.failUnlessEqual( self.instance.A[1], 1.3)
        self.failUnlessEqual( self.instance.A[3], 1.3)


class ArrayParam5(ArrayParam4):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        def A_init(i,model):
          return 1.3
        self.model.A = Param(self.model.Z, initialize=A_init)
        self.instance = self.model.create()


class ArrayParam6(PyomoModel):

    def test_index1(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            for i in model.A:
                if i%2 == 0:
                    yield i
        def B_init(i,j,model):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init)
        self.instance = self.model.create()
        #self.instance.pprint()
        self.failUnlessEqual(set(self.instance.B.keys()),set([(0,True),(2,True),(0,   False),(2,False)]))
        self.failUnlessEqual(self.instance.B[0,True],2)
        self.failUnlessEqual(self.instance.B[0,False],-2)
        self.failUnlessEqual(self.instance.B[2,True],4)
        self.failUnlessEqual(self.instance.B[2,False],-4)

    def test_index2(self):
        self.model.A = Set(initialize=range(0,4))
        @set_options(dimen=3)
        def B_index(model):
            return [(i,2*i,i*i) for i in model.A if i%2 == 0]
        def B_init(i,ii,iii,j,model):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init)
        self.instance = self.model.create()
        #self.instance.pprint()
        self.failUnlessEqual(set(self.instance.B.keys()),set([(0,0,0,True),(2,4,4,True),(0,0,0,False),(2,4,4,False)]))
        self.failUnlessEqual(self.instance.B[0,0,0,True],2)
        self.failUnlessEqual(self.instance.B[0,0,0,False],-2)
        self.failUnlessEqual(self.instance.B[2,4,4,True],4)
        self.failUnlessEqual(self.instance.B[2,4,4,False],-4)

    def test_index3(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            return [(i,2*i,i*i) for i in model.A if i%2 == 0]
        def B_init(i,ii,iii,j,model):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init)
        try:
            self.instance = self.model.create()
            self.fail("Expected ValueError because B_index returns a tuple")
        except ValueError:
            pass

    def test_index4(self):
        self.model.A = Set(initialize=range(0,4))
        @set_options(within=Integers)
        def B_index(model):
            return [i/2.0 for i in model.A]
        def B_init(i,j,model):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init)
        try:
            self.instance = self.model.create()
            self.fail("Expected ValueError because B_index returns invalid index values")
        except ValueError:
            pass

    def test_dimen1(self):
        model=Model()
        model.A = Set(dimen=2, initialize=[(1,2),(3,4)])
        model.B = Set(dimen=3, initialize=[(1,1,1),(2,2,2),(3,3,3)])
        model.C = Set(dimen=1, initialize=[9,8,7,6,5])
        model.x = Param(model.A, model.B, model.C, initialize=-1)
        model.y = Param(model.B, initialize=(1,1))
        instance=model.create()
        self.failUnlessEqual( instance.x.dim(), 6)
        self.failUnlessEqual( instance.y.dim(), 3)


class TestIO(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        if os.path.exists("param.dat"):
           os.remove("param.dat")

    def test_io1(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param A := 3.3;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Param()
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( self.instance.A, 3.3 )

    def test_io2(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := 1 3 5;"
        print >>OUTPUT, "param A :="
        print >>OUTPUT, "1 2.2"
        print >>OUTPUT, "3 2.3"
        print >>OUTPUT, "5 2.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.A=Param(self.model.Z)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( len(self.instance.A), 3 )

    def test_io3(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := 1 3 5;"
        print >>OUTPUT, "param : A B :="
        print >>OUTPUT, "1 2.2 3.3"
        print >>OUTPUT, "3 2.3 3.4"
        print >>OUTPUT, "5 2.5 3.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.A=Param(self.model.Z)
        self.model.B=Param(self.model.Z)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( len(self.instance.A), 3 )
        self.failUnlessEqual( len(self.instance.B), 3 )
        self.failUnlessEqual( self.instance.B[5], 3.5 )

    def test_io4(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := A1 A2 A3;"
        print >>OUTPUT, "set Y := 1 2 3;"
        print >>OUTPUT, "param A: A1 A2 A3 :="
        print >>OUTPUT, "1 1.3 2.3 3.3"
        print >>OUTPUT, "2 1.4 2.4 3.4"
        print >>OUTPUT, "3 1.5 2.5 3.5"
        print >>OUTPUT, ";"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.Y=Set()
        self.model.A=Param(self.model.Y,self.model.Z)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( len(self.instance.Y), 3 )
        self.failUnlessEqual( len(self.instance.Z), 3 )
        self.failUnlessEqual( len(self.instance.A), 9 )
        self.failUnlessEqual( self.instance.A[1, 'A2'], 2.3 )

    def test_io5(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := A1 A2 A3;"
        print >>OUTPUT, "set Y := 1 2 3;"
        print >>OUTPUT, "param A (tr): A1 A2 A3 :="
        print >>OUTPUT, "1 1.3 2.3 3.3"
        print >>OUTPUT, "2 1.4 2.4 3.4"
        print >>OUTPUT, "3 1.5 2.5 3.5"
        print >>OUTPUT, ";"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.Y=Set()
        self.model.A=Param(self.model.Z,self.model.Y)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( len(self.instance.Y), 3 )
        self.failUnlessEqual( len(self.instance.Z), 3 )
        self.failUnlessEqual( len(self.instance.A), 9 )
        self.failUnlessEqual( self.instance.A['A2',1], 2.3 )

    def test_io6(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := 1 3 5;"
        print >>OUTPUT, "param A default 0.0 :="
        print >>OUTPUT, "1 2.2"
        print >>OUTPUT, "3 ."
        print >>OUTPUT, "5 2.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.A=Param(self.model.Z)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( len(self.instance.A), 3 )
        self.failUnlessEqual( self.instance.A[3], 0.0 )

    def test_io7(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param A := True;"
        print >>OUTPUT, "param B := False;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Param(within=Boolean)
        self.model.B=Param(within=Boolean)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( self.instance.A.value, True )
        self.failUnlessEqual( self.instance.B.value, False )

    def test_io8(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param : A : B :="
        print >>OUTPUT, "\"A\" 3.3"
        print >>OUTPUT, "\"B\" 3.4"
        print >>OUTPUT, "\"C\" 3.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Set()
        self.model.B=Param(self.model.A)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( self.instance.A.data(), set(['A','B','C']) )

    def test_io9(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param : A : B :="
        print >>OUTPUT, "\"A\" 0.1"
        print >>OUTPUT, "\"B\" 1e-1"
        print >>OUTPUT, "\"b\" 1.4e-1"
        print >>OUTPUT, "\"C\" 1E-1"
        print >>OUTPUT, "\"c\" 1.4E-1"
        print >>OUTPUT, "\"D\" 1E+1"
        print >>OUTPUT, "\"d\" 1.4E+1"
        print >>OUTPUT, "\"AA\" -0.1"
        print >>OUTPUT, "\"BB\" -1e-1"
        print >>OUTPUT, "\"bb\" -1.4e-1"
        print >>OUTPUT, "\"CC\" -1E-1"
        print >>OUTPUT, "\"cc\" -1.4E-1"
        print >>OUTPUT, "\"DD\" -1E+1"
        print >>OUTPUT, "\"dd\" -1.4E+1;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Set()
        self.model.B=Param(self.model.A)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( self.instance.B['A'], 0.1)
        self.failUnlessEqual( self.instance.B['B'], 0.1)
        self.failUnlessEqual( self.instance.B['b'], 0.14)
        self.failUnlessEqual( self.instance.B['C'], 0.1)
        self.failUnlessEqual( self.instance.B['c'], 0.14)
        self.failUnlessEqual( self.instance.B['D'], 10)
        self.failUnlessEqual( self.instance.B['d'], 14)
        self.failUnlessEqual( self.instance.B['AA'], -0.1)
        self.failUnlessEqual( self.instance.B['BB'], -0.1)
        self.failUnlessEqual( self.instance.B['bb'], -0.14)
        self.failUnlessEqual( self.instance.B['CC'], -0.1)
        self.failUnlessEqual( self.instance.B['cc'], -0.14)
        self.failUnlessEqual( self.instance.B['DD'], -10)
        self.failUnlessEqual( self.instance.B['dd'], -14)

    def test_io10(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set A1 := a b c d e f g h i j k l ;"
        print >>OUTPUT, "set A2 := 2 4 6 ;"
        print >>OUTPUT, "param B :="
        print >>OUTPUT, " [*,2,*] a b 1 c d 2 e f 3"
        print >>OUTPUT, " [*,4,*] g h 4 i j 5"
        print >>OUTPUT, " [*,6,*] k l 6"
        print >>OUTPUT, ";"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A1=Set()
        self.model.A2=Set()
        self.model.B=Param(self.model.A1,self.model.A2,self.model.A1)
        self.instance = self.model.create("param.dat")
        self.failUnlessEqual( set(self.instance.B.keys()), set([('e', 2, 'f'), ('c', 2, 'd'), ('a', 2, 'b'), ('i', 4, 'j'), ('g', 4, 'h'), ('k', 6, 'l')]))


class TestParamError(PyomoModel):

    def test_value(self):
        p = Param()
        try:
            value(p)
            self.fail("expected ValueError")
        except ValueError:
            pass
        self.failUnlessEqual(p.value,None)

if __name__ == "__main__":
   unittest.main()
