#
# Unit Tests for Elements of a Model
#
# TestSimpleCon                Class for testing single constraint
# TestArrayCon                Class for testing array of constraint
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


class TestSimpleCon(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        pass

    def test_expr1(self):
        """Test expr option"""
        self.model = ConcreteModel()
        self.model.x = Var(RangeSet(1,4),initialize=2)
        ans=0
        for i in self.model.x.keys():
            ans = ans + self.model.x[i]
        ans = ans >= 0
        ans = ans <= 1
        self.model.c = Constraint(expr=ans)
        self.instance = self.model.create()
        try:
            self.failUnlessEqual(self.instance.c(), 8)
        except ValueError:
            pass
        else:
            self.fail("test_expr_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 8)
        self.failUnlessEqual(value(self.instance.c), 8)

    def test_expr2(self):
        """Test expr option"""
        self.model = ConcreteModel()
        self.model.x = Var(initialize=2)
        ans = self.model.x >= 0
        ans = ans <= 1
        self.model.c = Constraint(expr=ans)
        self.instance = self.model.create()
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 2)
        self.failUnlessEqual(value(self.instance.c), 2)

    def test_rule1(self):
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          ans = ans >= 0
          ans = ans <= 1
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.c(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 8)
        self.failUnlessEqual(value(self.instance.c), 8)

    def test_rule2(self):
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return (0,ans,1)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.c(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 8)
        self.failUnlessEqual(value(self.instance.c), 8)

    def test_rule3(self):
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return (0,ans,None)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.c(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 8)
        self.failUnlessEqual(value(self.instance.c), 8)

    def test_rule4(self):
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return (None,ans,1)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.c(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 8)
        self.failUnlessEqual(value(self.instance.c), 8)

    def test_rule5(self):
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          return (ans,1)
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        try:
          self.failUnlessEqual(self.instance.c(), 8)
        except ValueError:
          pass
        else:
          self.fail("test_rule_option")
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c(), 8)
        self.failUnlessEqual(value(self.instance.c), 8)

    def test_dim(self):
        """Test dim method"""
        self.model.c = Constraint()
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.c.dim(),0)

    def test_keys(self):
        """Test keys method"""
        self.model.c = Constraint()
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.c.keys(),[])

    def test_len(self):
        """Test len method"""
        self.model.c = Constraint()
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c),0)
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          ans = ans == 0
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c),1)


class TestArrayCon(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        self.model.A = Set(initialize=[1,2,3,4])

    def tearDown(self):
        pass

    def test_rule_option1(self):
        """Test rule option"""
        def f(i,model):
          ans=0
          for j in model.x.keys():
            ans = ans + model.x[j]
          ans *= i
          ans = ans < 0
          ans = ans > 0
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        try:
            self.instance.c[1]()
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c[1](), 8)
        self.failUnlessEqual(self.instance.c[2](), 16)
        self.failUnlessEqual(value(self.instance.c[1]), 8)
        self.failUnlessEqual(value(self.instance.c[2]), 16)
        self.failUnlessEqual(len(self.instance.c), 4)

    def test_rule_option2(self):
        """Test rule option"""
        def f(i,model):
          if i%2 == 0:
                return 0
          ans=0
          for j in model.x.keys():
            ans = ans + model.x[j]
          ans *= i
          ans = ans < 0
          ans = ans > 0
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        try:
            self.instance.c[1]()
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c[1](), 8)
        self.failUnlessEqual(value(self.instance.c[1]), 8)
        self.failUnlessEqual(len(self.instance.c), 2)

    def test_rule_option3(self):
        """Test rule option"""
        def f(i,model):
          if i%2 == 0:
                return None
          ans=0
          for j in model.x.keys():
            ans = ans + model.x[j]
          ans *= i
          ans = ans < 0
          ans = ans > 0
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,rule=f)
        self.instance = self.model.create()
        try:
            self.instance.c[1]()
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c[1](), 8)
        self.failUnlessEqual(value(self.instance.c[1]), 8)
        self.failUnlessEqual(len(self.instance.c), 2)

    def test_dim(self):
        """Test dim method"""
        self.model.c = Constraint(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.c.dim(),1)

    def test_keys(self):
        """Test keys method"""
        self.model.c = Constraint(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c.keys()),0)

    def test_len(self):
        """Test len method"""
        self.model.c = Constraint(self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c),0)
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          ans = ans==2
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c),1)


class Test2DArrayCon(PyomoModel):

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
        def f(i,j,model):
          ans=0
          for j in model.x.keys():
            ans = ans + model.x[j]
          ans *= i
          ans = ans < 0
          ans = ans > 0
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(self.model.A,self.model.A,rule=f)
        self.instance = self.model.create()
        try:
            self.instance.c[1,1]()
            self.fail("Expected ValueError")
        except ValueError:
            pass
        self.instance.x.reset()
        self.failUnlessEqual(self.instance.c[1,1](), 8)
        self.failUnlessEqual(self.instance.c[2,1](), 16)
        self.failUnlessEqual(value(self.instance.c[1,1]), 8)
        self.failUnlessEqual(value(self.instance.c[2,1]), 16)

    def test_dim(self):
        """Test dim method"""
        self.model.c = Constraint(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(self.instance.c.dim(),2)

    def test_keys(self):
        """Test keys method"""
        self.model.c = Constraint(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c.keys()),0)

    def test_len(self):
        """Test len method"""
        self.model.c = Constraint(self.model.A,self.model.A)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c),0)
        """Test rule option"""
        def f(model):
          ans=0
          for i in model.x.keys():
            ans = ans + model.x[i]
          ans = ans==2
          return ans
        self.model.x = Var(RangeSet(1,4),initialize=2)
        self.model.c = Constraint(rule=f)
        self.instance = self.model.create()
        self.failUnlessEqual(len(self.instance.c),1)

if __name__ == "__main__":
   unittest.main()

