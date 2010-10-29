import xml.dom

from coopr.opt.base import problem, AbstractProblemWriter, ProblemFormat
from coopr.pyomo.base import expr, Var, Objective, Constraint
from coopr.pyomo.expr import is_constant, is_quadratic, is_nonlinear
import pyutilib

convert_name = lambda x: x.replace('[','(').replace(']',')')

class ProblemWriter_osil(AbstractProblemWriter):
    """
    This is a writer instance for the OSiL xml specification.  See "OSiL: An
    Instance Language for Optimization" by Robert Fourer, Jun Ma, Kipp Martin.
    Likely available at:

    http://www.coin-or.org/OS/publications/ (index of papers, Jun 2010)
    """
    pyutilib.component.core.alias('osil')

    def __init__( self ):
        AbstractProblemWriter.__init__( self, ProblemFormat.osil )


    def __call__( self, model, filename ):
        if filename is None:
            filename = model.name + '.xml'

        output = open( filename, 'w' )
        self._print_model( model, output )
        output.close()

        return filename, None


    def _print_model( self, model, output ):
        dom = xml.dom.getDOMImplementation()

        doc = dom.createDocument(None, None, None)
        osil = doc.createElement('osil')
        instanceHeader = self._getInstanceHeader( doc, model )
        instanceData   = self._getInstanceData( doc, model )

        osil.appendChild( instanceHeader )
        osil.appendChild( instanceData )

        doc.appendChild( osil )

        output.write( doc.toprettyxml(indent="  ") )


    def _getInstanceHeader ( self, doc, model ):
        header = doc.createElement('instanceHeader')

        name   = doc.createElement('name')
        source = doc.createElement('source')
        description = doc.createElement('description')

        name.appendChild( doc.createTextNode( model.name ) )
        source.appendChild( doc.createTextNode( model.name ) )
        description.appendChild( doc.createTextNode( model.name ) )

        header.appendChild( name )
        header.appendChild( source )
        header.appendChild( description )

        return header


    def _getInstanceData ( self, doc, model ):

        instanceData = doc.createElement('instanceData')

        nodeFunctions = (
            self._getVariablesElement,
            self._getObjectivesElement,
            self._getConstraintsElement,
            self._getLinearConstraintCoefficientsElement,
            self._getQuadraticCoefficientsElement,
            self._getNonLinearExpressionsElement,
        )

        for f in nodeFunctions:
            instanceData.appendChild( f(doc, model) )

        return instanceData


    def _getNonLinearExpressionsElement ( self, doc, model ):
        nle = doc.createElement('nonlinearExpressions')

        def create_sub_expression ( binary_action, nodes ):
            """
            Creates a sub expression of terms that need a similar action.

            For example, create_sub_expression('times', [el1, el2, el3, el4] )
            would return:

            <times><el1><times><el2><times><el3><el4></times></times></times>
            """
            if len(nodes) > 1: # multiple vars in this term
                node = doc.createElement( binary_action )
                node.appendChild( nodes.pop() )
                node.appendChild( nodes.pop() )
                for var in nodes:
                    sub_node = doc.createElement( binary_action )
                    sub_node.appendChild( node )
                    sub_node.appendChild( var )
                    node = sub_node
                expression = node
            elif len(nodes) == 1:
                expression = nodes.pop()
            else:
                # TODO include a better error message
                raise Exception, 'Pyomo internal programming error.\n'        \
                'Please inform developers of what you did to encounter this ' \
                'message: Writer, Nonlinear Sub expression creator'

            return expression


        def _create_nl_expression ( expression, index ):
            if is_quadratic( expression ) or not is_nonlinear( expression ):
                return None

            order_nodes = list()
            for order in sorted( expression.keys() ):
                if order in (-1, 0, 1, 2):
                    continue
                try:
                    dummy = int(order)
                except:
                    msg  = 'Unable to write OSiL format of model.\n'          \
                    'Explanation: The Pyomo OSiL Writer has not implemented ' \
                    'a nonlinear expression type that you have in your '      \
                    'objective or constraints.  (For example, sin(x), ln(x),' \
                    ' or x^(2.3).)'
                    raise Exception, msg

                order = expression[order] # get the actual expression part
                term_nodes = list()
                for term in order:
                    coef = order[term]

                    var_nodes = list()
                    for var in term:
                        vname = convert_name( expression[-1][var].name )
                        vid   = expression[-1][var].id

                        var_node = doc.createElement('variable')
                        var_node.setAttribute('name', vname )
                        var_node.setAttribute('idx', str(vid) )

                        power = term[var]
                        if power > 1:
                            raised_to = doc.createElement('number')
                            raised_to.setAttribute('value', str(power) )
                            power_node = doc.createElement('power')
                            power_node.appendChild( var_node )
                            power_node.appendChild( raised_to )
                            var_node = power_node

                        var_nodes.append( var_node )

                    sub_expr = create_sub_expression('times', var_nodes )

                    term_node = doc.createElement('times')
                    coef_node = doc.createElement('number')
                    coef_node.setAttribute('value', str(coef) )
                    term_node.appendChild( coef_node )
                    term_node.appendChild( sub_expr )

                    term_nodes.append( term_node )

                sub_expr = create_sub_expression('plus', term_nodes )
                order_nodes.append( sub_expr )

            sub_expr = create_sub_expression('plus', order_nodes )

            nl = doc.createElement('nl')
            nl.setAttribute('idx', str(index) )
            nl.appendChild( sub_expr )

            return nl


        def create_nl_expressions ( expressions_set, **kwargs ):
            index    = kwargs.pop('index', 0 )   # expression index
            modifier = kwargs.pop('modifer', 1 ) # next expression index?
            for es in expressions_set:
                for key in es:
                    expression = es[key].repn
                    nlexpression = _create_nl_expression( expression, index )
                    if nlexpression:
                        nle.appendChild( nlexpression )

                    index += modifier

        objectives  = sorted( model.active_components( Objective ).values() )
        constraints = sorted( model.active_components( Constraint ).values() )
        create_nl_expressions( objectives, index=-1, modifier=-1  )
        create_nl_expressions( constraints )

        nle.setAttribute('number', str(len( nle.childNodes )) )

        return nle

    def _getLinearConstraintCoefficientsElement ( self, doc, model ):
        lcc = doc.createElement('linearConstraintCoefficients')

        constraints = sorted( model.active_components( Constraint ).values() )

        # TODO: figure out when to use colIdx
        start_node = doc.createElement('start')
        row_node   = doc.createElement('rowIdx')
        value_node = doc.createElement('value')

        def get_linear_info ( expression ):
            terms = None
            if 1 in expression:
                linear_terms = tuple( sorted(expression[1]) )

                t_count = 0 # term count.  OSiL orders terms, hence the sorted
                  # call in the previous statement.  It doesn't matter /how/
                  # it sorts, just that it's consistent per run, because we're
                  # effectively creating a matrix

                terms = list()
                for term_id in linear_terms:
                    coef = expression[1][term_id]
                    terms.append( (t_count, coef) )
                    t_count += 1 # zero based, increment at loop end

            return terms

        row = 0 # Constraint count.  OSiL orders the constraints, hence the
                # sorted version of the active_components, above
        for con in constraints:
            for index in con:
                C = con[index]
                for start, value in get_linear_info( C.repn ):
                    el_beg = doc.createElement('el')
                    el_val = doc.createElement('el')
                    el_row = doc.createElement('el')
                    el_beg.appendChild( doc.createTextNode( str(start)) )
                    el_val.appendChild( doc.createTextNode( str(value)) )
                    el_row.appendChild( doc.createTextNode( str(row)) )
                    start_node.appendChild( el_beg )
                    value_node.appendChild( el_val )
                    row_node.appendChild( el_row )

                row += 1 # zero based; increment at loop end
        lcc.appendChild( start_node )
        lcc.appendChild( row_node )
        lcc.appendChild( value_node )

        lcc.setAttribute('numberOfValues', str(len(row_node.childNodes)) )

        return lcc

    def _getConstraintsElement ( self, doc, model ):
        constraint = doc.createElement('constraints')

        def get_bound ( expression, offset=0.0 ):
            if isinstance( expression, expr._IdentityExpression ):
                return get_bound( expression._args[0], offset )
            elif expression.is_constant():
                return expression() + offset
            else:
                msg  = 'Non-constant constraint bound.  Expression type: '
                msg += expression.__class__.__name__
                # TODO: Convert exp.pprint to /return/ a string, not directly
                # print.  Then it's usable in any context, like below
                # if exp is not None:
                #     msg += exp.pprint()
                raise ValueError, msg

        def get_offset ( expression ):
            offset=0.0
            if 0 in expression:
                offset = x[0][None]
            return offset

        constraints = sorted( model.active_components( Constraint ).values() )

        for con in constraints:
            for index in con:
                node = doc.createElement('con')
                C = con[index]

                name = convert_name( C.label )
                offset = get_offset( C.repn )

                node.setAttribute('name', name)

                if C._equality: # is an equality constraint
                    node.setAttribute('constant',
                        str( get_bound(C.lower, -offset) ))
                else: # is an inequality constraint
                    if C.lower is not None:
                        node.setAttribute('lb',
                            str( get_bound(C.lower, -offset) ))
                    if C.upper is not None:
                        node.setAttribute('ub',
                            str( get_bound(C.upper, -offset) ))

                constraint.appendChild( node )

        constraint.setAttribute('number', str(len(constraint.childNodes)) )

        return constraint


    def _getQuadraticCoefficientsElement ( self, doc, model ):
        quadratic = doc.createElement('quadraticCoefficients')

        qterm_index_attributes = ('idxOne', 'idxTwo')

        def add_qterms ( objs, qidx=True ):
            for idx in xrange(len(objs)):
                qterm_idx = str(idx)
                if qidx != True:
                    qterm_idx = str(-1) # -1 for objectives

                obj = objs[idx]

                for key in obj:
                    expression = obj[key].repn
                    if is_constant( expression ):
                        # we've already informed the user we're ignoring this
                        # Object, so ignore it and move on
                        continue

                    if 2 in expression: # quadratic terms
                        keys = expression[2].keys()
                        for quadterm in tuple(keys):
                            qterm = doc.createElement('qterm')
                            i = iter( qterm_index_attributes )

                            for var_id in quadterm:
                                var_index = str( var_id[1] )
                                count = quadterm[var_id]

                                if ( 2 == count ):  # same var (e.g. X**2)
                                    qterm.setAttribute( i.next(), var_index )
                                    qterm.setAttribute( i.next(), var_index )
                                else: # different vars (e.g. X*Y)
                                    qterm.setAttribute( i.next(), var_index )

                            coef = str( expression[2][quadterm] )
                            qterm.setAttribute('coef', coef )
                            qterm.setAttribute('idx', qterm_idx )
                            quadratic.appendChild( qterm )

        # The quadratics section of the XML document deals with both
        # objectives and constraints, so we add them in two parts.
        objectives = sorted( model.active_components( Objective ).values() )
        constraints = sorted( model.active_components( Constraint ).values() )
        add_qterms( objectives, False )
        add_qterms( constraints )

        quadratic.setAttribute('numberOfQuadraticTerms',
            str(len(quadratic.childNodes)) )

        return quadratic


    def _getObjectivesElement ( self, doc, model ):
        objectives = doc.createElement('objectives')

        objs = model.active_components( Objective ).values()

        for obj in objs:
            obj_node = doc.createElement('obj')

            for key in obj: # note: None is a valid dict key
                expression = obj[key].repn
                if is_constant( expression ):
                    msg = "Ignoring objective '%s[%s]' which is constant"
                    Logger.warning( msg % (str(obj), str(key)) )
                    continue

                if 1 in expression: # first-order terms
                    keys = sorted( expression[1].keys() )
                    for var_key in keys:
                        var_index = expression[-1][var_key.keys()[0]].id
                        coef = expression[1][var_key]
                        value = doc.createTextNode( str(coef) )

                        coef_node = doc.createElement('coef')
                        coef_node.setAttribute('idx', str(var_index) )
                        coef_node.appendChild( value )

                        obj_node.appendChild( coef_node )

                # don't worry about non-linear parts here.  It's checked as
                # part of _getNonlinearExpressions

            sense = 'max'
            if obj.is_minimizing(): sense = 'min'

            obj_node.setAttribute('maxOrMin', sense )
            obj_node.setAttribute('name', obj.name )
            obj_node.setAttribute('numberOfObjCoef',
                str(len(obj_node.childNodes)) )

            objectives.appendChild( obj_node )

        objectives.setAttribute('number', str(len(objectives.childNodes)) )

        return objectives


    def _getVariablesElement ( self, doc, model ):
        variables = doc.createElement('variables')

        vars = model.active_components( Var ).values()

        for vararray in vars:
            ubound = 'INF'
            lbound = '-INF'
            vtype  = 'C' # variable type: continuous
            for key in vararray:
                name = '%s(%s)' % (str(vararray), str(key))
                name = ''.join(name.split()) # remove whitespace
                name = name.replace('((', '(').replace('))', ')')

                var = vararray[key]

                if ( var.ub ): ubound = str(var.ub.value)
                if ( var.lb ): lbound = str(var.lb.value)

                if   ( var.is_continuous() ): vtype = 'C'
                elif ( var.is_binary() ):     vtype = 'B'
                elif ( var.is_integer() ):    vtype = 'I'
                # TODO: can Pyomo represent 'S' (String-valued) variables?
                # TODO: can Pyomo represent 'D' (Semi-continuous) variables?
                # TODO: can Pyomo represent 'J' (Semi-integer) variables?

                node = doc.createElement('var')
                node.setAttribute('name', name )
                node.setAttribute('lb', lbound )
                node.setAttribute('ub', ubound )
                node.setAttribute('type', vtype )

                variables.appendChild( node )

        variables.setAttribute('number', str(len(variables.childNodes)) )

        return variables
