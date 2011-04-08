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
# Problem Writer for CPLEX LP Format Files
#

import math

from coopr.opt import ProblemFormat
from coopr.opt.base import AbstractProblemWriter
from coopr.pyomo.base import BooleanSet, Constraint, expr, IntegerSet
from coopr.pyomo.base import Objective, NumericConstant, SOSConstraint, Var
from coopr.pyomo.base import VarStatus, value
from coopr.pyomo.base.numtypes import minimize, maximize
from coopr.pyomo.expr import is_constant, is_nonlinear, is_quadratic

from pyutilib.component.core import alias
from pyutilib.misc import deprecated


def convert_name(namestr):
    
    return namestr.replace('[','(').replace(']',')')

class ProblemWriter_cpxlp(AbstractProblemWriter):

    alias('cpxlp')
    alias('lp')

    def __init__(self):
        
        AbstractProblemWriter.__init__(self,ProblemFormat.cpxlp)

        # temporarily placing attributes used in extensive-form writing
        # here, for eventual migration to the base class.
        self._output_objectives = True
        self._output_constraints = True
        self._output_variables = True
            # means we're outputting *some* variables - types determined by
            # following flags.

        # building on the above, partition out the variables that should
        # be written if the _output_variables attribute is set to True.
        # this is useful when writing components of multiple models to a
        # single LP file. unfortunately, the CPLEX LP format requires all
        # integer and binary (and continuous) variables to appear in a
        # single continuous block.
        #
        # SOS constraints must come after Bounds, General, Binary, and
        # Semi-Continuous sections
        #
        self._output_continuous_variables = True
        self._output_integer_variables = True
        self._output_binary_variables = True

        # do I pre-pend the model name to all identifiers I output?
        # useful in cases where you are writing components of multiple
        # models to a single output LP file.
        self._output_prefixes = False


    def __call__(self, model, filename):
        
        if filename is None:
           filename = model.name + ".lp"
        OUTPUT=open(filename,"w")
        symbol_map = self._print_model_LP(model,OUTPUT)
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


    @staticmethod
    def _collect_key ( a ):
        
        return a[0]


    @staticmethod
    def _no_label_error ( var ):
        
        msg  = "Unable to find label for variable '%s'.\n"                    \
        'Possibly uninstantiated model.  Do any constraint or objective  '     \
        'rules reference the original model object, as opposed to the  '     \
        'passed model object? Alternatively, if you are developing code, '     \
        'has the model instance been pre-processed?'

        raise ValueError, msg % str(var)


    def _print_expr_linear(self, x, OUTPUT, **kwargs):
        
        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo linear encoding of an expression to write in LP format

        optional keyword arguments:
          is_objective: set True if printing a quadratic objective.  Required
             for CPlex LP quadratic handling differences between objectives
             and constraints. (boolean)

          print_offset: print expression offset [deprecated] (boolean)
        """

        is_objective = kwargs.pop('is_objective', False)
        print_offset = kwargs.pop('print_offset', False)

        constant_term = x[0]
        linear_terms = x[1]

        name_to_coefficient_map = {}

        for coefficient, var_value in linear_terms:

           if var_value.fixed is True:

              constant_term += (coefficient * var_value.value)

           else:

              prefix = ""
              if self._output_prefixes is True:
                 parent_var = var_value.var
                 prefix = convert_name(parent_var.model.name) + "_"

              if not var_value.label:
                 self._no_label_error(var_value)

              name = prefix + convert_name(var_value.label)

              # due to potential disabling of expression simplification,
              # variables might appear more than once - condense coefficients.
              name_to_coefficient_map[name] = coefficient + name_to_coefficient_map.get(name,0.0)

        sorted_names = sorted(name_to_coefficient_map.keys())

        for name in sorted_names:
     
           coefficient = name_to_coefficient_map[name]

           sign = '+'
           if coefficient < 0: sign = '-'
           print >>OUTPUT, '%s%f %s' % (sign, math.fabs(coefficient), name)

        if print_offset and (constant_term != 0.0):
            sign = '+'
            if constant_term < 0: sign = '-'
            print >>OUTPUT, '%s%f %s' % (sign, math.fabs(constant_term), 'ONE_VAR_CONSTANT')

        return constant_term


    def _print_expr_canonical(self, x, OUTPUT, **kwargs):
        
        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo canonical expression to write in LP format

        optional keyword arguments:
          is_objective: set True if printing a quadratic objective.  Required
             for CPlex LP quadratic handling differences between objectives
             and constraints. (boolean)

          print_offset: print expression offset [deprecated] (boolean)
        """

        is_objective = kwargs.pop('is_objective', False)
        print_offset = kwargs.pop('print_offset', False)

        #
        # Linear
        #
        if 1 in x:

           var_hashes = x[1].keys()

           name_to_coefficient_map = {}

           for this_hash in var_hashes:

              var_value = x[-1][this_hash.keys()[0]]
              coefficient = x[1][this_hash]

              prefix = ""

              if self._output_prefixes is True:
                 parent_var = var_value.var
                 prefix = convert_name(parent_var.model.name) + "_"

              label = var_value.label
              if not label:
                 self._no_label_error(var_value)
  
              name = prefix + convert_name(label)              

              name_to_coefficient_map[name] = coefficient

           sorted_names = sorted(name_to_coefficient_map.keys())
   
           for name in sorted_names:           
              coef = name_to_coefficient_map[name]
              sign = '+'
              if coef < 0: sign = '-'
              print >>OUTPUT, '%s%f %s' % (sign, math.fabs(coef), name)

        #
        # Quadratic
        #
        if 2 in x:

            print >>OUTPUT, "+ ["

            for id in sorted(x[2].keys()):

                coefficient = x[2][id]
                sign = '+'
                if coefficient < 0: 
                   sign = '-'
                   coefficient = math.fabs(coefficient)

                if is_objective:
                    coefficient *= 2
                # times 2 because LP format requires /2 for all the quadratic
                # terms /of the objective only/.  Discovered the last bit thru
                # trial and error.  Obnoxious.
                # Ref: ILog CPlex 8.0 User's Manual, p197.

                print >>OUTPUT, sign, coefficient,

                term_variables = []
                
                for var in id:

                    var_value = x[-1][var]
                    
                    label = var_value.label
                    if not label:
                        self._no_label_error(var_value)

                    prefix = ""

                    if self._output_prefixes is True:
                       parent_var = var_value.var
                       prefix = convert_name(parent_var.model.name) + "_"                        

                    name = prefix + convert_name(label) 
                    term_variables.append(name)

                if len(term_variables) == 2:
                   print >>OUTPUT, term_variables[0],"*",term_variables[1],
                else:
                   print >>OUTPUT, term_variables[0],"^ 2",
                
            print >>OUTPUT, ""

            print >>OUTPUT, "]",
            if is_objective:
                print >>OUTPUT, ' / 2'
                # divide by 2 because LP format requires /2 for all the quadratic
                # terms.  Weird.  Ref: ILog CPlex 8.0 User's Manual, p197
            else:
               print >>OUTPUT, ""


        #
        # Constant offset
        #
        offset=0.0
        if 0 in x:
            offset = x[0][None]
        if print_offset and offset != 0.0:
            sign = '+'
            if offset < 0: sign = '-'
            print >>OUTPUT, '%s%f %s' % (sign, math.fabs(offset), 'ONE_VAR_CONSTANT')

        #
        # Return constant offset
        #
        return offset


#    @deprecated
    def _print_quadterm(self, x, is_minimizing, OUTPUT):
        
        # The LP format doesn't allow for expression of constant terms in the
        # objective.  A work-around involves tracking the sum of constant terms
        # in the quadratic quadratic terms, and then writing that out with a
        # dummy variable forced equal to one.
        print >>OUTPUT, ""
        for arg in x._args:
            if isinstance(arg,expr._ProductExpression):
                # NOTE: We need to handle quadratics defined with the 'pow'
                # term here.
                # WARNING: The following code is very specific to progressive
                # hedging, with a very specific format assumed.  We do need to
                # handle more general expressions, but we'll worry about that
                # at a latter time.
                blend = arg._numerator[0]()

                if blend is 1:

                   rho = arg._numerator[1]()

                   pow_expression = arg._numerator[2]

                   base = pow_expression._args[0]
                   exponent = pow_expression._args[1]

                   if not isinstance(base,expr._SumExpression):
                       msg = 'Quadratic term base must be a _SumExpression'
                       raise ValueError, msg

                   if not isinstance(exponent,NumericConstant):
                       msg = 'Quadratic term exponent must be a NumericConstant'
                       raise ValueError, msg

                   variable = base._args[0]
                   offset = base._args[1]
                   if variable.status is not VarStatus.unused:

                      sign = '-'
                      if is_minimizing is True:
                          sign = '+'
                      print >>OUTPUT, '%s [ %s %s^2 ] / 2' % (
                        sign,
                        str(rho),
                        convert_name(variable.label)
                      )

                      sign = '-'
                      if (is_minimizing is True) == (offset.value <  0):
                          sign = '+'
                      print >>OUTPUT, '%s %s %s' % (
                         sign,
                         str(abs(rho*offset.value)),
                         convert_name( variable.label )
                      )

                      objective_offset = (rho * offset.value*offset.value /2.0)
                      fmt = ' -%s ONE_VAR_CONSTANT'
                      if is_minimizing is True: fmt = ' +%s ONE_VAR_CONSTANT'
                      print >>OUTPUT, fmt % str(objective_offset)

            elif isinstance(arg,NumericConstant):
                # this is the "0.0" element that forms the initial expression
                # -- the quadratic sub-expressions aren't known to the presolve
                # routines. ideally unnecessary - hacked in for now.
                pass

            else:
                msg = '%s\nUnknown expression sub-type found in quadratic '   \
                      'objective expression'
                raise ValueError, msg % `arg`


    @staticmethod
    def printSOS(con, name, OUTPUT, index=None):
        
        """
        Returns the SOS constraint (as a string) associated with con.
        If specified, index is passed to con.sos_set().

        Arguments:
        con    The SOS constraint object
        name   The name of the variable
        OUTPUT The output stream
        index  [Optional] the index to pass to the sets indexing the variables.
        """

        # The name of the variable being indexed
        varName = str(con.sos_vars())

        # The list of variable names to be printed, including indices
        varNames = []

        # Get all the variables
        if index is None:
            tmpSet = con.sos_set()
        else:
            tmpSet = con.sos_set()[index]
        for x in tmpSet:
            strX = str(x)
            if strX[0] == "(":
                # its a tuple, remove whitespace
                varNames.append(varName + strX.replace(" ",""))
            else:
                # its a single number, add parenthesis
                varNames.append(varName + "(" + strX + ")")

        conNameIndex = ""
        if index is not None:
            conNameIndex = str(index)

        print >>OUTPUT, '%s%s: S%s::' % (name, conNameIndex, con.sos_level())

        # We need to 'weight' each variable
        # For now we just increment a counter
        for i in range(0, len(varNames)):
            print >>OUTPUT, '%s:%f' % (varNames[i], i+1)

    def _print_model_LP(self, model, OUTPUT):

        symbol_map = {}
        _obj = model.active_components(Objective)

        supports_quadratic = model.has_capability('quadratic')

        #
        # Objective
        #
        if self._output_objectives is True:
            
           printed_quadterm = False
           if len(_obj) == 0:
               msg = "ERROR: No objectives defined for input model '%s'; "    \
                     ' cannot write legal LP file'
               raise ValueError, msg % str( model.name )

           if _obj[ _obj.keys()[0] ].sense == maximize:
              print >>OUTPUT, "max "
           else:
              print >>OUTPUT, "min "

           obj = _obj[ _obj.keys()[0] ]
           obj_keys = obj.keys()
           if len(obj_keys) > 1:
               keys = obj.name + ' (indexed by: %s)' % ', '.join(map(str, obj_keys))

               msg = "More than one objective defined for input model '%s'; " \
                     'Cannot write legal LP file\n'                           \
                     'Objectives: %s'
               raise ValueError, msg % ( str(model.name), keys )

           for key in obj_keys:

                if obj[key].repn is None:
                   raise RuntimeError, "No canonical representation identified for objective="+obj[key].name

                if is_constant(obj[key].repn):

                    print ("Warning: Constant objective detected, replacing " +
                           "with a placeholder to prevent solver failure.")
                    
                    print >>OUTPUT, obj._data[None].label+": +0.0 ONE_VAR_CONSTANT"

                    # Skip the remaining logic of the section
                    continue

                if is_quadratic( obj[key].repn ):
                    if not supports_quadratic:
                        msg  = 'Solver unable to handle quadratic '           \
                               "objective expressions.  Objective at issue: %s%s."
                        if key is None:
                           msg %= (obj.name, " ")
                        else:
                           msg %= (obj.name, '[%s]' % key )
                        raise ValueError, msg

                elif is_nonlinear( obj[key].repn ):
                    msg  = "Cannot write legal LP file.  Objective '%s%s' "  \
                           'has nonlinear terms that are not quadratic.'
                    if key is None: msg %= (obj.name, '')
                    else:           msg %= (obj.name, '[%s]' % key )
                    raise ValueError, msg

                symbol_map['__default_objective__'] = obj._data[None].label
                print >>OUTPUT, obj._data[None].label+':'

                offset = self._print_expr_canonical(obj[key].repn,
                                                    OUTPUT,
                                                    print_offset=True,
                                                    is_objective=True)

           if obj._quad_subexpr is not None:
               self._print_quadterm(obj._quad_subexpr, (_obj[ _obj.keys()[0] ].sense == minimize), OUTPUT)
               printed_quadterm = True
               
           print >>OUTPUT, ""

        # Constraints
        #
        # If there are no non-trivial constraints, you'll end up with an empty
        # constraint block. CPLEX is OK with this, but GLPK isn't. And
        # eliminating the constraint block (i.e., the "s.t." line) causes GLPK
        # to whine elsewhere. output a warning if the constraint block is empty,
        # so users can quickly determine the cause of the solve failure.

        if self._output_constraints is True:

           # for now, if this routine isn't writing everything, then assume a
           # meta-level handler is dealing with the writing of the transitional
           # elements - these should probably be done in the form of
           # "end_objective()" and "end_constraint()" helper methods.
           if self._output_objectives == self._output_variables == True:
               print >>OUTPUT, "s.t."
               print >>OUTPUT, ""

           active_constraints = model.active_components(Constraint)
           have_nontrivial = False
           for constraint in active_constraints.values():
             if constraint.trivial:
                continue

             have_nontrivial=True
             
             for index in sorted(constraint.keys()):

               constraint_data = constraint[index]
               if not constraint_data.active:
                    continue

               # if expression trees have been linearized, then the canonical
               # representation attribute on the constraint data object will
               # be equal to None.
               if (constraint_data.repn is not None):

                  # There are conditions, e.g., when fixing variables, under which
                  # a constraint block might be empty.  Ignore these, for both
                  # practical reasons and the fact that the CPLEX LP format
                  # requires a variable in the constraint body.  It is also
                  # possible that the body of the constraint consists of only a
                  # constant, in which case the "variable" of
                  if is_constant(constraint_data.repn):
                      # this happens *all* the time in many applications,
                      # including PH - so suppress the warning.
                      #
                      #msg = 'WARNING: ignoring constraint %s[%s] which is ' \
                      #      'constant'
                      #print msg % (str(C),str(index))
                      continue
   
                  if is_quadratic( constraint_data.repn ):
                      if not supports_quadratic:
                          msg  = 'Solver unable to handle quadratic expressions.'\
                                 "  Constraint at issue: '%s%%s'"
                          msg %= constraint.name
                          if index is None: msg %= ''
                          else: msg %= '[%s]' % index
   
                          raise ValueError, msg

                  elif is_nonlinear( constraint_data.repn ):
                      msg = "Cannot write legal LP file.  Constraint '%s%%s' "   \
                            'has a body with nonlinear terms.'
                      if index is None: msg %= ( constraint.name, '')
                      else:            msg %= ( constraint.name, '[%s]' % index )
   
                      raise ValueError, msg

               prefix = ""
               if self._output_prefixes is True:
                   if constraint.model is None:
                      msg = "Constraint '%s' has no model attribute - no "   \
                            'label prefix can be assigned'
                      raise RuntimeError, msg % constraint_data.label
                   prefix = constraint.model.name+"_"

               con_name = convert_name(constraint_data.label)

               if constraint_data._equality:
                  label = '%sc_e_%s_' % (prefix, con_name)
                  symbol_map['%sc_e_%s_' % (prefix, constraint_data.label)] = constraint_data.label
                  print >>OUTPUT, label+':'
                  if constraint_data.lin_body is not None:
                     offset = self._print_expr_linear(constraint_data.lin_body, OUTPUT)               
                  else:
                     offset = self._print_expr_canonical(constraint_data.repn, OUTPUT)               
                  bound = constraint_data.lower
                  bound = str(self._get_bound(bound) - offset)
                  print >>OUTPUT, "=", bound
                  print >>OUTPUT, ""
               else:
                  # TBD: ENCAPSULATE THE IF-ELSE INTO A SINGLE UTILITY METHOD
                  # TBD: MAKE THE _data and C[ndx] calls consistent - everything should just reference the data directly
                  if constraint_data.lower is not None:
                     label = '%sc_l_%s_' % (prefix, con_name)
                     symbol_map['%sc_l_%s_' % (prefix, constraint_data.label)] = constraint_data.label
                     print >>OUTPUT, label+':'
                     if constraint_data.lin_body is not None:
                        offset = self._print_expr_linear(constraint_data.lin_body, OUTPUT)                                    
                     else:
                        offset = self._print_expr_canonical(constraint_data.repn, OUTPUT)                                    
                     bound = constraint_data.lower
                     bound = str(self._get_bound(bound) - offset)
                     print >>OUTPUT, ">=", bound
                     print >>OUTPUT, ""                     
                  if constraint_data.upper is not None:
                     label = '%sc_u_%s_' % (prefix, con_name)
                     symbol_map['%sc_u_%s_' % (prefix, constraint_data.label)] = constraint_data.label
                     print >>OUTPUT, label+':'
                     if constraint_data.lin_body is not None:
                        offset = self._print_expr_linear(constraint_data.lin_body, OUTPUT)                                                         
                     else:
                        offset = self._print_expr_canonical(constraint_data.repn, OUTPUT)                                                         
                     bound = constraint_data.upper
                     bound = str(self._get_bound(bound) - offset)
                     print >>OUTPUT, "<=", bound
                     print >>OUTPUT, ""                                          

           if not have_nontrivial:
               print 'WARNING: Empty constraint block written in LP format '  \
                     '- solver may error'

           # the CPLEX LP format doesn't allow constants in the objective (or
           # constraint body), which is a bit silly.  To avoid painful
           # book-keeping, we introduce the following "variable", constrained
           # to the value 1.  This is used when quadratic terms are present.
           # worst-case, if not used, is that CPLEX easily pre-processes it out.
           prefix = ""
           if self._output_prefixes is True:
              prefix = model.name + "_"
           print >>OUTPUT, '%sc_e_ONE_VAR_CONSTANT: ' % prefix
           print >>OUTPUT, '%sONE_VAR_CONSTANT = 1.0' % prefix
           print >>OUTPUT, ""

        #
        # Bounds
        #

        if self._output_variables is True:

           # For now, if this routine isn't writing everything, then assume a
           # meta-level handler is dealing with the writing of the transitional
           # elements - these should probably be done in the form of
           # "end_objective()" and "end_constraint()" helper methods.
           if True == self._output_objectives == self._output_constraints:
               print >>OUTPUT, "bounds "

           # Scan all variables even if we're only writing a subset of them.
           # required because we don't store maps by variable type currently.

           # Track the number of integer and binary variables, so you can
           # output their status later.
           niv = nbv = 0

           VAR = model.active_components(Var)

           for variable_name in sorted(VAR.keys()):

               var = VAR[variable_name]

               for index in sorted(var.keys()):
                   v = var[index]
                   if isinstance(v.domain, IntegerSet):   niv += 1
                   elif isinstance(v.domain, BooleanSet): nbv += 1

               if self._output_continuous_variables is True:

                   for index in sorted(var._varval.keys()):

                       if not var._varval[index].active:
                           continue
                       prefix = ""
                       if self._output_prefixes is True:
                           prefix = convert_name(var.model.name)+"_"

                       # if the variable isn't referenced in the model, don't
                       # output bounds...
                       if var[index].id != -1:
                           # in the CPLEX LP file format, the default variable
                           # bounds are 0 and +inf.  These bounds are in
                           # conflict with Pyomo, which assumes -inf and inf
                           # (which we would argue is more rational).
                           print >>OUTPUT,"   ",
                           if var[index].lb is not None:
                             print >>OUTPUT, str(value(var[index].lb())), "<= ",
                           else:
                             print >>OUTPUT, " -inf <= ",
                           name_to_output = prefix+convert_name(var[index].label)
                           if name_to_output == "e":
                               msg = 'Attempting to write variable with name' \
                                     "'e' in a CPLEX LP formatted file - "    \
                                     'will cause a parse failure due to '     \
                                     'confusion with numeric values '         \
                                     'expressed in scientific notation'
                               raise ValueError, msg
                           print >>OUTPUT, name_to_output,
                           if var[index].ub is not None:
                               print >>OUTPUT, " <=", str(value(var[index].ub()))
                           else:
                               print >>OUTPUT, " <= +inf"

           if (niv > 0) and (self._output_integer_variables is True):

              # If we're outputting the whole model, then assume we can output
              # the "general" header. If not, then assume a meta-level process
              # is taking care of it.
              if True == self._output_objectives == self._output_constraints:
                 print >>OUTPUT, "general"

              prefix = ""
              if self._output_prefixes is True:
                 prefix = convert_name(var.model.name)+"_"

              for variable_name in sorted(VAR.keys()):
        
                var = VAR[variable_name]

                for index in sorted(var.integer_keys()):

                   if not var[index].active:
                      continue
                   if var[index].id != -1: # skip if variable not referenced
                       var_name = prefix+convert_name(var[index].label)
                       print >>OUTPUT, ' ', var_name

           if (nbv > 0) and (self._output_binary_variables is True):

              # If we're outputting the whole model, then assume we can output
              # the "binary" header. if not, then assume a meta-level process
              # is taking care of it.
              if True == self._output_objectives == self._output_constraints:
                 print >>OUTPUT, "binary"

              prefix = ""
              if self._output_prefixes is True:
                 prefix = convert_name(var.model.name)+"_"

              for variable_name in sorted(VAR.keys()):
        
                var = VAR[variable_name]

                for index in sorted(var.binary_keys()):
                   if not var[index].active:
                       continue
                   if var[index].id != -1: # skip if variable not referenced
                       var_name = prefix+convert_name(var[index].label)
                       print >>OUTPUT, ' ', var_name


        # SOS constraints
        #
        # For now, we write out SOS1 and SOS2 constraints in the cplex format
        #
        # All Component objects are stored in model._component, which is a
        # dictionary of {class: {objName: object}}.
        #
        # Consider the variable X,
        #
        #   model.X = Var(...)
        #
        # We print X to CPLEX format as X(i,j,k,...) where i, j, k, ... are the
        # indices of X.
        #
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders
        sosn = model.has_capability("sosn")
        sos1 = model.has_capability("sos1")
        sos2 = model.has_capability("sos2")

        if sosn or sos1 or sos2:
            writtenSOS = False
            constrs = model.components[SOSConstraint]
            for name in constrs:
                con = constrs[name]
                level = con.sos_level()
                if (level == 1 and sos1) or (level == 2 and sos2) or (sosn):
                    if writtenSOS == False:
                        print >>OUTPUT, "SOS"
                        writtenSOS = True
                    masterIndex = con.sos_set_set()
                    if None in masterIndex:
                        # A single constraint
                        self.printSOS(con, name, OUTPUT)
                    else:
                        # A series of indexed constraints
                        for index in masterIndex:
                            self.printSOS(con, name, OUTPUT, index)

        #
        # wrap-up
        #
        if self._output_objectives == self._output_constraints == True:
           #
           # End
           #
           print >>OUTPUT, "end "
        #
        return symbol_map
