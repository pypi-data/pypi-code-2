import compiler
import dateutil.parser
import scipy

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
        if not isinstance(dslObject, Value):
            error = "specification is broken" 
            desc = "must start with a value object"
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
            raise DslSourceError("Unrecognised language", node.name, node)
        dslArgs = [self.visit(i) for i in childNodes[1:]]
        return dslClass(node=node, *dslArgs)

    def visitConst(self, node):
        if isinstance(node.value, (str, unicode)):
            return String(node.value, node=node)
        elif isinstance(node.value, (int, float)):
            return Float(node.value, node=node)
        else:
            raise DslSourceError("Unsupported constant type", type(node.value), node)
          
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

    pathCount = 500000

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


class Value(DslObject): pass


class Add(Value):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Value)
        self.assertArgsPosn(args, posn=1, requiredType=Value)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        return a + b

    def __str__(self):
        if len(self.args) >= 2:
            return '%s - %s' % (self.args[0], self.args[1])
        else:
            return 'Sub(???)'


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


class Fixing(Value):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Market)
        self.assertArgsPosn(args, posn=1, requiredType=Date)

    def evaluate(self, **kwds):
        image = kwds['image']
        self.nowTime = image.observationTime
        market = self.args[0].evaluate(**kwds)
        self.actualHistoricalVolatility = image.getMetricValue(
            'actual-historical-volatility', market)
        self.lastPrice = image.getMetricValue('last-price', market)
        self.expiration = self.args[1].evaluate(**kwds)
        return self.calcUnderlyings(image)
 
    def calcUnderlyings(self, image):
        T = image.priceProcess.getDurationYears(self.nowTime, self.expiration)
        sigma = float(self.actualHistoricalVolatility) / 100
        sigma_root_T = sigma * scipy.sqrt(T)
        sigma_squared_T = sigma**2 * T
        draws = self.calcDraws()
        return self.lastPrice * scipy.exp(sigma_root_T * draws - 0.5 * sigma_squared_T)

    def calcDraws(self):
        if not hasattr(self, '_draws'):
            self._draws = scipy.random.standard_normal(self.pathCount)
        return self._draws


class Float(Constant, Value):

    requiredType=(int, float)


class Market(DslObject):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=1)
        self.assertArgsPosn(args, posn=0, requiredType=String)
        # Todo: Check the market can actually be found.

    def evaluate(self, **kwds):
        market = None
        marketRef = self.args[0].evaluate()
        if marketRef:
            if marketRef.startswith('#'):
                marketId = marketRef[1:]
                image = kwds['image']
                market = image.registry.markets.findSingleDomainObject(id=marketId)
        if not market:
            raise Exception, "Market '%s' could not be found." % marketRef
        return market


class Max(Value):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Value)
        self.assertArgsPosn(args, posn=1, requiredType=Value)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        # Try to 'balance' the sides.
        #  - two scalar numbers are good
        #  - one number with one vector is okay
        #  - two vectors is not okay
        # Todo: Optimise with scipy.zeros() when a or b equals zero.
        if not (isinstance(a, (int, float)) or isinstance(b, (int, float))):
            descr = "%s and %s" % (type(a), type(b))
            raise DslProgrammingError('Unable to balance two vectors in Max (needs at least one scalar)', descr, self.node)
        elif isinstance(a, (int, float)) and not isinstance(b, (int, float)):
            a = scipy.array([a] * len(b))
        elif isinstance(b, (int, float)) and not isinstance(a, (int, float)):
            b = scipy.array([b] * len(a))
        c = scipy.array([a, b])
        return c.max(axis=0)


class Settlement(Value):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Date)
        self.assertArgsPosn(args, posn=1, requiredType=Value)

    def evaluate(self, **kwds):
        date = self.args[0].evaluate(**kwds)
        value = self.args[1].evaluate(**kwds)
        if hasattr(value, 'mean'):
            value = value.mean()
        # Todo: Discount by the duration until the date.
        return value


class String(Constant):

    requiredType = (str, unicode)


class Sub(Value):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=2)
        self.assertArgsPosn(args, posn=0, requiredType=Value)
        self.assertArgsPosn(args, posn=1, requiredType=Value)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        b = self.args[1].evaluate(**kwds)
        return a - b

    def __str__(self):
        if len(self.args) >= 2:
            return '%s - %s' % (self.args[0], self.args[1])
        else:
            return 'Sub(???)'


class UnarySub(Value):

    def validate(self, args):
        self.assertArgsLen(args, requiredLen=1)
        self.assertArgsPosn(args, posn=0, requiredType=Value)

    def evaluate(self, **kwds):
        a = self.args[0].evaluate(**kwds)
        return -a

    def __str__(self):
        if len(self.args) >= 1:
            return "-%s" % (self.args[0])
        else:
            return 'UnarySub(???)'


dslClasses = {
    'Add': Add,
    'Date': Date,
    'Fixing': Fixing,
    'Float': Float,
    'Market': Market,
    'Max': Max,
    'Settlement': Settlement,
    'String': String,
    'Sub': Sub,
    'UnarySub': UnarySub,
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

