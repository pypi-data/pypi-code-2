#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# AMPL Problem Writer Plugin
#

from coopr.opt import ProblemFormat, WriterFactory
from coopr.pyomo.base.numtypes import minimize, maximize
from coopr.pyomo.base import *
from coopr.pyomo.base import expr
from coopr.pyomo.base import intrinsic_functions
from coopr.pyomo.base.var import _VarValue, Var, _VarElement, _VarBase
from coopr.pyomo.base import numvalue
from coopr.opt.base import *
from coopr.pyomo.base.param import _ParamValue
from coopr.pyomo.base import var
from coopr.pyomo.base import param
from pyutilib.component.core import alias
from coopr.pyomo.expr.canonical_repn import is_nonlinear, is_linear

import time

import logging
logger = logging.getLogger('coopr.pyomo')

ampl_var_id = {}

class ProblemWriter_nl(AbstractProblemWriter):

    alias(str(ProblemFormat.nl))

    def __init__(self):
        AbstractProblemWriter.__init__(self,ProblemFormat.nl)

    def __call__(self, model, filename):
        if filename is None:
            filename = model.name + ".nl"
        OUTPUT=open(filename,"w")
        ampl_var_id = {}
        symbol_map = self._print_model_NL(model,OUTPUT)
        OUTPUT.close()
        return filename, symbol_map

    def _get_bound(self, exp):
        if isinstance(exp,expr._IdentityExpression):
            return self._get_bound(exp._args[0])
        elif exp.is_constant():
            return exp()
        else:
            raise ValueError, "ERROR: nonconstant bound: " + str(exp)
            return None

    def _print_nonlinear_terms_NL(self, OUTPUT, exp):
        if isinstance(exp, expr._IntrinsicFunctionExpression):
            if exp.name == 'log':
                print >>OUTPUT, "o43  #log"
            elif exp.name == 'log10':
                print >>OUTPUT, "o42  #log10"
            elif exp.name == 'sin':
                print >>OUTPUT, "o41  #sin"
            elif exp.name == 'cos':
                print >>OUTPUT, "o46  #cos"
            elif exp.name == 'tan':
                print >>OUTPUT, "o38  #tan"
            elif exp.name == 'sinh':
                print >>OUTPUT, "o40  #sinh"
            elif exp.name == 'cosh':
                print >>OUTPUT, "o45  #cosh"
            elif exp.name == 'tanh':
                print >>OUTPUT, "o37  #tanh"
            elif exp.name == 'asin':
                print >>OUTPUT, "o51  #asin"
            elif exp.name == 'acos':
                print >>OUTPUT, "o53  #acos"
            elif exp.name == 'atan':
                print >>OUTPUT, "o49  #atan"
            elif exp.name == 'exp':
                print >>OUTPUT, "o44  #exp"
            elif exp.name == 'sqrt':
                print >>OUTPUT, "o39  #sqrt"
            elif exp.name == 'asinh':
                print >>OUTPUT, "o50  #asinh"
            elif exp.name == 'acosh':
                print >>OUTPUT, "o52  #acosh"
            elif exp.name == 'atanh':
                print >>OUTPUT, "o47  #atanh"
            elif exp.name == 'pow':
                print >>OUTPUT, "o5  #^"
            else:
                logger.error("Unsupported intrinsic function (%s)", exp.name)
                raise TypeError("ASL writer does not support '%s' expressions"
                                % exp.name)

            for child_exp in exp._args:
                self._print_nonlinear_terms_NL(OUTPUT, child_exp)

        elif isinstance(exp, expr._SumExpression):
            n = len(exp._args)

            if n > 2:
                print >>OUTPUT, "o54  #sum"
                print >>OUTPUT, n

                if exp._const != 0.0:
                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "n%s" %exp._const

                for i in xrange(0,n):
                    if exp._coef[i] != 1:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %exp._coef[i]
                    self._print_nonlinear_terms_NL(OUTPUT, exp._args[i])
            else:
                if exp._const != 0.0:
                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "n%s" %exp._const

                for i in xrange(0,n-1):
                    print >>OUTPUT, "o0  #+"
                    if exp._coef[i] != 1:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %exp._coef[i]
                    self._print_nonlinear_terms_NL(OUTPUT, exp._args[i])

                if exp._coef[n-1] != 1:
                    print >>OUTPUT, "o2  #*"
                    print >>OUTPUT, "n%s" %exp._coef[n-1]
                self._print_nonlinear_terms_NL(OUTPUT, exp._args[n-1])

        elif isinstance(exp, list):
            # this is an implied summation of expressions (we did not create a new sum expression for efficiency)
            # this should be a list of tuples where [0] is the coeff and [1] is the expr to write
            n = len(exp)
            if n > 2:
                print >>OUTPUT, "o54  #sum"
                print >>OUTPUT, n

                for i in xrange(0,n):
                    assert(isinstance(exp[i],tuple))
                    coef = exp[i][0]
                    child_exp = exp[i][1]

                    if coef != 1.0:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %coef
                    self._print_nonlinear_terms_NL(OUTPUT, child_exp)
            else:
                for i in xrange(0,n):
                    assert(isinstance(exp[i],tuple))
                    coef = exp[i][0]
                    child_exp = exp[i][1]

                    if i != n-1:
                        # need the + op if it is not the last entry in the list
                        print >>OUTPUT, "o0  #+"

                    if coef != 1.0:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %coef
                    self._print_nonlinear_terms_NL(OUTPUT, child_exp)

        elif isinstance(exp, expr._ProductExpression):
            denom_exists = False
            if len(exp._denominator) == 0:
                pass
            else:
                print >>OUTPUT, "o3 # /"
                denom_exists = True

            if exp.coef != 1:
                print >>OUTPUT, "o2 # *"
                print >>OUTPUT, "n%s" %exp.coef

            if len(exp._numerator) == 0:
                print >>OUTPUT, "n1"

            # print out the numerator
            child_counter = 0
            max_count = len(exp._numerator)-1
            for child_exp in exp._numerator:
                if child_counter < max_count:
                    print >>OUTPUT, "o2  #*"
                self._print_nonlinear_terms_NL(OUTPUT, child_exp)
                child_counter += 1

            if denom_exists:
            # print out the denominator
                child_counter = 0
                max_count = len(exp._denominator)-1
                for child_exp in exp._denominator:
                    if child_counter < max_count:
                        print >>OUTPUT, "o2  #*"
                    self._print_nonlinear_terms_NL(OUTPUT, child_exp)
                    child_counter += 1

        elif isinstance(exp, expr._PowExpression):
            print >>OUTPUT, "o5  #^"
            for child_exp in exp._args:
                self._print_nonlinear_terms_NL(OUTPUT, child_exp)

        elif (isinstance(exp,var._VarValue) or isinstance(exp,var.Var)) and not exp.fixed_value():
            print >>OUTPUT, "v%s #%s" %(ampl_var_id[exp.name], exp.name)

        elif isinstance(exp,param._ParamValue):
            print >>OUTPUT, "n%s #%s" %(exp.value, exp.name)

        elif (isinstance(exp,numvalue.NumericConstant) or exp.fixed_value):
            print >>OUTPUT, "n%s # numeric constant" %exp.value

        else:
            raise ValueError, "Unsupported expression type in _print_nonlinear_terms_NL"
        
    def _print_ef_nonlinear_terms_NL(self, OUTPUT, exp, subproblem):
        if isinstance(exp, expr._IntrinsicFunctionExpression):
            if exp.name == 'log':
                print >>OUTPUT, "o43  #log"
            elif exp.name == 'log10':
                print >>OUTPUT, "o42  #log10"
            elif exp.name == 'sin':
                print >>OUTPUT, "o41  #sin"
            elif exp.name == 'cos':
                print >>OUTPUT, "o46  #cos"
            elif exp.name == 'tan':
                print >>OUTPUT, "o38  #tan"
            elif exp.name == 'sinh':
                print >>OUTPUT, "o40  #sinh"
            elif exp.name == 'cosh':
                print >>OUTPUT, "o45  #cosh"
            elif exp.name == 'tanh':
                print >>OUTPUT, "o37  #tanh"
            elif exp.name == 'asin':
                print >>OUTPUT, "o51  #asin"
            elif exp.name == 'acos':
                print >>OUTPUT, "o53  #acos"
            elif exp.name == 'atan':
                print >>OUTPUT, "o49  #atan"
            elif exp.name == 'exp':
                print >>OUTPUT, "o44  #exp"
            elif exp.name == 'sqrt':
                print >>OUTPUT, "o39  #sqrt"
            elif exp.name == 'asinh':
                print >>OUTPUT, "o50  #asinh"
            elif exp.name == 'acosh':
                print >>OUTPUT, "o52  #acosh"
            elif exp.name == 'atanh':
                print >>OUTPUT, "o47  #atanh"
            elif exp.name == 'pow':
                print >>OUTPUT, "o5  #^"
            else:
                logger.error("Unsupported intrinsic function (%s)", exp.name)
                raise TypeError("ASL writer does not support '%s' expressions"
                                % exp.name)

            for child_exp in exp._args:
                self._print_ef_nonlinear_terms_NL(OUTPUT, child_exp, subproblem)

        elif isinstance(exp, expr._SumExpression):
            n = len(exp._args)

            if n > 2:
                print >>OUTPUT, "o54  #sum"
                print >>OUTPUT, n

                if exp._const != 0.0:
                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "n%s" %exp._const

                for i in xrange(0,n):
                    if exp._coef[i] != 1:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %exp._coef[i]
                    self._print_ef_nonlinear_terms_NL(OUTPUT, exp._args[i], subproblem)
            else:
                if exp._const != 0.0:
                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "n%s" %exp._const

                for i in xrange(0,n-1):
                    print >>OUTPUT, "o0  #+"
                    if exp._coef[i] != 1:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %exp._coef[i]
                    self._print_ef_nonlinear_terms_NL(OUTPUT, exp._args[i], subproblem)

                if exp._coef[n-1] != 1:
                    print >>OUTPUT, "o2  #*"
                    print >>OUTPUT, "n%s" %exp._coef[n-1]
                self._print_ef_nonlinear_terms_NL(OUTPUT, exp._args[n-1], subproblem)

        elif isinstance(exp, list):
            # this is an implied summation of expressions (we did not create a new sum expression for efficiency)
            # this should be a list of tuples where [0] is the coeff and [1] is the expr to write
            n = len(exp)
            if n > 2:
                print >>OUTPUT, "o54  #sum"
                print >>OUTPUT, n

                for i in xrange(0,n):
                    assert(isinstance(exp[i],tuple))
                    coef = exp[i][0]
                    child_exp = exp[i][1]

                    if coef != 1.0:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %coef
                    self._print_ef_nonlinear_terms_NL(OUTPUT, child_exp, subproblem)
            else:
                for i in xrange(0,n):
                    assert(isinstance(exp[i],tuple))
                    coef = exp[i][0]
                    child_exp = exp[i][1]

                    if i != n-1:
                        # need the + op if it is not the last entry in the list
                        print >>OUTPUT, "o0  #+"

                    if coef != 1.0:
                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "n%s" %coef
                    self._print_ef_nonlinear_terms_NL(OUTPUT, child_exp, subproblem)

        elif isinstance(exp, expr._ProductExpression):
            denom_exists = False
            if len(exp._denominator) == 0:
                pass
            else:
                print >>OUTPUT, "o3 # /"
                denom_exists = True

            if exp.coef != 1:
                print >>OUTPUT, "o2 # *"
                print >>OUTPUT, "n%s" %exp.coef

            if len(exp._numerator) == 0:
                print >>OUTPUT, "n1"

            # print out the numerator
            child_counter = 0
            max_count = len(exp._numerator)-1
            for child_exp in exp._numerator:
                if child_counter < max_count:
                    print >>OUTPUT, "o2  #*"
                self._print_ef_nonlinear_terms_NL(OUTPUT, child_exp, subproblem)
                child_counter += 1

            if denom_exists:
            # print out the denominator
                child_counter = 0
                max_count = len(exp._denominator)-1
                for child_exp in exp._denominator:
                    if child_counter < max_count:
                        print >>OUTPUT, "o2  #*"
                    self._print_ef_nonlinear_terms_NL(OUTPUT, child_exp, subproblem)
                    child_counter += 1

        elif isinstance(exp, expr._PowExpression):
            print >>OUTPUT, "o5  #^"
            for child_exp in exp._args:
                self._print_ef_nonlinear_terms_NL(OUTPUT, child_exp, subproblem)

        elif (isinstance(exp,var._VarValue) or isinstance(exp,var.Var)) and not exp.fixed_value():
            if subproblem is tuple():
                key = subproblem[2]
                key_parts = key.split("_",1)
                tmp = key_parts[0]
                subproblem_name = tmp+"_"
                sub_vars = subproblem[1]
                tmp = exp.name.split("[")
                if tmp[0] in sub_vars:
                    subproblem_name = subproblem_name + exp.name
            else:
                subproblem_name = subproblem


            print >>OUTPUT, "v%s #%s" %(ampl_var_id[subproblem_name+exp.name], exp.name)

        elif isinstance(exp,param._ParamValue):
            print >>OUTPUT, "n%s #%s" %(exp.value, exp.name)

        elif (isinstance(exp,numvalue.NumericConstant) or exp.fixed_value):
            print >>OUTPUT, "n%s # numeric constant" %exp.value

        else:
            raise ValueError, "Unsupported expression type in _print_nonlinear_terms_NL"
        

    def _print_ef(self, model, OUTPUT):
        symbol_map = {}
        
        # linear variables
        LinearVars = set()
        LinearVarsInt = set()
        LinearVarsBool = set()
        ObjVars = set()
        ObjNonlinearVars = set()
        ObjNonlinearVarsInt = set()

        #
        # Collect statistics
        #
        Obj = model["MASTER"].active_components(Objective)
        Con = dict()
        master_vars = model["MASTER"].active_components(Var)
        subp_vars = set()
        for key in model.keys():
            Con[key] = model[key].active_components(Constraint)
            Con[key].update( model[key].active_components(ConstraintList) )
            if "MASTER" not in key:
                subp_vars.update(model[key].active_components(Var))
        sub_vars = list(subp_vars)
        del subp_vars

        Vars = dict() # will be the entire list of all vars used in the problem
        #
        # Count number of objectives and build the ampl_repns
        #
        n_objs = 0
        n_nonlinear_objs = 0
        ObjVars = set()
        ObjNonlinearVars = set()
        ObjNonlinearVarsInt = set()
        for obj in Obj:
            if Obj[obj].trivial:
                continue
            for i in Obj[obj]:
                ampl_repn = generate_ampl_repn(Obj[obj][i].expr)
                Obj[obj][i].ampl_repn = ampl_repn

                Vars.update(ampl_repn._linear_terms_var)
                Vars.update(ampl_repn._nonlinear_vars)

                for key in ampl_repn._linear_terms_var:
                    LinearVars.add(key)
                for key in ampl_repn._nonlinear_vars:
                    key_type = type(ampl_repn._nonlinear_vars[key].domain)
                    if (key_type is BooleanSet) or (key_type is IntegerSet):
                        ObjNonlinearVarsInt.add(key)
                    else:
                        ObjNonlinearVars.add(key)

                ObjVars.update(ampl_repn._linear_terms_var.keys())
                ObjVars.update(ampl_repn._nonlinear_vars.keys())
                n_objs += 1
                if ampl_repn.is_nonlinear():
                    n_nonlinear_objs += 1
        if n_objs > 1:
            raise ValueError, "asl solver has detected multiple objective functions, but currently only handles a single objective."

        #
        # Count number of constraints and build the ampl_repns
        #
        n_ranges = 0
        n_single_sided_ineq = 0
        n_equals = 0
        n_nonlinear_constraints = 0
        ConNonlinearVars = set()
        ConNonlinearVarsInt = set()
        nnz_grad_constraints = 0
        
        #
        # Handle the Master constraints
        #
        
        master_problem = Con["MASTER"]
        subproblem_names = [i for i in Con.keys() if i not in "MASTER"]
        for key, C in master_problem.iteritems():
            key_parts = key.split("_")
            tmp = key_parts[0]
            for i in xrange(len(key_parts)-1):
                if tmp in subproblem_names:
                    current_subproblem = tmp+"_"
                    break
                else:
                    tmp = "%s_%s" %(tmp,key_parts[i+1])
                    
            if C.trivial:
                continue
            for i, constraint_data in C._data.iteritems():
                ampl_repn = generate_ampl_repn(constraint_data.body)
                constraint_data.ampl_repn = ampl_repn
                if is_constant(ampl_repn):
                    continue

                for var_name in ampl_repn._linear_terms_var:
                    if var_name not in ampl_repn._nonlinear_vars:
                        tmp = var_name.split("[")
                        if tmp[0] in sub_vars:
                            Vars[current_subproblem+var_name] = ampl_repn._linear_terms_var[var_name]
                            LinearVars.add(current_subproblem+var_name)
                        else:
                            Vars[var_name] = ampl_repn._linear_terms_var[var_name]
                            LinearVars.add(var_name)
                for var_name in ampl_repn._nonlinear_vars:
                    tmp = var_name.split("[")
                    if tmp[0] in sub_vars:
                        key_type = type(ampl_repn._nonlinear_vars[var_name].domain)
                        if (key_type is BooleanSet) or (key_type is IntegerSet):
                            Vars[current_subproblem+var_name] = ampl_repn._nonlinear_vars[var_name]
                            ConNonlinearVarsInt.add(current_subproblem+var_name)
                        else:
                            Vars[current_subproblem+var_name] = ampl_repn._nonlinear_vars[var_name]
                            ConNonlinearVars.add(current_subproblem+var_name)
                    else:
                        key_type = type(ampl_repn._nonlinear_vars[var_name].domain)
                        if (key_type is BooleanSet) or (key_type is IntegerSet):
                            Vars[var_name] = ampl_repn._nonlinear_vars[var_name]
                            ConNonlinearVarsInt.add(var_name)
                        else:
                            Vars[var_name] = ampl_repn._nonlinear_vars[var_name]
                            ConNonlinearVars.add(var_name)
                        
                if ampl_repn.is_nonlinear():
                    n_nonlinear_constraints += 1

                # Merge variables from this expression
                new_vars = ampl_repn._linear_terms_var.copy()
                new_vars.update(ampl_repn._nonlinear_vars)
                nnz_grad_constraints += len(new_vars)

                L = None
                U = None
                if constraint_data.lower is not None: L = self._get_bound(constraint_data.lower)
                if constraint_data.upper is not None: U = self._get_bound(constraint_data.upper)
                if (L is None and U is None):
                    # constraint with NO bounds ???
                    raise ValueError, "Constraint " + str(con) +\
                                        "[" + str(i) + "]: lower bound = None and upper bound = None"
                elif (L is None or U is None):
                    # one sided inequality
                    n_single_sided_ineq += 1
                elif (L > U):
                    msg = 'Constraint %s[%s]: lower bound greater than upper' \
                        ' bound (%s > %s)'
                    raise ValueError, msg % (str(key), str(i), str(L), str(U) )
                elif (L == U):
                    # equality
                    n_equals += 1
                else:
                    # double sided inequality
                    # both are not none and they are valid
                    n_ranges += 1
        
        

        for subproblem in subproblem_names:
            subproblem_name = subproblem+"_"
            for key, C in Con[subproblem].iteritems():
                if C.trivial:
                    continue
                for i, constraint_data in C._data.iteritems():
                    ampl_repn = generate_ampl_repn(constraint_data.body)
                    constraint_data.ampl_repn = ampl_repn
                    if is_constant(ampl_repn):
                        continue

                    #
                    # WHEN ITERATING THROUGH THESE WE NEED TO ADD THE SUBPROBLEM NAME TO THE VAR DICTIONARY KEYS!!!
                    #
                    for var_name in ampl_repn._linear_terms_var:
                        Vars[subproblem_name+var_name] = ampl_repn._linear_terms_var[var_name]
                        LinearVars.add(subproblem_name+var_name)
                    for var_name in ampl_repn._nonlinear_vars:
                        if isinstance(ampl_repn._nonlinear_vars[var_name].domain, BooleanSet) or isinstance(ampl_repn._nonlinear_vars[var_name].domain, IntegerSet):
                            Vars[subproblem_name+var_name] = ampl_repn._nonlinear_vars[var_name]
                            ConNonlinearVarsInt.add(subproblem_name+var_name)
                        else:
                            Vars[subproblem_name+var_name] = ampl_repn._nonlinear_vars[var_name]
                            ConNonlinearVars.add(subproblem_name+var_name)

                    if ampl_repn.is_nonlinear():
                        n_nonlinear_constraints += 1

                    # Merge variables from this expression
                    new_vars = ampl_repn._linear_terms_var.copy()
                    new_vars.update(ampl_repn._nonlinear_vars)
                    nnz_grad_constraints += len(new_vars)

                    L = None
                    U = None
                    if constraint_data.lower is not None: L = self._get_bound(constraint_data.lower)
                    if constraint_data.upper is not None: U = self._get_bound(constraint_data.upper)
                    if (L is None and U is None):
                        # constraint with NO bounds ???
                        raise ValueError, "Constraint " + str(con) +\
                                         "[" + str(i) + "]: lower bound = None and upper bound = None"
                    elif (L is None or U is None):
                        # one sided inequality
                        n_single_sided_ineq += 1
                    elif (L > U):
                        msg = 'Constraint %s[%s]: lower bound greater than upper' \
                            ' bound (%s > %s)'
                        raise ValueError, msg % (str(key), str(i), str(L), str(U) )
                    elif (L == U):
                        # equality
                        n_equals += 1
                    else:
                        # double sided inequality
                        # both are not none and they are valid
                        n_ranges += 1

        LinearVars = LinearVars.difference(ObjNonlinearVars)
        LinearVars = LinearVars.difference(ObjNonlinearVarsInt)
        LinearVars = LinearVars.difference(ConNonlinearVars)
        LinearVars = LinearVars.difference(ConNonlinearVarsInt)
        var_names = LinearVars.copy()
        for var_name in var_names:
            var = Vars[var_name]
            var_type = type(var.domain)
            if var_type == IntegerSet:
                LinearVarsInt.add(var_name)
                LinearVars.discard(var_name)
            elif var_type == BooleanSet:
                L = var.lb
                U = var.ub
                if L is None or U is None:
                    raise ValueError, "Variable " + str(var.name) +\
                          "is binary, but does not have lb and ub set"
                elif value(L) == 0 and value(U) == 1:
                    LinearVarsBool.add(var_name)
                    LinearVars.discard(var_name)
                else:
                    LinearVarsInt.update(var_name)
                    LinearVars.discard(var_name)

        Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVars.intersection(ConNonlinearVars)
        Discrete_Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVarsInt.intersection(ConNonlinearVarsInt)
        ObjNonlinearVars = ObjNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVars = ConNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ObjNonlinearVarsInt = ObjNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVarsInt = ConNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)

        # put the ampl variable id into the variable
        var_id_ctr=0
        full_var_list = []
        full_var_list.extend(sorted(Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(Discrete_Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(ConNonlinearVars))
        full_var_list.extend(sorted(ConNonlinearVarsInt))
        full_var_list.extend(sorted(ObjNonlinearVars))
        full_var_list.extend(sorted(ObjNonlinearVarsInt))
        full_var_list.extend(sorted(LinearVars))
        full_var_list.extend(sorted(LinearVarsBool))
        full_var_list.extend(sorted(LinearVarsInt))
        
        for var_name in full_var_list:
            ampl_var_id[var_name] = var_id_ctr
            var_id_ctr += 1


        #
        # Print Header
        #
        # LINE 1
        #
        print >>OUTPUT,"g3 1 1 0\t# problem %s of %s" %("Extensive Form", model["MASTER"].name)
        #
        # LINE 2
        #
        print >>OUTPUT, " %s %s %s %s %s \t# vars, constraints, objectives, general inequalities, equalities  " \
            %(len(Vars), n_single_sided_ineq+n_ranges+n_equals, n_objs, n_ranges, n_equals)
        #
        # LINE 3
        #
        print >>OUTPUT, " %s %s \t# nonlinear constraints, objectives" %(n_nonlinear_constraints, n_nonlinear_objs)
        #
        # LINE 4
        #
        print >>OUTPUT, " 0 0\t# network constraints: nonlinear, linear"
        #
        # LINE 5
        #
        nlv_both = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)+len(Nonlinear_Vars_in_Objs_and_Constraints)
        print >>OUTPUT, " %s %s %s \t# nonlinear vars in constraints, objectives, both" \
        %(len(ConNonlinearVarsInt)+len(ConNonlinearVars)+nlv_both, len(ObjNonlinearVarsInt)+len(ObjNonlinearVars)+nlv_both, nlv_both)
        #
        # LINE 6
        #
        print >>OUTPUT, " 0 0 0 1\t# linear network variables; functions; arith, flags"
        #
        # LINE 7
        #
        n_int_nonlinear_b = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        n_int_nonlinear_c = len(ConNonlinearVarsInt)
        n_int_nonlinear_o = len(ObjNonlinearVarsInt)
        print >>OUTPUT, " %s %s %s %s %s \t# discrete variables: binary, integer, nonlinear (b,c,o)" \
            %(len(LinearVarsBool), len(LinearVarsInt), n_int_nonlinear_b, n_int_nonlinear_c, n_int_nonlinear_o)
        #
        # LINE 8
        #
        # objective info computed above
        print >>OUTPUT, " %s %s \t# nonzeros in Jacobian, obj. gradient" %(nnz_grad_constraints, len(ObjVars))
        #
        # LINE 9
        #
        print >>OUTPUT, " 0 0\t# max name lengths: constraints, variables"
        #
        # LINE 10
        #
        print >>OUTPUT, " 0 0 0 0 0\t# common exprs: b,c,o,c1,o1"
        #
        # "C" lines
        #
        nc = 0
        stack_lin = list()
        stack_nonlin = list()
        cu = [0 for i in xrange(len(Vars))]

        for key, C in Con["MASTER"].iteritems():
            if C.trivial:
                continue
            for ndx, constraint_data in C._data.iteritems():
                ampl_repn = constraint_data.ampl_repn
                if is_constant(ampl_repn):
                    continue

                if ampl_repn.is_linear():
                    stack_lin.append(("MASTER", key,ndx))
                else:
                    stack_nonlin.append(("MASTER", key,ndx))
                    print >>OUTPUT, "C%s\t#%s %s[%s]" %(nc, "MASTER", key, ndx)
                    nc += 1

                    assert(not ampl_repn._nonlinear_expr is None)
                    self._print_ef_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr, ("MASTER",sub_vars, key))

        for subproblem in subproblem_names:
            subproblem_name = subproblem+"_"
            for key, C in Con[subproblem].iteritems():
                if C.trivial:
                    continue
                for ndx, constraint_data in C._data.iteritems():
                    ampl_repn = constraint_data.ampl_repn
                    if is_constant(ampl_repn):
                        continue

                    if ampl_repn.is_linear():
                        stack_lin.append((subproblem, key,ndx))
                    else:
                        stack_nonlin.append((subproblem, key,ndx))
                        print >>OUTPUT, "C%s\t#%s %s[%s]" %(nc, subproblem, key, ndx)
                        nc += 1

                        assert(not ampl_repn._nonlinear_expr is None)
                        self._print_ef_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr, subproblem_name)
                


        for (problem,key,ndx) in stack_lin:
            print >>OUTPUT, "C%s\t#%s %s[%s]" %(nc,problem,key,ndx)
            nc += 1
            print >>OUTPUT, "n0"


        #
        # "O" lines
        #
        no = 0
        for key in Obj:
            k = 0
            if Obj[key].sense == maximize:
                k = 1
            for ndx in Obj[key]:
                ampl_repn = Obj[key][ndx].ampl_repn
                if ampl_repn is None:
                    continue
                if ampl_repn.is_constant():
                    pass
#                    continue
                print >>OUTPUT, "O%s %s\t#%s[%s]" %(no, k, key, ndx)
                no += 1

                if ampl_repn.is_linear():
                    print >>OUTPUT, "n%s" %ampl_repn._constant
                else:
                    assert(not ampl_repn._nonlinear_expr is None)
                    if ampl_repn._constant != 0.0:
                        print >>OUTPUT, "o0  #+"
                        print >>OUTPUT, "n%s" %ampl_repn._constant

                    self._print_ef_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr, "")

        #
        # "x" lines
        #
        # variable initialization
        n_var_inits = 0
        for (var_name, var) in Vars.iteritems():
            if var.value is not None:
                n_var_inits += 1
            else:
                assert(var.initial is None)

        print >>OUTPUT, "x%s" %n_var_inits
        for var_name in full_var_list:
            var = Vars[var_name]
            if var.value is not None:
                print >>OUTPUT, "%s %s # %s initial" %(ampl_var_id[var_name], var.value, var_name)

        #
        # "r" lines
        #
        print >>OUTPUT, "r"
        nc = 0
        stack_ = stack_nonlin
        stack_.extend(stack_lin)

        for (problem,key,ndx) in stack_:
            constraint_data = Con[problem][key][ndx]
            ampl_repn = constraint_data.ampl_repn
            offset = ampl_repn._constant

            if constraint_data._equality:
                print >>OUTPUT, "4 %s  # c%s %s %s" %(self._get_bound(constraint_data.lower)-offset, nc, problem, constraint_data.name)
            else:
                if constraint_data.lower is None:
                    if constraint_data.upper is None:
                        print >>OUTPUT, "3  # c%s %s" %(nc, constraint_data.name)
                    else:
                        print >>OUTPUT, "1 %s  # c%s %s %s" %(self._get_bound(constraint_data.upper)-offset, nc, problem, constraint_data.name)
                else:
                    if constraint_data.upper is None:
                        print >>OUTPUT, "2 %s  # c%s %s %s" %(self._get_bound(constraint_data.lower)-offset, nc, problem, constraint_data.name)
                    else:
                        print >>OUTPUT, "0 %s %s  # c%s %s %s" %(self._get_bound(constraint_data.lower)-offset, self._get_bound(constraint_data.upper)-offset, nc, problem, constraint_data.name)
            symbol_map["c" + str(nc)] = "%s_%s" %(problem, constraint_data.label)
            nc += 1

        #
        # "b" lines
        #
        print >>OUTPUT, "b"
        for ndx in full_var_list:
            vv = Vars[ndx]
            var = vv.var
            if isinstance(var.domain, BooleanSet):
                print >>OUTPUT, "0 0 1  # v%s  %s" %(ampl_var_id[ndx], ndx)
                symbol_map["v"+str(ampl_var_id[ndx])] = vv.label
                continue
            L = vv.lb
            U = vv.ub
            if L is not None:
                Lv = value(L)
                if U is not None:
                    Uv = value(U)
                    if Lv == Uv:
                        print >>OUTPUT, "4 %s  # v%s  %s" %(Lv, ampl_var_id[ndx], ndx)
                    else:
                        print >>OUTPUT, "0 %s %s  # v%s  %s" %(Lv, Uv, ampl_var_id[ndx], ndx)
                else:
                    print >>OUTPUT, "2 %s  # v%s  %s" %(Lv, ampl_var_id[ndx], ndx)
            elif U is not None:
                print >>OUTPUT, "1 %s  # v%s  %s" %(value(U), ampl_var_id[ndx], ndx)
            else:
                print >>OUTPUT, "3  #v%s  %s" %(ampl_var_id[ndx], ndx)
            symbol_map["v"+str(ampl_var_id[ndx])] = ndx
        #
        # "k" lines
        #
        ktot = 0
#        cu = {}
#        for i in xrange(len(Vars)):
#            cu[i] = 0
        cu = [0 for i in xrange(len(Vars))]

        for (problem,key,ndx) in stack_:
            if problem is "MASTER":
                key_parts = key.split("_")
                tmp = key_parts[0]
                for i in xrange(len(key_parts)-1):
                    if tmp in subproblem_names:
                        current_subproblem = tmp+"_"
                        break
                    else:
                        tmp = "%s_%s" %(tmp,key_parts[i+1])
                constraint_data = Con[problem][key][ndx]
                con_vars = set(constraint_data.ampl_repn._linear_terms_var.keys())
                con_vars.update(set(constraint_data.ampl_repn._nonlinear_vars.keys()))
                for d in con_vars:
                    tmp = d.split("[")
                    if tmp[0] in sub_vars:
                        cu[ampl_var_id[current_subproblem+d]] += 1
                    else:
                        cu[ampl_var_id[d]] += 1
            else:
                current_subproblem = problem+"_"
                constraint_data = Con[problem][key][ndx]
                con_vars = set(constraint_data.ampl_repn._linear_terms_var.keys())
                con_vars.update(set(constraint_data.ampl_repn._nonlinear_vars.keys()))
                for d in con_vars:
                    cu[ampl_var_id[current_subproblem+d]] += 1

        n1 = len(Vars) - 1
        print >>OUTPUT, "k%s" %n1
        ktot = 0
        for i in xrange(n1):
            ktot += cu[i]
            print >>OUTPUT, ktot

        #
        # "J" lines
        #
        nc = 0
        for (problem,key,ndx) in stack_:
            constraint_data = Con[problem][key][ndx]
            ampl_repn = constraint_data.ampl_repn
            # we should probably have this set already created in ampl_repn
            con_vars = set(ampl_repn._linear_terms_var.keys())
            con_vars.update(set(ampl_repn._nonlinear_vars.keys()))
            print >>OUTPUT, "J%s %s # %s %s" %(nc, len(con_vars), problem, constraint_data.name)
            nc += 1
            grad_entries = {}
            if problem is "MASTER":
                key_parts = key.split("_")
                tmp = key_parts[0]
                for i in xrange(len(key_parts)-1):
                    if tmp in subproblem_names:
                        current_subproblem = tmp+"_"
                        break
                    else:
                        tmp = "%s_%s" %(tmp,key_parts[i+1])

                for con_var in con_vars:
                    tmp = con_var.split("[")
                    if tmp[0] in sub_vars:
                        dict_name = current_subproblem+con_var
                    else:
                        dict_name = con_var
                    if con_var in ampl_repn._linear_terms_var:
                        grad_entries[ampl_var_id[dict_name]] = ampl_repn._linear_terms_coef[con_var]
                    else:
                        assert(con_var in ampl_repn._nonlinear_vars)
                        grad_entries[ampl_var_id[dict_name]] = 0
                sorted_keys = grad_entries.keys()
                sorted_keys.sort()
                for var_id in sorted_keys:
                    print >>OUTPUT, "%s   %s" %(var_id, grad_entries[var_id])
            else:
                current_subproblem = problem+"_"
                for con_var in con_vars:
                    if con_var in ampl_repn._linear_terms_var:
                        grad_entries[ampl_var_id[current_subproblem+con_var]] = ampl_repn._linear_terms_coef[con_var]
                    else:
                        assert(con_var in ampl_repn._nonlinear_vars)
                        grad_entries[ampl_var_id[current_subproblem+con_var]] = 0
                sorted_keys = grad_entries.keys()
                sorted_keys.sort()
                for var_id in sorted_keys:
                    print >>OUTPUT, "%s   %s" %(var_id, grad_entries[var_id])

        #
        # "G" lines
        #
        no = 0
        grad_entries = {}
        for key in Obj:
            if Obj[key].trivial:
                continue
            obj = Obj[key]
            for ndx in obj:
                ampl_repn = obj[ndx].ampl_repn
                obj_vars = set(ampl_repn._linear_terms_var.keys())
                obj_vars.update(set(ampl_repn._nonlinear_vars.keys()))
                if len(obj_vars) == 0:
                    pass
                else:
                    print >>OUTPUT, "G%s %s" %(no, len(obj_vars))
                no += 1

                for obj_var in obj_vars:
                    if obj_var in ampl_repn._linear_terms_var:
                        grad_entries[ampl_var_id[obj_var]] = ampl_repn._linear_terms_coef[obj_var]
                    else:
                        assert(obj_var in ampl_repn._nonlinear_vars)
                        grad_entries[ampl_var_id[obj_var]] = 0

        sorted_keys = grad_entries.keys()
        sorted_keys.sort()
        for var_id in sorted_keys:
            print >>OUTPUT, "%s   %s" %(var_id, grad_entries[var_id])

        return symbol_map
       

    
    def _print_model_NL(self, model, OUTPUT, verbose=False):

        # maps NL variables to the "real" variable names in the problem.
        # it's really NL variable ordering, as there are no variable names
        # in the NL format. however, we by convention make them go from
        # x0 upward.

#        start_overall_time = time.clock()

        symbol_map = {}
        
        if type(model) is dict:
            symbol_map = self._print_ef(model, OUTPUT)
            return symbol_map
        
        #
        # Collect statistics
        #
        Obj = model.active_components(Objective)
        Con = model.active_components(Constraint)
        Con.update( model.active_components(ConstraintList) )

        Vars = dict() # will be the entire list of all vars used in the problem
        # linear variables
        LinearVars = set()
        LinearVarsInt = set()
        LinearVarsBool = set()
        #
        # Count number of objectives and build the ampl_repns
        #

#        print "Generate objective representation:",
#        start_time = time.clock()

        n_objs = 0
        n_nonlinear_objs = 0
        ObjVars = set()
        ObjNonlinearVars = set()
        ObjNonlinearVarsInt = set()
        for obj in Obj:
            if Obj[obj].trivial:
                continue
            for i in Obj[obj]:
                tmp_obj = Obj[obj][i]
                ampl_repn = generate_ampl_repn(tmp_obj.expr)
                tmp_obj.ampl_repn = ampl_repn

                Vars.update(ampl_repn._linear_terms_var)
                Vars.update(ampl_repn._nonlinear_vars)

                for var_name in ampl_repn._linear_terms_var:
                    LinearVars.add(var_name)

                for key in ampl_repn._nonlinear_vars:
                    key_type = type(ampl_repn._nonlinear_vars[key].domain)
                    if (key_type is BooleanSet) or (key_type is IntegerSet):
                        ObjNonlinearVarsInt.add(key)
                    else:
                        ObjNonlinearVars.add(key)

                ObjVars.update(ampl_repn._linear_terms_var.keys())
                ObjVars.update(ampl_repn._nonlinear_vars.keys())
                n_objs += 1
                if ampl_repn.is_nonlinear():
                    n_nonlinear_objs += 1
        if n_objs > 1:
            raise ValueError, "asl solver has detected multiple objective functions, but currently only handles a single objective."

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Generate constraint repns:",
#        start_time = time.clock()

        #
        # Count number of constraints and build the ampl_repns
        #

        n_ranges = 0
        n_single_sided_ineq = 0
        n_equals = 0
        n_nonlinear_constraints = 0
        ConNonlinearVars = set()
        ConNonlinearVarsInt = set()
        nnz_grad_constraints = 0
        for key, C in Con.iteritems():
            if C.trivial:
                continue
            for i, constraint_data in C._data.iteritems():
                ampl_repn = generate_ampl_repn(constraint_data.body)
                constraint_data.ampl_repn = ampl_repn
                if is_constant(ampl_repn):
                    continue

                # Merge variables from this expression
                all_vars = ampl_repn._linear_terms_var.copy()
                all_vars.update(ampl_repn._nonlinear_vars)
                Vars.update(all_vars)
                nnz_grad_constraints += len(all_vars)

                for var_name in ampl_repn._linear_terms_var:
                    LinearVars.add(var_name)

                for var_name in ampl_repn._nonlinear_vars:
                    var_type = ampl_repn._nonlinear_vars[var_name].domain
                    if (var_type is BooleanSet) or (var_type is IntegerSet):
                        ConNonlinearVarsInt.add(var_name)
                    else:
                        ConNonlinearVars.add(var_name)

                if ampl_repn.is_nonlinear():
                    n_nonlinear_constraints += 1

                L = None
                U = None
                if constraint_data.lower is not None: L = self._get_bound(constraint_data.lower)
                if constraint_data.upper is not None: U = self._get_bound(constraint_data.upper)
                if (L is None and U is None):
                    # constraint with NO bounds ???
                    raise ValueError, "Constraint " + str(con) +\
                                         "[" + str(i) + "]: lower bound = None and upper bound = None"
                elif (L is None or U is None):
                    # one sided inequality
                    n_single_sided_ineq += 1
                elif (L > U):
                    msg = 'Constraint %s[%s]: lower bound greater than upper' \
                          ' bound (%s > %s)'
                    raise ValueError, msg % (str(key), str(i), str(L), str(U) )
                elif (L == U):
                    # equality
                    n_equals += 1
                else:
                    # double sided inequality
                    # both are not none and they are valid
                    n_ranges += 1

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Generate ampl_var_id:",
#        start_time = time.clock()
        
        LinearVars = LinearVars.difference(ObjNonlinearVars)
        LinearVars = LinearVars.difference(ObjNonlinearVarsInt)
        LinearVars = LinearVars.difference(ConNonlinearVars)
        LinearVars = LinearVars.difference(ConNonlinearVarsInt)
        var_names = LinearVars.copy()
        for var_name in var_names:
            var = Vars[var_name]
            var_type = type(var.domain)
            if var_type is IntegerSet:
                LinearVarsInt.add(var_name)
                LinearVars.discard(var_name)
            elif var_type is BooleanSet:
                L = var.lb
                U = var.ub
                if L is None or U is None:
                    raise ValueError, "Variable " + str(var.name) +\
                          "is binary, but does not have lb and ub set"
                elif value(L) == 0 and value(U) == 1:
                    LinearVarsBool.add(var_name)
                    LinearVars.discard(var_name)
                else:
                    LinearVarsInt.add(var_name)
                    LinearVars.discard(var_name)

        Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVars.intersection(ConNonlinearVars)
        Discrete_Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVarsInt.intersection(ConNonlinearVarsInt)
        ObjNonlinearVars = ObjNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVars = ConNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ObjNonlinearVarsInt = ObjNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVarsInt = ConNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        

        # put the ampl variable id into the variable
        var_id_ctr=0
        full_var_list = []
        full_var_list.extend(sorted(Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(Discrete_Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(ConNonlinearVars))
        full_var_list.extend(sorted(ConNonlinearVarsInt))
        full_var_list.extend(sorted(ObjNonlinearVars))
        full_var_list.extend(sorted(ObjNonlinearVarsInt))
        full_var_list.extend(sorted(LinearVars))
        full_var_list.extend(sorted(LinearVarsBool))
        full_var_list.extend(sorted(LinearVarsInt))

        for var_name in full_var_list:
            ampl_var_id[var_name] = var_id_ctr
            var_id_ctr += 1

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing NL file header:",
#        start_time = time.clock()
        #
        # Print Header
        #
        # LINE 1
        #
        print >>OUTPUT,"g3 1 1 0\t# problem %s" %model.name
        #
        # LINE 2
        #
        print >>OUTPUT, " %s %s %s %s %s \t# vars, constraints, objectives, general inequalities, equalities  " \
            %(len(Vars), n_single_sided_ineq+n_ranges+n_equals, n_objs, n_ranges, n_equals)
        #
        # LINE 3
        #
        print >>OUTPUT, " %s %s \t# nonlinear constraints, objectives" %(n_nonlinear_constraints, n_nonlinear_objs)
        #
        # LINE 4
        #
        print >>OUTPUT, " 0 0\t# network constraints: nonlinear, linear"
        #
        # LINE 5
        #
        nlv_both = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)+len(Nonlinear_Vars_in_Objs_and_Constraints)
        print >>OUTPUT, " %s %s %s \t# nonlinear vars in constraints, objectives, both" \
        %(len(ConNonlinearVarsInt)+len(ConNonlinearVars)+nlv_both, len(ObjNonlinearVarsInt)+len(ObjNonlinearVars)+nlv_both, nlv_both)
             
        #
        # LINE 6
        #
        print >>OUTPUT, " 0 0 0 1\t# linear network variables; functions; arith, flags"
        #
        # LINE 7
        #
        n_int_nonlinear_b = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        n_int_nonlinear_c = len(ConNonlinearVarsInt)
        n_int_nonlinear_o = len(ObjNonlinearVarsInt) 
        print >>OUTPUT, " %s %s %s %s %s \t# discrete variables: binary, integer, nonlinear (b,c,o)" \
            %(len(LinearVarsBool), len(LinearVarsInt), n_int_nonlinear_b, n_int_nonlinear_c, n_int_nonlinear_o)
        #
        # LINE 8
        #
        # objective info computed above
        print >>OUTPUT, " %s %s \t# nonzeros in Jacobian, obj. gradient" %(nnz_grad_constraints, len(ObjVars))
        #
        # LINE 9
        #
        print >>OUTPUT, " 0 0\t# max name lengths: constraints, variables"
        #
        # LINE 10
        #
        print >>OUTPUT, " 0 0 0 0 0\t# common exprs: b,c,o,c1,o1"

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing constraints:",
#        start_time = time.clock()

        #
        # "C" lines
        #
        nc = 0
        stack_lin = list()
        stack_nonlin = list()

        cu = [0 for i in xrange(len(Vars))]
        
        for key, C in Con.iteritems():
            if C.trivial:
                continue
            for ndx, constraint_data in C._data.iteritems():
                ampl_repn = constraint_data.ampl_repn
                if is_constant(ampl_repn):
                    continue

                if ampl_repn.is_linear():
                    stack_lin.append((key,ndx))
                else:
                    stack_nonlin.append((key,ndx))
                    print >>OUTPUT, "C%s\t#%s[%s]" %(nc, key, ndx)
                    nc += 1

                    assert(not ampl_repn._nonlinear_expr is None)
                    self._print_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr)

                con_vars = set(constraint_data.ampl_repn._linear_terms_var.keys())
                con_vars.update(set(constraint_data.ampl_repn._nonlinear_vars.keys()))
                for d in con_vars:
                    cu[ampl_var_id[d]] += 1



        for (key,ndx) in stack_lin:
            print >>OUTPUT, "C%s\t#%s[%s]" %(nc,key,ndx)
            nc += 1
            print >>OUTPUT, "n0"

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing objective:",
#        start_time = time.clock()
        #
        # "O" lines
        #
        no = 0
        for key in Obj:
            k = 0
            if Obj[key].sense == maximize:
                k = 1
            for ndx in Obj[key]:
                ampl_repn = Obj[key][ndx].ampl_repn
                if ampl_repn is None:
                    continue
                if ampl_repn.is_constant():
                    pass
                print >>OUTPUT, "O%s %s\t#%s[%s]" %(no, k, key, ndx)
                no += 1

                if ampl_repn.is_linear():
                    print >>OUTPUT, "n%s" %ampl_repn._constant
                else:
                    assert(not ampl_repn._nonlinear_expr is None)
                    if ampl_repn._constant != 0.0:
                        print >>OUTPUT, "o0  #+"
#                        print >>OUTPUT, "o0"  #+"
                        print >>OUTPUT, "n%s" %ampl_repn._constant

                    self._print_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr)

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing intializations:",
#        start_time = time.clock()
        #
        # "x" lines
        #
        # variable initialization
        ##n_var_inits = 0
        ##tmp_list = []
        ##for (var_name, var) in Vars.iteritems():
        ##    if var.value is not None:
        ##        n_var_inits += 1
        ##        tmp_list.append(var_name)
        ##
        ##print >>OUTPUT, "x%s" % n_var_inits
        ##for var_name in tmp_list:
        ##    var = Vars[var_name]
        ##    print >>OUTPUT, "%s %s # %s initial" %(ampl_var_id[var_name], var.value, var_name)
        ##del tmp_list

        # This does the same thing .. but it ensures a consistent order on different platforms.
        # This might be a bit slower, though...
        tmp_map = {}
        for (var_name, var) in Vars.iteritems():
            if var.value is not None:
                tmp_map[ampl_var_id[var_name]] = var_name

        print >>OUTPUT, "x%s" % len(tmp_map)
        for id in sorted(tmp_map.keys()):
            var_name = tmp_map[id]
            var = Vars[var_name]
            print >>OUTPUT, "%s %s # %s initial" %(id, var.value, var_name)
        
#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing constraint bounds:",
#        start_time = time.clock()
        #
        # "r" lines
        #
        print >>OUTPUT, "r"
        nc = 0
        stack_ = stack_nonlin
        stack_.extend(stack_lin)

        for (key,ndx) in stack_:
            constraint_data = Con[key][ndx]
            ampl_repn = constraint_data.ampl_repn

            offset = ampl_repn._constant

            if constraint_data._equality:
#                print >>OUTPUT, 4, self._get_bound(constraint_data.lower)-offset  # c%s %s" %(self._get_bound(constraint_data.lower)-offset, nc, constraint_data.name)
                print >>OUTPUT, "4 %s  # c%s %s" %(self._get_bound(constraint_data.lower)-offset, nc, constraint_data.name)
            else:
                if constraint_data.lower is None:
                    if constraint_data.upper is not None:
                        print >>OUTPUT, "1 %s  # c%s %s" %(self._get_bound(constraint_data.upper)-offset, nc, constraint_data.name)
#                        print >>OUTPUT, 1, self._get_bound(constraint_data.upper)-offset
                    else:
                        print >>OUTPUT, "3  # c%s %s" %(nc, constraint_data.name)
#                        print >>OUTPUT, 3
                else:
                    if constraint_data.upper is None:
                        print >>OUTPUT, "2 %s  # c%s %s" %(self._get_bound(constraint_data.lower)-offset, nc, constraint_data.name)
#                        print >>OUTPUT, 2, self._get_bound(constraint_data.lower)-offset
                    else:
                        print >>OUTPUT, "0 %s %s  # c%s %s" %(self._get_bound(constraint_data.lower)-offset, self._get_bound(constraint_data.upper)-offset, nc, constraint_data.name)
#                        print >>OUTPUT, 0, self._get_bound(constraint_data.lower)-offset, self._get_bound(constraint_data.upper)-offset
            symbol_map["c" + str(nc)] = constraint_data.label 
            nc += 1


#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing variable bounds:",
#        start_time = time.clock()
        #
        # "b" lines
        #
        print >>OUTPUT, "b"
        for ndx in full_var_list:
            vv = Vars[ndx]
            var = vv.var
            name = vv.name
            if isinstance(var.domain, BooleanSet):
#                print >>OUTPUT, "0 0 1"  # v%s  %s" %(ampl_var_id[name], name)
                print >>OUTPUT, "0 0 1  # v%s  %s" %(ampl_var_id[name], name)
                symbol_map["v"+str(ampl_var_id[name])] = vv.label
                continue
            L = vv.lb
            U = vv.ub
            if L is not None:
                Lv = value(L)
                if U is not None:
                    Uv = value(U)
                    if Lv == Uv:
#                        print >>OUTPUT, 4, Lv
                        print >>OUTPUT, "4 %s  # v%s  %s" %(Lv, ampl_var_id[name], name)
                    else:
#                        print >>OUTPUT, 0, Lv, Uv
                        print >>OUTPUT, "0 %s %s  # v%s  %s" %(Lv, Uv, ampl_var_id[name], name)
                else:
#                    print >>OUTPUT, 2, Lv
                    print >>OUTPUT, "2 %s  # v%s  %s" %(Lv, ampl_var_id[name], name)
            elif U is not None:
#                print >>OUTPUT, 1, value(U)
                print >>OUTPUT, "1 %s  # v%s  %s" %(value(U), ampl_var_id[name], name)
            else:
#                print >>OUTPUT, 3  #v%s  %s" %(ampl_var_id[name], name)
                print >>OUTPUT, "3  #v%s  %s" %(ampl_var_id[name], name)
            symbol_map["v"+str(ampl_var_id[name])] = vv.label

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing k's:",
#        start_time = time.clock()        

        #
        # "k" lines
        #
        ktot = 0
        n1 = len(Vars) - 1
        print >>OUTPUT, "k%s" %n1
        ktot = 0
        for i in xrange(n1):
            ktot += cu[i]
            print >>OUTPUT, ktot

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing Jacobian's:",
#        start_time= time.clock()

        #
        # "J" lines
        # 
        nc = 0
        for (key,ndx) in stack_:
            constraint_data = Con[key][ndx]
            ampl_repn = constraint_data.ampl_repn
            # we should probably have this set already created in ampl_repn
            con_vars = set(ampl_repn._linear_terms_var.iterkeys())
            con_vars.update(ampl_repn._nonlinear_vars.iterkeys())
            
#            print >>OUTPUT, "J%s %s" %(nc, len(con_vars))
            print >>OUTPUT, "J%s %s  #  %s" %(nc, len(con_vars), constraint_data.name)
            nc += 1
            
            
            grad_entries = {}
            for con_var in con_vars:
                if con_var in ampl_repn._linear_terms_var:
                    grad_entries[ampl_var_id[con_var]] = ampl_repn._linear_terms_coef[con_var]
                else:
                    grad_entries[ampl_var_id[con_var]] = 0

            sorted_keys = grad_entries.keys()
            sorted_keys.sort()
            for var_id in sorted_keys:
                print >>OUTPUT, var_id, grad_entries[var_id]

#        end_time = time.clock()
#        print (end_time - start_time)

 #       print "Printing objective gradient:",
 #       start_time = time.clock()
        #
        # "G" lines
        #
        no = 0
        grad_entries = {}
        for key in Obj:
            if Obj[key].trivial:
                continue
            obj = Obj[key]
            for ndx in obj:
                ampl_repn = obj[ndx].ampl_repn
                obj_vars = set(ampl_repn._linear_terms_var.keys())
                obj_vars.update(set(ampl_repn._nonlinear_vars.keys()))
                if len(obj_vars) == 0:
                    pass
                else:
                    print >>OUTPUT, "G%s %s" %(no, len(obj_vars))
                no += 1

                for obj_var in obj_vars:
                    if obj_var in ampl_repn._linear_terms_var:
                        grad_entries[ampl_var_id[obj_var]] = ampl_repn._linear_terms_coef[obj_var]
                    else:
                        assert(obj_var in ampl_repn._nonlinear_vars)
                        grad_entries[ampl_var_id[obj_var]] = 0

        sorted_keys = grad_entries.keys()
        sorted_keys.sort()
        for var_id in sorted_keys:
            print >>OUTPUT, var_id, grad_entries[var_id]
#            print >>OUTPUT, "%s   %s" %(var_id, grad_entries[var_id])

#        print (end_time - start_time)
#        end_overall_time = time.clock()
#        print "Total time:",end_overall_time-start_overall_time

        return symbol_map

class ampl_representation:
    def __init__(self):
        self._constant = 0
        self._linear_terms_var = {}
        self._linear_terms_coef = {}
        self._nonlinear_expr = None
        self._nonlinear_vars = {}

    def clone(self):
        clone = ampl_representation()
        clone._constant = self.constant
        clone._linear_terms_var = self._linear_terms_var
        clone._linear_terms_coef = self._linear_terms_coef
        clone._nonlinear_expr = self._nonlinear_expr
        clone._nonlinear_vars = self._nonlinear_vars
        return clone

    def is_constant(self):
        if len(self._linear_terms_var) == 0 and self._nonlinear_expr is None:
            return True
        return False

    def is_linear(self):
        if self._nonlinear_expr is None:
            assert(len(self._nonlinear_vars) == 0)
            return True

    def is_nonlinear(self):
        if not self._nonlinear_expr is None:
            return True
        return False

    def needs_sum(self):
        num_components = 0
        if self._constant != 0:
            num_components += 1

        num_components += len(self._linear_terms_var)

        if not self._nonlinear_expr is None:
            num_components += 1

        if num_components > 1:
            return True
        return False

    def create_expr(self):
        if self.needs_sum() == True:
            ret_expr = expr._SumExpression()
            if self.is_constant():
                ret_expr._const = self._constant

            for (var_name, var) in self._linear_terms_var.iteritems():
                ret_expr.add(self._linear_terms_coef[var_name], var)

            if self.is_nonlinear():
                ret_expr.add(1.0, self._nonlinear_expr)

            return ret_expr
        else:
            # we know there is only one component present in ampl_repn
            if self.is_constant():
                return as_numeric(self._constant)
            elif self.is_nonlinear():
                return self._nonlinear_expr
            else:
                assert( len(self._linear_terms_var) == 1 )
                return self._linear_terms_var[self._linear_terms_var.keys()[0]]



def generate_ampl_repn(exp):
    ampl_repn = ampl_representation()

    #
    # Expression
    #
    if isinstance(exp,expr.Expression):
        exp_type = type(exp)

        #
        # Sum
        #
        if exp_type is expr._SumExpression:
            ampl_repn._constant = float(exp._const)
            ampl_repn._nonlinear_expr = None
            for i in xrange(len(exp._args)):
                exp_coef = exp._coef[i]
                child_repn = generate_ampl_repn(exp._args[i])
                # adjust the constant
                ampl_repn._constant += exp_coef*child_repn._constant

                # adjust the linear terms
                for (var_name,var) in child_repn._linear_terms_var.iteritems():
                    if var_name in ampl_repn._linear_terms_var:
                        ampl_repn._linear_terms_coef[var_name] += exp_coef*child_repn._linear_terms_coef[var_name]
                    else:
                        ampl_repn._linear_terms_var[var_name] = var
                        ampl_repn._linear_terms_coef[var_name] = exp_coef*child_repn._linear_terms_coef[var_name]

                # adjust the nonlinear terms
                if not child_repn._nonlinear_expr is None:
                    if ampl_repn._nonlinear_expr is None:
                        ampl_repn._nonlinear_expr = [(exp_coef, child_repn._nonlinear_expr)]
                    else:
                        assert(len(ampl_repn._nonlinear_expr) > 0)
                        ampl_repn._nonlinear_expr.append((exp_coef, child_repn._nonlinear_expr))

                # adjust the nonlinear vars
                ampl_repn._nonlinear_vars.update(child_repn._nonlinear_vars)

            return ampl_repn

        #
        # Product
        #
        elif exp_type is expr._ProductExpression:
            #
            # Iterate through the denominator.  If they aren't all constants, then
            # simply return this expresion.
            #
            denom=1.0
            for e in exp._denominator:
                if e.fixed_value():
                    #print 'Z',type(e),e.fixed
                    denom *= e.value
                elif e.is_constant():
                    denom *= e()
                else:
                    ampl_repn._nonlinear_expr = exp
                    break
                if denom == 0.0:
                    print "Divide-by-zero error - offending sub-expression:"
                    e.pprint()
                    raise ZeroDivisionError

            if not ampl_repn._nonlinear_expr is None:
                # we have a nonlinear expression ... build up all the vars
                for e in exp._denominator:
                    arg_repn = generate_ampl_repn(e)
                    ampl_repn._nonlinear_vars.update(arg_repn._linear_terms_var)
                    ampl_repn._nonlinear_vars.update(arg_repn._nonlinear_vars)

                for e in exp._numerator:
                    arg_repn = generate_ampl_repn(e)
                    ampl_repn._nonlinear_vars.update(arg_repn._linear_terms_var)
                    ampl_repn._nonlinear_vars.update(arg_repn._nonlinear_vars)
                return ampl_repn

            #
            # OK, the denominator is a constant.
            #
            # build up the ampl_repns for the numerator
            n_linear_args = 0
            n_nonlinear_args = 0
            arg_repns = list()
            for i in xrange(len(exp._numerator)):
                e = exp._numerator[i]
                e_repn = generate_ampl_repn(e)
                arg_repns.append(e_repn)
                if e_repn.is_nonlinear():
                    n_nonlinear_args += 1
                elif not e_repn.is_constant():
                    n_linear_args += 1

            is_nonlinear = False
            if n_linear_args > 1 or n_nonlinear_args > 0:
                is_nonlinear = True


            if is_nonlinear == True:
                # do like AMPL and simply return the expression
                # without extracting the potentially linear part
                ampl_repn = ampl_representation()
                ampl_repn._nonlinear_expr = exp
                for repn in arg_repns:
                    ampl_repn._nonlinear_vars.update(repn._linear_terms_var)
                    ampl_repn._nonlinear_vars.update(repn._nonlinear_vars)
                return ampl_repn

            else: # is linear or constant
                ampl_repn = current_repn = arg_repns[0]
                for i in xrange(1,len(arg_repns)):
                    e_repn = arg_repns[i]
                    ampl_repn = ampl_representation()

                    # const_c * const_e
                    ampl_repn._constant = current_repn._constant * e_repn._constant

                    # const_e * L_c
                    if e_repn._constant != 0.0:
                        for (var_name, var) in current_repn._linear_terms_var.iteritems():
                            ampl_repn._linear_terms_coef[var_name] = current_repn._linear_terms_coef[var_name] * e_repn._constant
                            ampl_repn._linear_terms_var[var_name] = var

                    # const_c * L_e
                    if current_repn._constant != 0.0:
                        for (e_var_name,e_var) in e_repn._linear_terms_var.iteritems():
                            if e_var_name in ampl_repn._linear_terms_var:
                                ampl_repn._linear_terms_coef[e_var_name] += current_repn._constant * e_repn._linear_terms_coef[e_var_name]
                            else:
                                ampl_repn._linear_terms_coef[e_var_name] = current_repn._constant * e_repn._linear_terms_coef[e_var_name]
                                ampl_repn._linear_terms_var[e_var_name] = e_var

                current_repn = ampl_repn

            # now deal with the product expression's coefficient that needs
            # to be applied to all parts of the ampl_repn
            ampl_repn._constant *= exp.coef/denom
            for var_name in ampl_repn._linear_terms_coef:
                ampl_repn._linear_terms_coef[var_name] *= exp.coef/denom
            assert(ampl_repn._nonlinear_expr is None)
            assert(len(ampl_repn._nonlinear_vars) == 0)

            return ampl_repn

        #
        # Power Expressions
        #
        elif exp_type is expr._PowExpression:
            assert(len(exp._args) == 2)
            base_repn = generate_ampl_repn(exp._args[0])
            exponent_repn = generate_ampl_repn(exp._args[1])

            if base_repn.is_constant() and exponent_repn.is_constant():
                ampl_repn._constant = base_repn._constant**exponent_repn._constant
            elif exponent_repn.is_constant() and exponent_repn._constant == 1.0:
                # not sure if this is necessary (may be able to just return base_repn
                ampl_repn = base_repn.clone()
            elif exponent_repn.is_constant() and exponent_repn._constant == 0.0:
                ampl_repn._constant = 1.0
            else:
                # instead, let's just return the expression we are given and only
                # use the ampl_repn for the vars
                ampl_repn._nonlinear_expr = exp
                ampl_repn._nonlinear_vars = base_repn._nonlinear_vars
                ampl_repn._nonlinear_vars.update(exponent_repn._nonlinear_vars)
                ampl_repn._nonlinear_vars.update(base_repn._linear_terms_var)
                ampl_repn._nonlinear_vars.update(exponent_repn._linear_terms_var)

            return ampl_repn

        #
        # Intrinsic Functions
        #
        elif exp_type is expr._IntrinsicFunctionExpression:
            assert(len(exp._args) == 1)

            # this is inefficient since it is using much more than what we need
            child_repn = generate_ampl_repn(exp._args[0])

            ampl_repn._nonlinear_expr = exp
            ampl_repn._nonlinear_vars = child_repn._nonlinear_vars
            ampl_repn._nonlinear_vars.update(child_repn._linear_terms_var)
            return ampl_repn
        #
        # ERROR
        #
        else:
            raise ValueError, "Unsupported expression type: "+str(exp)
    #
    # Constant
    #
    elif exp.fixed_value():
        ampl_repn._constant = float(exp.value)
        return ampl_repn

    #
    # Variable
    #
    elif type(exp) is _VarValue or exp.type() is Var:
        ampl_repn._linear_terms_coef = {exp.name: 1.0}
        ampl_repn._linear_terms_var = {exp.name: exp}
        return ampl_repn

    #
    # recurse to the bottom of the identity expression
    #
    elif isinstance(exp, expr._IdentityExpression):
        while isinstance(exp, expr._IdentityExpression):
            exp = exp._args[0]
    #
    # ERROR
    #
    else:
        raise ValueError, "Unexpected expression type: "+str(exp)
