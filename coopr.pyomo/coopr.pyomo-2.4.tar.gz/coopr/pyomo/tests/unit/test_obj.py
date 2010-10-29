#
# Unit Tests for Elements of a Model
#
# TestSimpleObj                Class for testing single objective
# TestArrayObj                Class for testing array of objective
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


class TestSimpleObj(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        pass

    def test_expr1_option(self):
        """Test expr option"""
        self.model = ConcreteModel()
        self.model.x = Var(RangeSet(1,4),initialize=2)
        ans=0
        for i in self.model.x.keys():
            ans = ans + self.model.x[i]
        self.model.obj = Objective(expr=ans)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.obj(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.obj(), 8)
        self.failUnlessEqual(value(self.instance.obj), 8)

    def test_expr2_option(self):
        """Test expr option"""
        self.model = ConcreteModel()
        self.model.x = Var(initialize=2)
        self.model.obj = Objective(expr=self.model.x)
        self.instance = self.model.create()
        self.instance.x.reset()
        print 'X',type(self.instance.obj.rule)
        self.failUnlessEqual(self.instance.obj(), 2)
        self.failUnlessEqual(value(self.instance.obj), 2)

    def test_rule_option(self):
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.obj(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.obj(), 8)
        self.failUnlessEqual(value(self.instance.obj), 8)

    def test_arguments(self):
        """Test that arguments notare of type _SetContainer"""
        def rule(model):
            return 1
        try:
            self.model.obj = Objective(self.model, rule=rule)
        except TypeError:
            pass
        else:
            self.fail("Objective should only accept '_SetContainter's")
        

    def test_sense_option(self):
        """Test sense option"""
        def rule(model):
            return 1.0
        self.model.obj = Objective(sense=maximize, rule=rule)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.sense, maximize)

    def test_dim(self):
        """Test dim method"""
        def rule(model):
            return 1
        self.model.obj = Objective(rule=rule)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.dim(),0)

    def test_keys(self):
        """Test keys method"""
        def rule(model):
            return 1
        self.model.obj = Objective(rule=rule)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.keys(),[None])

    def test_len(self):
        """Test len method"""
        def rule(model):
            return 1.0
        self.model.obj = Objective(rule=rule)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj),1)
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj),1)


class TestArrayObj(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def tearDown(self):
        pass

    def test_rule_option(self):
        """Test rule option"""
        def f(i,model):
          ans=0
          for j in model.x.keys():
            ans = ans + model.x[j]
          ans *= i
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(self.model.A,rule=f)
        self.instance = self.model.create()
        try:
            self.instance.obj[1]()
            self.fail("Excepted ValueError due to uninitialized variables")
        except ValueError:
            pass
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.obj[1](), 8)
        self.failUnlessEqual(self.instance.obj[2](), 16)
        self.failUnlessEqual(value(self.instance.obj[1]), 8)
        self.failUnlessEqual(value(self.instance.obj[2]), 16)

    def test_sense_option(self):
        """Test sense option"""
        self.model.obj = Objective(self.model.A,sense=maximize)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.sense, maximize)

    def test_dim(self):
        """Test dim method"""
        self.model.obj = Objective(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.dim(),1)

    def test_keys(self):
        """Test keys method"""
        def A_rule(i, model):
            return model.x
        self.model.x = Var()
        self.model.obj = Objective(self.model.A, rule=A_rule)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj.keys()),2)

    def test_len(self):
        """Test len method"""
        self.model.obj = Objective(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj),0)
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj),1)


class Test2DArrayObj(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2])

    def tearDown(self):
        pass

    def test_rule_option(self):
        """Test rule option"""
        def f(i,k,model):
          ans=0
          for j in model.x.keys():
            ans = ans + model.x[j]
          ans *= i
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(self.model.A,self.model.A, rule=f)
        self.instance = self.model.create()
        try:
            self.failUnlessEqual(self.instance.obj(),None)
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.obj[1,1](), 8)
        self.failUnlessEqual(self.instance.obj[2,1](), 16)
        self.failUnlessEqual(value(self.instance.obj[1,1]), 8)
        self.failUnlessEqual(value(self.instance.obj[2,1]), 16)

    def test_sense_option(self):
        """Test sense option"""
        self.model.obj = Objective(self.model.A,self.model.A,sense=maximize)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.sense, maximize)

    def test_dim(self):
        """Test dim method"""
        self.model.obj = Objective(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.obj.dim(),2)

    def test_keys(self):
        """Test keys method"""
        def A_rule(i,j,model):
            return model.x
        self.model.x = Var()
        self.model.obj = Objective(self.model.A,self.model.A, rule=A_rule)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj.keys()),4)

    def test_len(self):
        """Test len method"""
        self.model.obj = Objective(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj),0)
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.obj = Objective(rule=f)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.obj),1)


if __name__ == "__main__":
   unittest.main()

