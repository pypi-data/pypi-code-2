#
# Unit Tests for Elements of a Model
#
# TestSimpleVar                Class for testing single variables
# TestArrayVar                Class for testing array of variables
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo.base import IntegerSet
from coopr.pyomo import *
from coopr.opt import *
from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services

class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = Model()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class TestSimpleVar(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        pass

    def test_fixed_attr(self):
        """Test fixed attribute"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.instance.x.fixed = True
        self.failUnlessEqual(self.instance.x.fixed, True)

    def test_value_attr(self):
        """Test value attribute"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.instance.x.value = 3.5
        self.failUnlessEqual(self.instance.x.value, 3.5)

    def test_initial_attr(self):
        """Test initial attribute"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.instance.x.initial = 3.5
        self.failUnlessEqual(self.instance.x.initial, 3.5)

    def test_domain_attr(self):
        """Test domain attribute"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.instance.x.domain = Integers
        self.failUnlessEqual(type(self.instance.x.domain), IntegerSet)

    def test_name_attr(self):
        """Test name attribute"""
        #
        # A user would never need to do this, but this 
        # attribute is needed within Pyomo
        #
        self.model.x = Var()
        self.model.x.name = "foo"
        self.failUnlessEqual(self.model.x.name, "foo")

    def test_lb_attr1(self):
        """Test lb attribute"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.instance.x.setlb(-1.0)
        self.failUnlessEqual(self.instance.x.lb(), -1.0)

    def test_lb_attr2(self):
        """Test lb attribute"""
        self.model.x = Var(within=NonNegativeReals, bounds=(-1,2))
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.lb(), 0.0)
        self.failUnlessEqual(self.instance.x.ub(), 2.0)

    def test_ub_attr1(self):
        """Test ub attribute"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.instance.x.setub(1.0)
        self.failUnlessEqual(self.instance.x.ub(), 1.0)

    def test_ub_attr2(self):
        """Test ub attribute"""
        self.model.x = Var(within=NonPositiveReals, bounds=(-2,1))
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.lb(), -2.0)
        self.failUnlessEqual(self.instance.x.ub(), 0.0)

    def test_within_option(self):
        """Test within option"""
        self.model.x = Var(within=Integers)
        self.failUnlessEqual(type(self.model.x.domain), IntegerSet)

    def test_initialize_option(self):
        """Test initialize option"""
        self.model.x = Var(initialize=1.3)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.initial, 1.3)

    def test_bounds_option1(self):
        """Test bounds option"""
        def x_bounds(model):
          return (-1.0,1.0)
        self.model.x = Var(bounds=x_bounds)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.lb(), -1.0)
        self.failUnlessEqual(self.instance.x.ub(), 1.0)

    def test_bounds_option2(self):
        """Test bounds option"""
        self.model.x = Var(bounds=(-1.0,1.0))
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.lb(), -1.0)
        self.failUnlessEqual(self.instance.x.ub(), 1.0)

    def test_rule_option(self):
        """Test rule option"""
        def x_init(model):
          return 1.3
        self.model.x = Var(initialize=x_init)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.value, None)
        self.failUnlessEqual(self.instance.x.initial, 1.3)

    def test_reset(self):
        """Test reset method"""
        self.model.x = Var(initialize=3)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.initial,3)
        self.failUnlessEqual(self.instance.x.value,None)
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.x.initial,3)
        self.failUnlessEqual(self.instance.x.initial,3)

    def test_dim(self):
        """Test dim method"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.dim(),0)

    def test_keys(self):
        """Test keys method"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.keys(),[None])

    def test_len(self):
        """Test len method"""
        self.model.x = Var()
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.x),1)

    def test_simplify(self):
        """Test simplify method"""
        self.model.x = Var()
        self.failUnlessEqual(type(self.model.x.simplify(self.model)),_VarElement)

    def test_value(self):
        """Check the value of the variable"""
        self.model.x = Var(initialize=3.3)
        self.instance = self.model.create()
        tmp = value(self.instance.x.initial)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = float(self.instance.x.initial)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = int(self.instance.x.initial)
        self.failUnlessEqual( type(tmp), int)
        self.failUnlessEqual( tmp, 3 )


class TestArrayVar(TestSimpleVar):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def test_fixed_attr(self):
        """Test fixed attribute"""
        self.model.x = Var(self.model.A)
        self.model.y = Var(self.model.A)
        self.instance = self.model.create()
        self.instance.x.fixed = True
        #try:
          #self.instance.x.fixed
        #except AttributeError:
          #pass
        #else:
          #self.fail("test_fixed_attr")
        self.failUnlessEqual(self.instance.x[1].fixed, False)
        self.instance.y[1].fixed=True
        self.failUnlessEqual(self.instance.y[1].fixed, True)

    def test_value_attr(self):
        """Test value attribute"""
        self.model.x = Var(self.model.A)
        self.model.y = Var(self.model.A)
        self.instance = self.model.create()
        try:
            self.instance.x = 3.5
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.y[1] = 3.5
        self.failUnlessEqual(self.instance.y[1], 3.5)

    #def test_initial_attr(self):
        #"""Test initial attribute"""
        #self.model.x = Var(self.model.A)
        #self.instance = self.model.create()
        #self.instance.x.initial = 3.5
        #self.failUnlessEqual(self.instance.x[1].initial, 3.5)

    #def test_lb_attr(self):
        #"""Test lb attribute"""
        #self.model.x = Var(self.model.A)
        #self.instance = self.model.create()
        #self.instance.x.setlb(-1.0)
        #self.failUnlessEqual(self.instance.x[1].lb(), -1.0)

    #def test_ub_attr(self):
        #"""Test ub attribute"""
        #self.model.x = Var(self.model.A)
        #self.instance = self.model.create()
        #self.instance.x.setub(1.0)
        #self.failUnlessEqual(self.instance.x[1].ub(), 1.0)

    def test_initialize_option(self):
        """Test initialize option"""
        self.model.x = Var(self.model.A,initialize={1:1.3,2:2.3})
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1], 1.3)
        self.failUnlessEqual(self.instance.x[2], 2.3)

    def test_bounds_option1(self):
        """Test bounds option"""
        def x_bounds(i,model):
          return (-1.0,1.0)
        self.model.x = Var(self.model.A, bounds=x_bounds)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1].lb(), -1.0)
        self.failUnlessEqual(self.instance.x[1].ub(), 1.0)

    def test_bounds_option2(self):
        """Test bounds option"""
        self.model.x = Var(self.model.A, bounds=(-1.0,1.0))
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1].lb(), -1.0)
        self.failUnlessEqual(self.instance.x[1].ub(), 1.0)

    def test_rule_option(self):
        """Test rule option"""
        def x_init(i,model):
          return 1.3
        self.model.x = Var(self.model.A, initialize=x_init)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1].initial, 1.3)

    def test_reset(self):
        """Test reset method"""
        self.model.x = Var(self.model.A,initialize=3)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1].initial,3)
        self.failUnlessEqual(self.instance.x[1].value,None)
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.x[1].initial,3)
        self.failUnlessEqual(self.instance.x[1].initial,3)

    def test_dim(self):
        """Test dim method"""
        self.model.x = Var(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.dim(),1)

    def test_keys(self):
        """Test keys method"""
        self.model.x = Var(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.keys(),[1,2])

    def test_len(self):
        """Test len method"""
        self.model.x = Var(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.x),2)

    def test_value(self):
        """Check the value of the variable"""
        self.model.x = Var(self.model.A,initialize=3.3)
        self.instance = self.model.create()
        tmp = value(self.instance.x[1].initial)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = float(self.instance.x[1].initial)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = int(self.instance.x[1].initial)
        self.failUnlessEqual( type(tmp), int)
        self.failUnlessEqual( tmp, 3 )


class Test2DArrayVar(TestSimpleVar):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def test_fixed_attr(self):
        """Test fixed attribute"""
        self.model.x = Var(self.model.A,self.model.A)
        self.model.y = Var(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.instance.x.fixed = True
        #try:
          #self.instance.x.fixed
        #except AttributeError:
          #pass
        #else:
          #self.fail("test_fixed_attr")
        self.failUnlessEqual(self.instance.x[1,2].fixed, False)
        self.instance.y[1,2].fixed=True
        self.failUnlessEqual(self.instance.y[1,2].fixed, True)

    def test_value_attr(self):
        """Test value attribute"""
        self.model.x = Var(self.model.A,self.model.A)
        self.model.y = Var(self.model.A,self.model.A)
        self.instance = self.model.create()
        try:
            self.instance.x = 3.5
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.y[1,2] = 3.5
        self.failUnlessEqual(self.instance.y[1,2], 3.5)

    #def test_initial_attr(self):
        #"""Test initial attribute"""
        #self.model.x = Var(self.model.A,self.model.A)
        #self.instance = self.model.create()
        #self.instance.x.initial = 3.5
        #self.failUnlessEqual(self.instance.x[1,1].initial, 3.5)

    #def test_lb_attr(self):
        #"""Test lb attribute"""
        #self.model.x = Var(self.model.A,self.model.A)
        #self.instance = self.model.create()
        #self.instance.x.setlb(-1.0)
        #self.failUnlessEqual(self.instance.x[2,1].lb(), -1.0)

    #def test_ub_attr(self):
        #"""Test ub attribute"""
        #self.model.x = Var(self.model.A,self.model.A)
        #self.instance = self.model.create()
        #self.instance.x.setub(1.0)
        #self.failUnlessEqual(self.instance.x[2,1].ub(), 1.0)

    def test_initialize_option(self):
        """Test initialize option"""
        self.model.x = Var(self.model.A,self.model.A,initialize={(1,1):1.3,(2,2):2.3})
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1,1], 1.3)
        self.failUnlessEqual(self.instance.x[2,2], 2.3)
        try:
            value(self.instance.x[1,2])
            self.fail("Expected KeyError")
        except KeyError:
            pass

    def test_bounds_option1(self):
        """Test bounds option"""
        def x_bounds(i,j,model):
          return (-1.0*(i+j),1.0*(i+j))
        self.model.x = Var(self.model.A, self.model.A, bounds=x_bounds)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1,1].lb(), -2.0)
        self.failUnlessEqual(self.instance.x[1,2].ub(), 3.0)

    def test_bounds_option2(self):
        """Test bounds option"""
        self.model.x = Var(self.model.A, self.model.A, bounds=(-1.0,1.0))
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1,1].lb(), -1.0)
        self.failUnlessEqual(self.instance.x[1,1].ub(), 1.0)

    def test_rule_option(self):
        """Test rule option"""
        def x_init(i,j,model):
          return 1.3
        self.model.x = Var(self.model.A, self.model.A, initialize=x_init)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1,2].initial, 1.3)

    def test_reset(self):
        """Test reset method"""
        self.model.x = Var(self.model.A,self.model.A, initialize=3)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x[1,1].initial,3)
        self.failUnlessEqual(self.instance.x[1,1].value,None)
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.x[1,1].initial,3)
        self.failUnlessEqual(self.instance.x[1,1].initial,3)

    def test_dim(self):
        """Test dim method"""
        self.model.x = Var(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.x.dim(),2)

    def test_keys(self):
        """Test keys method"""
        self.model.x = Var(self.model.A,self.model.A)
        self.instance = self.model.create()
        ans = [(1,1),(1,2),(2,1),(2,2)]
        self.failUnlessEqual(self.instance.x.keys().sort(),ans.sort())

    def test_len(self):
        """Test len method"""
        self.model.x = Var(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.x),4)

    def test_value(self):
        """Check the value of the variable"""
        self.model.x = Var(self.model.A,self.model.A,initialize=3.3)
        self.instance = self.model.create()
        tmp = value(self.instance.x[1,1].initial)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = float(self.instance.x[1,1].initial)
        self.failUnlessEqual( type(tmp), float)
        self.failUnlessEqual( tmp, 3.3 )
        tmp = int(self.instance.x[1,1].initial)
        self.failUnlessEqual( type(tmp), int)
        self.failUnlessEqual( tmp, 3 )


class TestVarComplexArray(PyomoModel):

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
        self.model.B = Var(B_index, [True,False], initialize=B_init)
        self.instance = self.model.create()
        #self.instance.pprint()
        self.failUnlessEqual(set(self.instance.B.keys()),set([(0,True),(2,True),(0,   False),(2,False)]))
        self.failUnlessEqual(self.instance.B[0,True],2)
        self.failUnlessEqual(self.instance.B[0,False],-2)
        self.failUnlessEqual(self.instance.B[2,True],4)
        self.failUnlessEqual(self.instance.B[2,False],-4)


if __name__ == "__main__":
   unittest.main()

