import compiler
import dateutil.parser
import scipy
import numpy
import math
from quant.leastsquares import LeastSquares

# Todo: Write plots to file.
isPlotting = False
if isPlotting:
    from pylab import *

# Todo: Independent tests for this module.

class DslParser(object):
    
    def parse(self, dslSource):
        try:
            dslAst = compiler.parse(dslSource, 'eval')
        except SyntaxError, err:
            error = "specification is broken" 
            desc = err
            raise DslSourceError(error, desc)
        try:
            dslObject = self.visit(dslAst)
        except DslSourceError, err:
            raise
        if not isinstance(dslObject, Expression):
            error = "specification is broken" 
            desc = "must start with a contract object"
            desc += " (%s was found)" % (dslObject.__class__.__name__)
            raise DslSourceError(error, desc, dslObject.node)
        return dslObject

    def visit(self, node):
        cls = node.__class__
        meth = getattr(self, 'visit'+cls.__name__, self.default)
        return meth(node)
            
    def default(self, node):
        if node:
            raise DslSourceError( "Unsupported source construct", node.__class__, node)
        else:
            raise Exception, "Node is broken."
            
    def visitAdd(self, node):
        return Add(node=node, *self.visitChildNodes(node))

    def visitCallFunc(self, node):
        childNodes = node.getChildNodes()
        if not len(childNodes):
            raise DslSourceError("Call func is broken (child nodes not found)", node.name, node)
        calledNode = childNodes[0]
        if calledNode.__class__.__name__ != 'Name':
            if calledNode.__class__.__name__ == 'CallFunc':
                uncallableName = calledNode.getChildNodes()[0].name
            else:
                uncallableName = calledNode.__class__.__name__
            descr = "'%s' object is not callable" % uncallableName
            raise DslSourceError("Type error", descr, node)
        # Resolve the name.
        if calledNode.name in dslClasses:
            dslClass = dslClasses[calledNode.name]
        else:
            raise DslSourceError("Unrecognised language", calledNode.name, calledNode)
        dslArgs = [self.visit(i) for i in childNodes[1:]]
        return dslClass(node=node, *dslArgs)

    def visitConst(self, node):
        if isinstance(node.value, (str, unicode)):
            return String(node.value, node=node)
        elif isinstance(node.value, (int, float)):
            return Float(node.value, node=node)
        else:
            raise DslSourceError("Unsupported constant type", type(node.value), node)
          
    def visitDiv(self, node):
        return Div(node=node, *self.visitChildNodes(node))
    
    def visitMul(self, node):
        return Mul(node=node, *self.visitChildNodes(node))
    
    def visitExpression(self, node):
        for child in node.getChildNodes():
            return self.visit(child)
            
    def visitName(self, node):
        if node.name in dslClasses:
            dslClass = dslClasses[node.name]
            return dslClass(node=node)
        else:
            raise DslSourceError("Strings must be quoted", node.name, node)
                                 
    def visitSub(self, node):
        return Sub(node=node, *self.visitChildNodes(node))

    def visitUnarySub(self, node):
        return UnarySub(node=node, *self.visitChildNodes(node))

    def visitChildNodes(self, node):
        return [self.visit(i) for i in node.getChildNodes()]


class DslObject(object):

    def __init__(self, *args, **kwds):
        self.node = kwds.pop('node', None)
        self.validate(args)
        self.args = args

    def validate(self, args):
        pass

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join([str(i) for i in self.args]))

    def evaluate(self, **kwds):
        raise Exception, "Method not implemented on %s" % self.__class__

    def assertArgsLen(self, args, requiredLen=None, minLen=None):
        if minLen != None and len(args) < minLen:
            error = "%s is broken" % self.__class__.__name__
            descr = "requires at least %s arguments (%s were given)" % (minLen, len(args))
            raise DslSourceError(error, descr, self.node)
        if requiredLen != None and len(args) != requiredLen:
            error = "%s is broken" % self.__class__.__name__
            descr = "requires %s arguments (%s were given)" % (requiredLen, len(args))
            raise DslSourceError(error, descr, self.node)

    def assertArgsPosn(self, args, posn, requiredType):
        arg = args[posn]
        if not isinstance(arg, requiredType):
            error = "%s is broken" % self.__class__.__name__
            if isinstance(requiredType, tuple):
                requiredTypeNames = [i.__name__ for i in requiredType]
                requiredTypeNames = ", ".join(requiredTypeNames)
            else:
                requiredTypeNames = requiredType.__name__
            desc = "argument %s must be %s" % (posn, requiredTypeNames)
            desc += " (but a %s was found)" % (arg.__class__.__name__)
            raise DslSourceError(error, desc, self.node)

    def findInstances(self, dslType):
        dslObjects = set()
        for arg in self.args:
            if isinstance(arg, dslType):
                dslObjects.add(arg)
            if isinstance(arg, DslObject):
                dslObjects.update(arg.findInstances(dslType=dslType))
        return dslObjects


class Constant(DslObject):

    requiredType = None

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=1)
        if self.requiredType == None:
            raise Exception, "requiredType attribute not set on %s" % self.__class__
        self.assertArgsPosn(args, posn=0, requiredType=self.requiredType)

    def evaluate(self, **kwds):
        return self.args[0]

    def __str__(self):
        return repr(self.args[0])


class Expression(DslObject):

    def discount(self, value, date, **kwds):
        image = kwds['image']
        r = float(kwds['interestRate']) / 100
        T = image.priceProcess.getDurationYears(kwds['presentTime'], date)
        return value * math.exp( - r * T)


class Add(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        return a + b

    def __str__(self):
        if len(self.args) >= 2:
            return '%s - %s' % (self.args[0], self.args[1])
        else:
            return 'Sub(???)'


class Choice(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        presentTime = kwds['presentTime']
        contract0 = self.args[0]
        contract1 = self.args[1]
        initialState = State(self, presentTime)
        finalStates = [State(contract0, presentTime), State(contract1, presentTime)]
        longstaffSchwartz = LongstaffSchwartz(initialState, finalStates)
        return longstaffSchwartz.evaluate(**kwds)


class State(object):

    def __init__(self, dslObject, time):
        self.subsequentStates = set()
        self.dslObject = dslObject
        self.time = time

    def addSubsequentState(self, state):
        self.subsequentStates.add(state)
        
    def __repr__(self):
        return "State(%s, time=%s)" % (self.dslObject, self.time)


class LongstaffSchwartz(object):

    def __init__(self, initialState, subsequentStates=[]):
        self.initialState = initialState
        for subsequentState in subsequentStates:
            self.initialState.addSubsequentState(subsequentState)
        self.states = None
        self.statesByTime = None

    def evaluate(self, **kwds):
        allRvs = kwds['allRvs']
        image = kwds['image']
        firstMarketRvs = allRvs.values()[0]
        allStates = self.getStates()
        allStates.reverse()
        valueOfBeingIn = {}
        for state in allStates:
            lenSubsequentStates = len(state.subsequentStates)
            if lenSubsequentStates > 1:
                nextValues = []
                conditionalExpectedValues = []
                expectedContinuationValues = []
                diffContinuationValues = []
                underlyingValue = firstMarketRvs[state.time]
                plotCount = 3000 
                for subsequentState in state.subsequentStates:
                    regressionVariables = []
                    markets = subsequentState.dslObject.findInstances(Market)
                    for market in markets:
                        marketRvs = allRvs[market.getDomainObject(image)]
                        try:
                            marketRv = marketRvs[state.time]
                        except KeyError, inst:
                            msg = "Couldn't find time '%s' in random variables. Times are: %s" % (state.time, marketRvs.keys())
                            raise Exception, msg

                        regressionVariables.append(marketRv)
                    payoffValue = self.getPayoff(state, subsequentState)
                    # Todo: Either use or remove 'getPayoff()', payoffValue not used ATM.
                    expectedContinuationValue = valueOfBeingIn[subsequentState]
                    expectedContinuationValues.append(expectedContinuationValue)
                    if len(regressionVariables):
                        conditionalExpectedValue = LeastSquares(regressionVariables, expectedContinuationValue).fit()
                        if isPlotting:
                            data = scipy.array([underlyingValue[:plotCount], conditionalExpectedValue[:plotCount], expectedContinuationValue[:plotCount]])
                            plot(data[0], data[2], 'go')
                            plot(data[0], data[1], 'y^')
                    else:
                        conditionalExpectedValue = expectedContinuationValue
                    conditionalExpectedValues.append(conditionalExpectedValue)
                conditionalExpectedValues = scipy.array(conditionalExpectedValues)
                expectedContinuationValues = scipy.array(expectedContinuationValues)
                coords = []
                argmax = conditionalExpectedValues.argmax(axis=0)
                offsets = scipy.array(range(0, conditionalExpectedValues.shape[1])) * conditionalExpectedValues.shape[0]
                indices = argmax + offsets
                assert indices.shape == underlyingValue.shape
                stateValue = expectedContinuationValues.transpose().take(indices)
                assert stateValue.shape == underlyingValue.shape
                if isPlotting:
                    data = scipy.array([underlyingValue[:plotCount], stateValue[:plotCount]])
                    plot(data[0], data[1], 'rs')
                    draw()
                    show()
            elif lenSubsequentStates == 1:
                subsequentState = state.subsequentStates.pop()
                stateValue = valueOfBeingIn[subsequentState]
            elif lenSubsequentStates == 0:
                stateValue = state.dslObject.evaluate(**kwds)
                if isinstance(stateValue, (int, float)):
                    underlyingValue = firstMarketRvs[state.time]
                    pathCount = len(underlyingValue)
                    if stateValue == 0:
                        stateValue = scipy.zeros(pathCount)
                    else:
                        ones = scipy.ones(pathCount)
                        stateValue = ones * stateValue
                if not isinstance(stateValue, numpy.ndarray):
                    raise Exception, "State value type is '%s' when numpy.ndarray is required: %s" % (type(stateValue), stateValue)
            valueOfBeingIn[state] = stateValue
        return valueOfBeingIn[self.initialState]

    def getTimes(self):
        return self.getStatesByTime().keys()
        
    def getStatesAt(self, time):
        return self.getStatesByTime()[time]

    def getStatesByTime(self):
        if self.statesByTime == None:
            self.statesByTime = {}
            for state in self.getStates():
                if state.time not in self.statesByTime:
                    self.statesByTime[state.time] = []
                self.statesByTime[state.time].append(state)
        return self.statesByTime
        
    def getStates(self):
        if self.states == None:
            self.states = self.findStates(self.initialState)
        return self.states

    def findStates(self, state):
        states = [state]
        for subsequentState in state.subsequentStates:
            states += self.findStates(subsequentState)
        return states

    def getPayoff(self, state, nextState):
        return 0


class Date(DslObject):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=1)
        self.assertArgsPosn(args, posn=0, requiredType=String)
        # Check the string can actually be parsed.
        dateStr = args[0].evaluate()
        if not dateStr:
            error = "%s is broken" % self.__class__.__name__
            descr = "date string is empty"
            raise DslSourceError(error, descr, self.node)
        try:
            dateTime = dateutil.parser.parse(dateStr)
        except ValueError, inst:
            error = "%s is broken" % self.__class__.__name__
            descr = "date parser can't parse '%s'" % (dateStr)
            raise DslSourceError(error, descr, self.node)

    def evaluate(self, **kwds):
        dateStr = self.args[0].evaluate(**kwds)
        return dateutil.parser.parse(dateStr)


class Div(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        return a / b

    def __str__(self):
        if len(self.args) >= 2:
            return '%s / %s' % (self.args[0], self.args[1])
        else:
            return 'Div(???)'


class Mul(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        return a * b

    def __str__(self):
        if len(self.args) >= 2:
            return '%s * %s' % (self.args[0], self.args[1])
        else:
            return 'Mul(???)'


class Fixing(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        try:
            self.assertArgsPosn(args, posn=0, requiredType=Date)
            self.assertArgsPosn(args, posn=1, requiredType=Expression)
            self.posDate = 0
            self.posExpr = 1
        except:
            # Old format (still used in the tests).
            # Todo: Change the tests to new format. :-)
            self.assertArgsPosn(args, posn=0, requiredType=Expression)
            self.assertArgsPosn(args, posn=1, requiredType=Date)
            self.posExpr = 0
            self.posDate = 1

    def evaluate(self, **kwds):
        newkwds = kwds.copy()
        newkwds['presentTime'] = self.getDate()
        return self.args[self.posExpr].evaluate(**newkwds)

    def getDate(self):
        return self.args[self.posDate].evaluate()
 

class Float(Constant, Expression):

    requiredType=(int, float)


class Market(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=1)
        self.assertArgsPosn(args, posn=0, requiredType=String)
        # Todo: Check the market can actually be found.

    def evaluate(self, **kwds):
        image = kwds['image']
        presentTime = kwds['presentTime']
        lastPrice = self.getLastPrice(image)
        if presentTime == image.observationTime:
            value = lastPrice
        else:
            allRvs = kwds['allRvs']
            domainObject = self.getDomainObject(image)
            if domainObject not in allRvs:
                raise Exception, "Market %s not in all rvs: %s" % (domainObject, allRvs.keys())

            marketRvs = allRvs[domainObject]
            if presentTime not in marketRvs:
                raise Exception, "Present time %s not in market rvs: %s" % (presentTime, marketRvs.keys())
            rv = marketRvs[presentTime]
            sigma = self.getSigma(image)
            T = image.priceProcess.getDurationYears(image.observationTime, presentTime)
            value = lastPrice * scipy.exp(sigma * rv - 0.5 * sigma * sigma * T)
        return value

    def getLastPrice(self, image):
        return self.getMetricValue(image, 'last-price')

    def getSigma(self, image):
        volatility = self.getMetricValue(image, 'actual-historical-volatility')
        return float(volatility) / 100

    def getMetricValue(self, image, metricName):
        return image.getMetricValue(metricName, self.getDomainObject(image))

    def getDomainObject(self, image):
        if not hasattr(self, 'domainObject'):
            self.domainObject = None
            marketRef = self.args[0].evaluate()
            if marketRef:
                if marketRef.startswith('#'):
                    marketId = marketRef[1:]
                    self.domainObject = image.registry.markets.findSingleDomainObject(id=marketId)
            if not self.domainObject:
                raise Exception, "Market '%s' could not be found." % marketRef
        return self.domainObject


class Max(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        # Assume a and b have type ndarray, or type int, or type float.
        # Todo: Figure out how to test positively for ndarray type. :-)
        # Try to 'balance' the sides.
        #  - two scalar numbers are good
        #  - one number with one vector is okay
        #  - two vectors is not okay
        # Todo: Decide how or whether or not to support max of two random variable.
        #       Is not Choice the true "max" of two random variables, so this
        #       Max should not validate with e.g. two Fixings? Or does that mean
        #       something else, if so is it useful?
        if not isinstance(a, (int, float)) and not isinstance(b, (int, float)):
            if len(a) != len(b):
                descr = "%s and %s" % (len(a), len(b))
                raise DslProgrammingError('Vectors have different length: ', descr, self.node)
        elif not (isinstance(a, (int, float)) or isinstance(b, (int, float))):
        #if not (isinstance(a, (int, float)) or isinstance(b, (int, float))):
            descr = "%s and %s" % (type(a), type(b))
            raise DslProgrammingError('Unable to balance two vectors in Max (needs at least one scalar)', descr, self.node)
        elif isinstance(a, (int, float)) and not isinstance(b, (int, float)):
            # Todo: Optimise with scipy.zeros() when a or b equals zero.
            a = scipy.array([a] * len(b))
        elif isinstance(b, (int, float)) and not isinstance(a, (int, float)):
            # Todo: Optimise with scipy.zeros() when a or b equals zero.
            b = scipy.array([b] * len(a))
        c = scipy.array([a, b])
        return c.max(axis=0)


class Settlement(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        try:
            self.assertArgsPosn(args, posn=1, requiredType=Expression)
            self.assertArgsPosn(args, posn=0, requiredType=Date)
            self.posExpr = 1
            self.posDate = 0
        except:
            # Old format (still used in the tests).
            # Todo: Change the tests to new format. :-)
            self.assertArgsPosn(args, posn=1, requiredType=Date)
            self.assertArgsPosn(args, posn=0, requiredType=Expression)
            self.posDate = 1
            self.posExpr = 0

    def evaluate(self, **kwds):
        newkwds = kwds.copy()
        value = self.args[self.posExpr].evaluate(**newkwds)
        date = self.args[self.posDate].evaluate(**newkwds)
        return self.discount(value, date, **kwds)


class String(Constant):

    requiredType = (str, unicode)


class Sub(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        return a - b

    def __str__(self):
        if len(self.args) >= 2:
            return '%s - %s' % (self.args[0], self.args[1])
        else:
            return 'Sub(???)'


class UnarySub(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=1)
        self.assertArgsPosn(args, posn=0, requiredType=Expression)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        return -a

    def __str__(self):
        if len(self.args) >= 1:
            return "-%s" % (self.args[0])
        else:
            return 'UnarySub(???)'


class Wait(Expression):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Date)
        self.assertArgsPosn(args, posn=1, requiredType=Expression)

    def evaluate(self, **kwds):
        date = self.getDate()
        newkwds = kwds.copy()
        newkwds['presentTime'] = date
        value = self.getExpression().evaluate(**newkwds)
        return self.discount(value, date, **kwds)

    def getDate(self):
        return self.args[0].evaluate()
 
    def getExpression(self):
        return self.args[1]
 


dslClasses = {
    'Add': Add,
    'Choice': Choice,
    'Date': Date,
    'Div': Div,
    'Fixing': Fixing,
    'Float': Float,
    'Market': Market,
    'Max': Max,
    'Mul': Mul,
    'Settlement': Settlement,
    'String': String,
    'Sub': Sub,
    'UnarySub': UnarySub,
    'Wait': Wait,
}

class DslError(Exception):

    def __init__(self, error, descr=None, node=None):
        self.error = error
        self.descr = descr
        self.node = node
        self.lineno = getattr(node, "lineno", None)
        
    def __repr__(self):
        msg = "%s: %s" % (self.error, self.descr)
        if self.lineno:
            msg += " (line %d)" % (self.lineno)
        return msg

    __str__ = __repr__    

           
class DslSourceError(DslError): pass

class DslProgrammingError(DslError): pass

