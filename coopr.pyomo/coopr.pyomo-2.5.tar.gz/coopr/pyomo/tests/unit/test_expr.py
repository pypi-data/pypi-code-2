#
# Unit Tests for Expression and Related Objects
#
# PyomoModel        Base test class
# TestNumericValue  Class for testing NumericValue()
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest

class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = Model()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class TestNumericValueBase(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.type=NumericConstant

    def tearDown(self):
        pass

    def create(self,val,domain):
        tmp=self.type(value=val, domain=domain)
        return tmp

    @nottest
    def equal_test(self,exp,val):
        if isinstance(exp,Expression):
           self.failUnlessEqual(exp(),val)
        else:
           self.failUnlessEqual(exp,val)

    def test_valid_value(self):
        """Check that values can be validated"""
        a=self.create(1.3,Reals)
        a._valid_value(a.value)
        #b=self.create(1.3,Integers)
        #b._valid_value(b.value)
        #print "HERE",type(b),b,b._attr_domain
        #print "HERE",b.domain
        #print "HERE", b.value
        #print "HERE", b.value in b.domain
        try:
          b=self.create(1.3,Integers)
          b._valid_value(b.value)
        except ValueError:
          pass
        else:
          self.fail("test_valid_value")

    def test_getattr(self):
        """Check that attributes can be retrieved"""
        a=self.create(1.3,Reals)
        try:
          a.__getattr__("_x")
        except AttributeError:
          pass
        else:
          self.fail("test_getattr")
        try:
          a.__getattr__("x")
        except AttributeError:
          pass
        else:
          self.fail("test_getattr")

    def Xtest_setattr(self):
        """Check that attributes can be set"""
        a=self.create(1.3,Reals)
        try:
          a.x=1
        except AttributeError:
          pass
        else:
          self.fail("test_setattr")
        a._x=1
        tmp=a._x
        a._standard_attr.add("x")
        a.x=1

    def test_lt(self):
        a=self.create(1.3,Reals)
        b=self.create(2.0,Reals)
        self.equal_test(a<b,True)
        self.equal_test(a<a,False)
        self.equal_test(b<a,False)
        self.equal_test(a<2.0,True)
        self.equal_test(a<1.3,False)
        self.equal_test(b<1.3,False)
        self.equal_test(1.3<b,True)
        self.equal_test(1.3<a,False)
        self.equal_test(2.0<a,False)

    def test_gt(self):
        a=self.create(1.3,Reals)
        b=self.create(2.0,Reals)
        self.equal_test(a>b,False)
        self.equal_test(a>a,False)
        self.equal_test(b>a,True)
        self.equal_test(a>2.0,False)
        self.equal_test(a>1.3,False)
        self.equal_test(b>1.3,True)
        self.equal_test(1.3>b,False)
        self.equal_test(1.3>a,False)
        self.equal_test(2.0>a,True)

    def test_eq(self):
        a=self.create(1.3,Reals)
        b=self.create(2.0,Reals)
        self.equal_test(a==b,False)
        self.equal_test(a==a,True)
        self.equal_test(b==a,False)
        self.equal_test(a==2.0,False)
        self.equal_test(a==1.3,True)
        self.equal_test(b==1.3,False)
        self.equal_test(1.3==b,False)
        self.equal_test(1.3==a,True)
        self.equal_test(2.0==a,False)

    def test_arith(self):
        a=self.create(0.5,Reals)
        b=self.create(2.0,Reals)
        self.equal_test(a-b,-1.5)
        self.equal_test(a+b,2.5)
        self.equal_test(a*b,1.0)
        self.equal_test(b/a,4.0)
        self.equal_test(a**b,0.25)

        self.equal_test(a-2.0,-1.5)
        self.equal_test(a+2.0,2.5)
        self.equal_test(a*2.0,1.0)
        self.equal_test(b/(0.5),4.0)
        self.equal_test(a**2.0,0.25)

        self.equal_test(0.5-b,-1.5)
        self.equal_test(0.5+b,2.5)
        self.equal_test(0.5*b,1.0)
        self.equal_test(2.0/a,4.0)
        self.equal_test((0.5)**b,0.25)

        self.equal_test(-a,-0.5)
        self.equal_test(+a,0.5)
        self.equal_test(abs(-a),0.5)



class TestNumericConstant(TestNumericValueBase):

    def setUp(self):
        #
        # Create Model
        #
        TestNumericValueBase.setUp(self)
        #
        # Create model instance
        #
        self.type=NumericConstant

    #def create(self,val,domain):
        #tmp=self.type(val, domain)
        #tmp._domain=domain
        #return tmp

    def test_asnum(self):
        try:
            as_numeric(None)
            self.fail("test_asnum - expected ValueError")
        except ValueError:
            pass


class TestVarValue(TestNumericValueBase):

    def setUp(self):
        import coopr.pyomo.base.var
        #
        # Create Model
        #
        TestNumericValueBase.setUp(self)
        #
        # Create model instance
        #
        self.type=coopr.pyomo.base.var._VarValue

    def create(self,val,domain):
        tmp=self.type(name="unknown",domain=domain)
        tmp.value=val
        return tmp


class TestNumericValue(pyutilib.th.TestCase):

    def test_vals(self):
        # the following aspect of this test is being removed due to the check seminatics
        # of a numeric constant requiring far too much run-time, especially when involved
        # in expression tree construction. if the user specifies a constant, we're assuming
        # it is correct.
#        try:
#            NumericConstant(value='a')
#            self.fail("Cannot initialize a constant with a non-numeric value")
#        except ValueError:
#            pass
        a = NumericConstant(value=1.1)
        b = float(a)
        self.failUnlessEqual(b,1.1)
        b = int(a)
        self.failUnlessEqual(b,1)

    def Xtest_getattr1(self):
        a = NumericConstant(value=1.1)
        try:
            a.model
            self.fail("Expected error")
        except AttributeError:
            pass

    def test_ops(self):
        a = NumericConstant(value=1.1)
        b = NumericConstant(value=2.2)
        c = NumericConstant(value=-2.2)
        a <= b
        self.failUnlessEqual(a() <= b(), True)
        self.failUnlessEqual(a() >= b(), False)
        self.failUnlessEqual(a() == b(), False)
        self.failUnlessEqual(abs(a() + b()-3.3) <= 1e-7, True)
        self.failUnlessEqual(abs(b() - a()-1.1) <= 1e-7, True)
        self.failUnlessEqual(abs(b() * 3-6.6) <= 1e-7, True)
        self.failUnlessEqual(abs(b() / 2-1.1) <= 1e-7, True)
        self.failUnlessEqual(abs(abs(-b())-2.2) <= 1e-7, True)
        self.failUnlessEqual(abs(c()), 2.2)
        self.failUnlessEqual(str(c), "-2.2")

    def test_expr(self):
        model = Model()
        model.a = Var()
        model.b = Param(initialize=2)
        instance=model.create()
        expr = instance.a+1
        expr = expr-1
        expr = expr*instance.a
        expr = expr/instance.a
        expr = expr**instance.b
        expr = 1-expr
        expr = 1+expr
        expr = 2*expr
        expr = 2/expr
        expr = 2**expr
        expr = - expr
        expr = + expr
        expr = abs(expr)
        OUTPUT=open(currdir+"expr.out","w")
        expr.pprint(ostream=OUTPUT)
        expr.simplify(instance)
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.failUnlessFileEqualsBaseline(currdir+"expr.out",currdir+"expr.txt")


class MiscVarTests(pyutilib.th.TestCase):

    def test_error1(self):
        a = Var(name="a")
        try:
            a = Var(foo=1)
            self.fail("test_error1")
        except ValueError:
            pass

    def test_getattr1(self):
        """
        Verify the behavior of non-standard suffixes with simple variable
        """
        model = Model()
        model.a = Var()
        #try:
            #model.a.suffix = True
            #self.fail("Expected AttributeError")
        #except AttributeError:
            #pass
        model.a.declare_attribute("suffix")
        model.a.declare_attribute("foo",default=False)
        #try:
            #
            # This fails because we don't have an instance
            #
            #model.a.suffix = True
            #self.fail("Expected TypeError")
        #except TypeError:
            #pass
        instance = model.create()
        self.failUnlessEqual(instance.a.suffix,None)
        instance.a.suffix = True
        self.failUnlessEqual(instance.a.suffix,True)
        self.failUnlessEqual(instance.a.foo,False)

    def test_getattr2(self):
        """
        Verify the behavior of non-standard suffixes with an array of variables
        """
        model = Model()
        model.X = Set(initialize=[1,3,5])
        model.a = Var(model.X)
        #try:
            #model.a.suffix = True
            #self.fail("Expected AttributeError")
        #except AttributeError:
            #pass
        model.a.declare_attribute("suffix")
        model.a.declare_attribute("foo",default=False)
        #try:
            #model.a.suffix = True
            #self.fail("Expected TypeError")
        #except TypeError:
            #pass
        try:
            self.failUnlessEqual(model.a.suffix,None)
            self.fail("Expected AttributeError")
        except AttributeError:
            pass
        instance = model.create()
        self.failUnlessEqual(instance.a[1].suffix,None)
        #
        # Cannot set all suffixes simultaneously
        #
        instance.a.suffix = True
        self.failUnlessEqual(instance.a[1].suffix,None)
        self.failUnlessEqual(instance.a[3].foo,False)

    def test_error2(self):
        try:
            model=Model()
            model.a = Var(initialize=[1,2,3])
            model.b = Var(model.a)
            self.fail("test_error2")
        except TypeError:
            pass

    def test_contains(self):
        model=Model()
        model.a = Set(initialize=[1,2,3])
        model.b = Var(model.a)
        instance = model.create()
        self.failUnlessEqual(1 in instance.b,True)

    def test_float_int(self):
        model=Model()
        model.a = Set(initialize=[1,2,3])
        model.b = Var(model.a,initialize=1.1)
        model.c = Var(initialize=2.1)
        model.d = Var()
        instance = model.create()
        instance.reset()
        self.failUnlessEqual(float(instance.b[1]),1.1)
        self.failUnlessEqual(int(instance.b[1]),1)
        self.failUnlessEqual(float(instance.c),2.1)
        self.failUnlessEqual(int(instance.c),2)
        try:
            float(instance.d)
            self.fail("expected ValueError")
        except ValueError:
            pass
        try:
            int(instance.d)
            self.fail("expected ValueError")
        except ValueError:
            pass
        try:
            float(instance.b)
            self.fail("expected TypeError")
        except TypeError:
            pass
        try:
            int(instance.b)
            self.fail("expected TypeError")
        except TypeError:
            pass

    def test_set_get(self):
        model=Model()
        model.a = Set(initialize=[1,2,3])
        model.b = Var(model.a,initialize=1.1,within=PositiveReals)
        model.c = Var(initialize=2.1, within=PositiveReals)
        try:
            model.b = 2.2
            self.fail("can't set the value of an array variable")
        except ValueError:
            pass
        instance = model.create()
        try:
            instance.c[1]=2.2
            self.fail("can't use an index to set a singleton variable")
        except KeyError:
            pass
        try:
            instance.b[4]=2.2
            self.fail("can't set an array variable with a bad index")
        except KeyError:
            pass
        try:
            instance.b[3] = -2.2
            #print "HERE",type(instance.b[3])
            self.fail("can't set an array variable with a bad value")
        except ValueError:
            pass
        try:
            tmp = instance.c[3]
            self.fail("can't index a singleton variable")
        except KeyError:
            pass

        try:
            instance.c.set_value('a')
            self.fail("can't set a bad value for variable c")
        except ValueError:
            pass
        try:
            instance.c.set_value(-1.0)
            self.fail("can't set a bad value for variable c")
        except ValueError:
            pass

        try:
            instance.c.initial = 'a'
            instance.c.reset()
            self.fail("can't set a bad initial for variable c")
        except ValueError:
            pass
        try:
            instance.c.initial = -1.0
            instance.c.reset()
            self.fail("can't set a bad initial for variable c")
        except ValueError:
            pass
        
        #try:
            #instance.c.ub = 'a'
            #self.fail("can't set a bad ub for variable c")
        #except ValueError:
            #pass
        #try:
            #instance.c.ub = -1.0
            #self.fail("can't set a bad ub for variable c")
        #except ValueError:
            #pass
        
        #try:
            #instance.c.fixed = 'a'
            #self.fail("can't fix a variable with a non-boolean")
        #except ValueError:
            #pass
        
    def test_pprint(self):
        def c1_rule(model):
            return (1.0,model.b[1],None)
        def c2_rule(model):
            return (None,model.b[1],0.0)
        def c3_rule(model):
            return (0.0,model.b[1],1.0)
        def c4_rule(model):
            return (3.0,model.b[1])
        def c5_rule(i,model):
            return (model.b[i],0.0)

        def c6a_rule(model):
            return 0.0 <= model.c
        def c6b_rule(model):
            return 0.0 < model.c
        def c7a_rule(model):
            return model.c <= 1.0
        def c7b_rule(model):
            return model.c < 1.0
        def c8_rule(model):
            return model.c == 2.0
        def c9a_rule(model):
            return model.A+model.A <= model.c
        def c9b_rule(model):
            return model.A+model.A < model.c
        def c10a_rule(model):
            return model.c <= model.B+model.B
        def c10b_rule(model):
            return model.c < model.B+model.B
        def c11_rule(model):
            return model.c == model.A+model.B
        def c15a_rule(model):
            return model.A <= model.A*model.d
        def c15b_rule(model):
            return model.A < model.A*model.d
        def c16a_rule(model):
            return model.A*model.d <= model.B
        def c16b_rule(model):
            return model.A*model.d < model.B

        def c12_rule(model):
            return model.c == model.d
        def c13a_rule(model):
            return model.c <= model.d
        def c13b_rule(model):
            return model.c < model.d
        def c14a_rule(model):
            return model.c >= model.d
        def c14b_rule(model):
            return model.c > model.d

        #def c20_rule(model):
            #return model.A > model.c > model.B
        #def c21_rule(model):
            #return model.A > model.c < model.B
        #def c22_rule(model):
            #return model.A < model.c > model.B
        #def c23_rule(model):
            #return model.A < model.c < model.B

        def o2_rule(i,model):
            return model.b[i]
        model=Model()
        model.a = Set(initialize=[1,2,3])
        model.b = Var(model.a,initialize=1.1,within=PositiveReals)
        model.c = Var(initialize=2.1, within=PositiveReals)
        model.d = Var(initialize=3.1, within=PositiveReals)
        model.e = Var(initialize=4.1, within=PositiveReals)
        model.A = Param(default=-1)
        model.B = Param(default=-2)
        #model.o1 = Objective()
        model.o2 = Objective(model.a,rule=o2_rule)
        model.o3 = Objective(model.a,model.a)
        model.c1 = Constraint(rule=c1_rule)
        model.c2 = Constraint(rule=c2_rule)
        model.c3 = Constraint(rule=c3_rule)
        model.c4 = Constraint(rule=c4_rule)
        model.c5 = Constraint(model.a,rule=c5_rule)

        model.c6a = Constraint(rule=c6a_rule)
        model.c6b = Constraint(rule=c6b_rule)
        model.c7a = Constraint(rule=c7a_rule)
        model.c7b = Constraint(rule=c7b_rule)
        model.c8 = Constraint(rule=c8_rule)
        model.c9a = Constraint(rule=c9a_rule)
        model.c9b = Constraint(rule=c9b_rule)
        model.c10a = Constraint(rule=c10a_rule)
        model.c10b = Constraint(rule=c10b_rule)
        model.c11 = Constraint(rule=c11_rule)
        model.c15a = Constraint(rule=c15a_rule)
        model.c15b = Constraint(rule=c15b_rule)
        model.c16a = Constraint(rule=c16a_rule)
        model.c16b = Constraint(rule=c16b_rule)

        model.c12 = Constraint(rule=c12_rule)
        model.c13a = Constraint(rule=c13a_rule)
        model.c13b = Constraint(rule=c13b_rule)
        model.c14a = Constraint(rule=c14a_rule)
        model.c14b = Constraint(rule=c14b_rule)

        #model.c20 = Constraint(rule=c20_rule)
        #model.c21 = Constraint(rule=c21_rule)
        #model.c22 = Constraint(rule=c22_rule)
        #model.c23 = Constraint(rule=c23_rule)

        instance=model.create()
        OUTPUT=open(currdir+"varpprint.out","w")
        instance.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.failUnlessFileEqualsBaseline(currdir+"varpprint.out",currdir+"varpprint.txt")

    def test_expr_error1(self):
        m = Model()
        m.A = Set()
        m.p = Param(m.A)
        m.q = Param()
        e = m.q*2
        try:
            m.p * 2
            self.fail("Expected TypeError")
        except TypeError:
            pass



class MiscParamTests(pyutilib.th.TestCase):

    def test_constructor(self):
        a = Param(name="a")
        try:
            b = Param(foo="bar")
            self.fail("Cannot pass in 'foo' as an option to Param")
        except ValueError:
            pass
        model=Model()
        model.b = Param(initialize=[1,2,3])
        try:
            model.c = Param(model.b)
            self.fail("Can't index a parameter with a parameter")
        except TypeError:
            pass
        #
        model = Model()
        model.a = Param(initialize={None:3.3})
        instance = model.create()

    def test_get_set(self):
        model=Model()
        model.a = Param()
        model.b = Set(initialize=[1,2,3])
        model.c = Param(model.b,initialize=2, within=Reals)
        #try:
            #model.a.value = 3
            #self.fail("can't set the value of an unitialized parameter")
        #except AttributeError:
            #pass
        try:
            model.a.construct()
            self.fail("Can't construct a parameter without data")
        except ValueError:
            pass
        model.a = Param(initialize=2)
        instance=model.create()
        instance.a.value=3
        #try:
            #instance.a.default='2'
            #self.fail("can't set a bad default value")
        #except ValueError:
            #pass
        self.failUnlessEqual(2 in instance.c, True)

        try:
            instance.a[1] = 3
            self.fail("can't index a singleton parameter")
        except KeyError:
            pass
        try:
            instance.c[4] = 3
            self.fail("can't index a parameter with a bad index")
        except KeyError:
            pass
        try:
            instance.c[3] = 'a'
            self.fail("can't set a parameter with a bad value")
        except ValueError:
            pass

    def test_iter(self):
        model=Model()
        model.b = Set(initialize=[1,2,3])
        model.c = Param(model.b,initialize=2)
        instance = model.create()
        for i in instance.c:
            self.failUnlessEqual(i in instance.c, True)

    def test_valid(self):
        def d_valid(a,model):
            return True
        def e_valid(a,i,j,model):
            return True
        model=Model()
        model.b = Set(initialize=[1,3,5])
        model.c = Param(initialize=2, within=None)
        model.d = Param(initialize=(2,3), validate=d_valid)
        model.e = Param(model.b,model.b,initialize={(1,1):(2,3)}, validate=e_valid)
        instance = model.create()
        instance.e.check_values()
        #try:
            #instance.c.value = 'b'
            #self.fail("can't have a non-numerical parameter")
        #except ValueError:
            #pass

    def test_expr_error1(self):
        m = Model()
        m.A = Set()
        m.p = Param(m.A)
        m.q = Param()
        e = m.q*2
        try:
            m.p*2
            self.fail("Expected TypeError")
        except TypeError:
            pass


class MiscExprTests(pyutilib.th.TestCase):

    def setUp(self):
        def d_fn(model):
            return model.c+model.c
        self.model=Model()
        self.model.a = Var(initialize=1.0)
        self.model.b = Var(initialize=2.0)
        self.model.c = Param(initialize=0)
        self.model.d = Param(initialize=d_fn)
        self.instance= self.model.create()

    def test_lt(self):
        expr = self.instance.a < self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),True)

    def test_lte(self):
        expr = self.instance.a <= self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),True)

    def test_gt(self):
        expr = self.instance.a > self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),False)

    def test_gte(self):
        expr = self.instance.a >= self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),False)

    def test_eq(self):
        expr = self.instance.a == self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),False)

    def test_minus(self):
        expr = self.instance.a - self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),-1)

    def test_division(self):
        expr = self.instance.a / self.instance.b
        self.instance.reset()
        self.failUnlessEqual(expr(),0.5)

    def test_negate(self):
        expr = - self.instance.a
        self.instance.reset()
        self.failUnlessEqual(expr(),-1)

    def test_prod(self):
        OUTPUT=open(currdir+"test_prod.out","w")
        expr = self.model.a * self.model.a * self.model.a
        expr.pprint(ostream=OUTPUT)
        expr = expr.simplify(self.model)
        expr.pprint(ostream=OUTPUT)

        expr = expr*0
        expr.pprint(ostream=OUTPUT)
        expr = expr.simplify(self.model)
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.failUnlessFileEqualsBaseline(currdir+"test_prod.out",currdir+"test_prod.txt")


class MiscObjTests(pyutilib.th.TestCase):

    def test_constructor(self):
        a = Objective(name="b")
        self.failUnlessEqual(a.name,"b")
        try:
            a = Objective(foo="bar")
            self.fail("Can't specify an unexpected constructor option")
        except ValueError:
            pass

    def test_contains(self):
        model=Model()
        model.a=Set(initialize=[1,2,3])
        model.x=Var()
        def b_rule(i,model):
            return model.x
        model.b=Objective(model.a, rule=b_rule)
        instance=model.create()
        self.failUnlessEqual(2 in instance.b,True)
        tmp=[]
        for i in instance.b:
          tmp.append(i)
        self.failUnlessEqual(len(tmp),3)

    def test_set_get(self):
        a = Objective()
        #try:
            #a.value = 1
            #self.fail("Can't set value attribute")
        #except AttributeError:
            #pass
        self.failUnlessEqual(a(),None)
        #
        model=Model()
        model.x = Var(initialize=1)
        model.y = Var(initialize=2)
        model.obj = Objective()
        model.obj._data[None].expr = model.x+model.y
        instance = model.create()
        instance.reset()
        self.failUnlessEqual(instance.obj(),3)

    def test_rule(self):
        def rule1(model):
            return None
        model=Model()
        model.o = Objective(rule=rule1)
        try:
            instance=model.create()
            self.fail("Error generating objective")
        except Exception:
            pass
        #
        def rule1(model):
            return 1.1
        model=Model()
        model.o = Objective(rule=rule1)
        instance=model.create()
        self.failUnlessEqual(instance.o(),1.1)
        #
        def rule1(i,model):
            return 1.1
        model=Model()
        model.a=Set(initialize=[1,2,3])
        model.o = Objective(model.a,rule=rule1)
        instance=model.create()
        try:
            instance=model.create()
        except Exception:
            self.fail("Error generating objective")
        

class MiscConTests(pyutilib.th.TestCase):

    def test_constructor(self):
        a = Constraint(name="b")
        self.failUnlessEqual(a.name,"b")
        try:
            a = Constraint(foo="bar")
            self.fail("Can't specify an unexpected constructor option")
        except ValueError:
            pass

    def test_contains(self):
        model=Model()
        model.a=Set(initialize=[1,2,3])
        model.b=Constraint(model.a)
        instance=model.create()
        self.failUnlessEqual(2 in instance.b,False)
        tmp=[]
        for i in instance.b:
          tmp.append(i)
        self.failUnlessEqual(len(tmp),0)

    def test_set_get(self):
        a = Constraint()
        #try:
            #a.value = 1
            #self.fail("Can't set value attribute")
        #except AttributeError:
            #pass
        self.failUnlessEqual(a(),None)

    def test_rule(self):
        def rule1(model):
            return None
        model=Model()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        try:
            instance=model.create()
        except Exception, e:
            self.fail("Failure to create empty constraint: %s" % str(e))
        #
        def rule1(model):
            return (0.0,model.x,2.0)
        model=Model()
        model.x = Var(initialize=1.1)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        instance.reset()
        self.failUnlessEqual(instance.o(),1.1)
        #
        def rule1(i,model):
            return None
        model=Model()
        model.a=Set(initialize=[1,2,3])
        model.o = Constraint(model.a,rule=rule1)
        try:
            instance=model.create()
        except Exception:
            self.fail("Error generating empty objective")
        #
        def rule1(model):
            return (0.0,1.1,2.0,None)
        model=Model()
        model.o = Constraint(rule=rule1)
        try:
            instance=model.create()
            self.fail("Can only return tuples of length 2 or 3")
        except ValueError:
            pass
        
    def test_constructor_coverage(self):
        def rule1(model):
            return (0.0,model.x)
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            return (model.y,model.x,model.z)
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr=model.x
            expr = expr == 0.0
            expr = expr > 1.0
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        try:
            instance=model.create()
            self.fail("bad constraint formulation")
        except ValueError:
            pass
        #
        def rule1(model):
            expr = model.U >= model.x
            expr = expr >= model.L
            return expr
        model=Model()
        model.x = Var()
        model.L = Param(initialize=0)
        model.U = Param(initialize=1)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x <= model.z
            expr = expr >= model.y
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x >= model.z
            expr = model.y >= expr
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.y <= model.x
            expr = model.y >= expr
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x >= model.L
            return expr
        model=Model()
        model.x = Var()
        model.L = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.U >= model.x
            return expr
        model=Model()
        model.x = Var()
        model.U = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()

        #
        def rule1(model):
            expr=model.x
            expr = expr == 0.0
            expr = expr < 1.0
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        try:
            instance=model.create()
            self.fail("bad constraint formulation")
        except ValueError:
            pass
        #
        def rule1(model):
            expr = model.U <= model.x
            expr = expr <= model.L
            return expr
        model=Model()
        model.x = Var()
        model.L = Param(initialize=0)
        model.U = Param(initialize=1)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x >= model.z
            expr = expr <= model.y
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x <= model.z
            expr = model.y <= expr
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.y >= model.x
            expr = model.y <= expr
            return expr
        model=Model()
        model.x = Var()
        model.y = Var()
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.x <= model.L
            return expr
        model=Model()
        model.x = Var()
        model.L = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()
        #
        def rule1(model):
            expr = model.U <= model.x
            return expr
        model=Model()
        model.x = Var()
        model.U = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        instance=model.create()

        #
        def rule1(model):
            return model.x+model.x
        model=Model()
        model.x = Var()
        model.o = Constraint(rule=rule1)
        try:
            instance=model.create()
            self.fail("Cannot return an unbounded expression")
        except ValueError:
            pass
        #
        

if __name__ == "__main__":
   unittest.main()
