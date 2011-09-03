#==============================================================================
# STUBS for development purposes
#==============================================================================

class _base_stub(object):

    def _typename(self):
        return type(self).__name__

class _space_stub(_base_stub):

    def __init__(self):
        self._nivars = 0
        self._nbvars = 0
        self._nsvars = 0

    def intvar(self, *args):
        n = self._nivars
        self._nivars = n+1
        return IntVar(n)

    def boolvar(self, *args):
        n = self._nbvars
        self._bvars = n+1
        return BoolVar(n)

    def setvar(self, *args):
        n = self._nsvars
        self._nsvars = n+1
        return SetVar(n)

    def intvars(self, n, *args):
        return (self.intvar(*args) for i in range(n))

    def boolvars(self, n, *args):
        return (self.boolvar(*args) for i in range(n))

    def setvars(self, n, *args):
        return (self.setvar(*args) for i in range(n))

    def intset(self, *args):
        return IntSet(args)

class _var_stub(_base_stub):

    def __init__(self, n):
        self.idx = n

    def __str__(self):
        return "<%s %s>" % (self._typename(), self.idx)

class _Var(_var_stub):
    pass


#==============================================================================
# Expr: base class for expressions, containing all the operator logic
#==============================================================================

class Expr(_base_stub):
    
    @staticmethod
    def _add(x,y):
        if is_int(x,y):
            return IExprADD(x,y)
        if is_set(x,y):
            return SExprDUNION(x,y)
        raise TypeError("%s + %s" % (x,y))

    def __add__(self, other):
        return self._add(self, other)
    def __radd__(self, other):
        return self._add(other, self)

    @staticmethod
    def _sub(x,y):
        if is_int(x,y):
            return IExprSUB(x,y)
        if is_set(x,y):
            return SExprDIFF(x,y)
        raise TypeError("%s - %s" % (x,y))

    def __sub__(self, other):
        return self._sub(self, other)
    def __rsub__(self, other):
        return self._sub(other, self)

    @staticmethod
    def _mul(x,y):
        if is_int(x,y):
            return IExprMUL(x,y)
        raise TypeError("%s * %s" % (x,y))

    def __mul__(self, other):
        return self._mul(self, other)
    def __rmul__(self, other):
        return self._mul(other, self)

    @staticmethod
    def _and(x,y):
        if is_bool(x,y):
            return BExprAND(x,y)
        if is_set(x,y):
            return SExprINTER(x,y)
        raise TypeError("%s & %s" % (x,y))

    def __and__(self, other):
        return self._and(self, other)
    def __rand__(self, other):
        return self._and(other, self)

    @staticmethod
    def _or(x,y):
        if is_bool(x,y):
            return BExprOR(x,y)
        if is_set(x,y):
            return SExprUNION(x,y)
        raise TypeError("%s | %s" % (x,y))

    def __or__(self, other):
        return self._or(self, other)
    def __ror__(self, other):
        return self._or(other, self)

    @staticmethod
    def _imp(x,y):
        if is_bool(x,y):
            return BExprIMP(x,y)
        raise TypeError("%s >> %s" % (x,y))

    def __rshift__(self, other):
        return self._imp(self, other)
    def __rrshift__(self, other):
        return self._imp(other, self)
    def __lshift__(self, other):
        return self._imp(other, self)
    def __rlshift__(self, other):
        return self._imp(self, other)

    @staticmethod
    def _eq(x,y):
        if is_int(x,y):
            return IRelEQ(x,y)
        if is_set(x,y):
            return SRelEQ(x,y)
        raise TypeError("%s == %s" % (x,y))

    def __eq__(self, other):
        return self._eq(self, other)

    @staticmethod
    def _ne(x,y):
        if is_int(x,y):
            return IRelNE(x,y)
        if is_set(x,y):
            return SRelNE(x,y)
        raise TypeError("%s != %s" % (x,y))

    def __ne__(self, other):
        return self._ne(self, other)

    @staticmethod
    def _lt(x,y):
        if is_int(x,y):
            return IExprLT(x,y)
        raise TypeError("%s < %s" % (x,y))

    def __lt__(self, other):
        return self._lt(self, other)
    def __gt__(self, other):
        return self._lt(other, self)

    @staticmethod
    def _le(x,y):
        if is_int(x,y):
            return IExprLE(x,y)
        if is_set(x,y):
            return SExprLE(x,y)
        if is_int(x) and is_set(y):
            return SExprLE(x,y)
        raise TypeError("%s <= %s" % (x,y))

    def __le__(self, other):
        return self._le(self, other)
    def __ge__(self, other):
        return self._le(other, self)

    @staticmethod
    def _neg(x):
        if is_int(x):
            return IExprNEG(x)
        if is_set(x):
            return SExprCOMPL(x)
        raise TypeError("- %s" % x)

    def __neg__(self):
        return self._neg(self)

    @staticmethod
    def _not(x):
        if is_bool(x):
            return BExprNOT(x)
        raise TypeError("~ %s" % x)

    def __invert__(self):
        return self._not(self)

    @staticmethod
    def _floordiv(x,y):
        if is_int(x,y):
            return IExprDIV(x,y)
        if is_set(x,y):
            return SExprDISJ(x,y)
        raise TypeError("%s // %s" % (x,y))

    def __floordiv__(self, other):
        return self._floordiv(self, other)
    def __rfloordiv__(self, other):
        return self._floordiv(other, self)

    @staticmethod
    def _xor(x,y):
        if is_bool(x,y):
            return BExprXOR(x,y)
        raise TypeError("%s ^ %s" % (x,y))

    def __xor__(self, other):
        return self._xor(self, other)
    def __rxor__(self, othet):
        return self._xor(other, self)

    @staticmethod
    def _mod(x,y):
        if is_int(x,y):
            return IExprMOD(x,y)
        raise TypeError("%s %% %s" % (x,y))
    
    def __mod__(self, other):
        return self._mod(self, other)
    def __rmod__(self, other):
        return self._mod(other, self)

    @staticmethod
    def _div(x,y):
        if is_int(x,y):
            return IExprDIV(x,y)
        raise TypeError("%s / %s" % (x,y))

    def __div__(self, other):
        return self._div(self, other)
    def __rdiv__(self, other):
        return self._div(other, self)

    def __truediv__(self, other):
        return self._div(self, other)
    def __rtruediv__(self, other):
        return self._div(other, self)

class IExpr(Expr): pass
class BExpr(IExpr): pass
class SExpr(Expr): pass

class UniExpr(object):

    def __init__(self, x):
        self.x = x

    def __str__(self):
        return "<%s %s>" % (self._typename(), self.x)

class BinExpr(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "<%s %s %s>" % (self._typename(), self.x, self.y)

class IUniExpr(UniExpr,IExpr): pass
class BUniExpr(UniExpr,BExpr): pass
class SUniExpr(UniExpr,SExpr): pass

class IBinExpr(BinExpr,IExpr): pass
class BBinExpr(BinExpr,BExpr): pass
class SBinExpr(BinExpr,SExpr): pass

class IExprNEG(IUniExpr): pass
class IExprADD(IBinExpr): pass
class IExprSUB(IBinExpr): pass
class IExprMUL(IBinExpr): pass
class IExprDIV(IBinExpr): pass
class IExprMOD(IBinExpr): pass

class BExprNOT(BUniExpr): pass
class BExprAND(BBinExpr): pass
class BExprOR (BBinExpr): pass
class BExprIMP(BBinExpr): pass
class BExprXOR(BBinExpr): pass

class Rel(BBinExpr): pass
class IRel(Rel): pass
class SRel(Rel): pass

class IRelEQ(IRel): pass
class IRelNE(IRel): pass
class IRelLT(IRel): pass
class IRelLE(IRel): pass

class SExprCOMPL(SUniExpr): pass
class SExprINTER(SBinExpr): pass
class SExprUNION(SBinExpr): pass
class SExprDUNION(SBinExpr): pass
class SExprDIFF (SBinExpr): pass

class SRelEQ(SRel): pass
class SRelNE(SRel): pass
class SRelLE(SRel): pass
class SRelDISJ(SRel): pass

class IExprSUM(IUniExpr): pass
class BExprSUM(IExprSUM): pass
class IExprSUM2(IBinExpr): pass
class BExprSUM2(IExprSUM2): pass
class IExprMIN(IUniExpr): pass
class IExprMIN2(IBinExpr): pass
class SExprMIN(SUniExpr): pass
class IExprMAX(IUniExpr): pass
class IExprMAX2(IBinExpr): pass
class SExprMAX(SUniExpr): pass
class IExprABS(IUniExpr): pass
class IExprSQR(IUniExpr): pass
class IExprSQRT(IUniExpr): pass
class SExprCARD(SUniExpr): pass

class IExprELEM(IUniExpr): pass
class SExprELEM(SUniExpr): pass
class SExprELEMINTER(SUniExpr): pass
class SExprELEMINTER2(SBinExpr): pass
class SExprELEMUNION(SUniExpr): pass
class SExprELEMUNION2(SBinExpr): pass
class SExprELEMDUNION(SUniExpr): pass
class SExprELEMDUNION2(SBinExpr): pass
class SExprSINGLETON(SUniExpr): pass

#==============================================================================
# variable and intset types (stubs for development)
#==============================================================================

class IntVar (_Var,IExpr): pass
class BoolVar(_Var,BExpr): pass
class SetVar (_Var,Sexpr): pass

class IntSet(SExpr):

    def __init__(self, args):
        self.args = args

    def __str__(self):
        return "<%s %s>" % (self._typename(), self.args)

#==============================================================================
# tests
#==============================================================================

def are_of_type(x, types):
    for y in x:
        if not isinstance(y, types):
            return False
    return True

_VECTOID_TYPES = (tuple, list)

def is_vectoid(*x):
    return are_of_type(x, _VECTOID_TYPES)

def is_vectoid_of_type(x, types):
    return is_vectoid(x) and are_of_type(x, types)

_INT_TYPES = (int, IExpr)

def is_int(*x):
    return are_of_type(x, _INT_TYPES)

def is_ints(x):
    return is_vectoid_of_type(x, _INT_TYPES)

_BOOL_TYPES = (bool, BExpr)

def is_bool(*x):
    return are_of_type(x, _BOOL_TYPES)

def is_bools(x):
    return is_vectoid_of_type(x, _BOOL_TYPES)

_SET_TYPES = (SExpr,)

def is_set(*x):
    return are_of_type(x, _SET_TYPES)

def is_sets(x):
    return is_vectoid_of_type(x, _SET_TYPES)

_INTSET_TYPES = (IntSet,)

def is_intset(*x):
    return are_of_type(x, _INTSET_TYPES)

def is_intsets(x):
    return is_vectoid_of_type(x, _INTSET_TYPES)

_INTVAR_TYPES = (IntVar,)

def is_intvar(*x):
    return are_of_type(x, _INTVAR_TYPES)

def is_intvars(x):
    return is_vectoid_of_type(x, _INTVAR_TYPES)

_BOOLVAR_TYPES = (BoolVar,)

def is_boolvar(*x):
    return are_of_type(x, _BOOLVAR_TYPES)

def is_boolvars(x):
    is_vectoid_of_type(x, _BOOLVAR_TYPES)

_SETVAR_TYPES = (SetVar,)

def is_setvar(*x):
    return are_of_type(x, _SETVAR_TYPES)

def is_setvars(x):
    return is_vectoid_of_type(x, _SETVAR_TYPES)

_INTEGER_TYPES = (int,)

def is_integer(*x):
    return are_of_type(x, _INTEGER_TYPES)

def is_integers(x):
    return is_vectoid_of_type(x, _INTEGER_TYPES)

#==============================================================================
# functions
#==============================================================================

def sum(x,y=None):
    if y is None:
        if is_boolvars(x):
            return BExprSUM(x)
        if is_intvars(x):
            return IExprSUM(x)
        raise TypeError("sum(%s)" % x)
    elif not is_integers(x):
        raise TypeError("sum(%s,%s)" % (x,y))
    elif is_boolvars(y):
        return BExprSUM2(x,y)
    elif is_intvars(y):
        return IExprSUM2(x,y)
    else:
        raise TypeError("sum(%s,%s)" % (x,y))

_saved_min = min

def min(x,y=None):
    if y is None:
        if is_set(x):
            return SExprMIN(x)
        if is_intvars(x):
            return IExprMIN(x)
        return _saved_min(x)
    if is_integer(x,y):
        return _saved_min(x,y)
    if is_int(x,y):
        return IExprMIN2(x,y)
    return _saved_min(x,y)

_saved_max = max

def max(x,y=None):
    if y is None:
        if is_set(x):
            return SExprMAX(x)
        if is_intvars(x):
            return IExprMAX(x)
        return _saved_max(x)
    if is_integer(x,y):
        return _saved_max(x,y)
    if is_int(x,y):
        return IExprMAX2(x,y)
    return _saved_max(x,y)

_saved_abs = abs

def abs(x):
    if is_integer(x):
        return _saved_abs(x)
    if is_int(x):
        return IExprABS(x)
    return _saved_abs(x)

def sqr(x):
    if is_integer(x):
        return x*x
    if is_int(x):
        return IExprSQR(x)
    raise TypeError("sqr(%s)" % x)

def sqrt(x):
    if is_int(x):
        return IExprSQRT(x)
    raise TypeError("sqrt(%s)" % x)

def cardinality(x):
    if is_set(x):
        return SExprCARD(x)
    type TypeError("cardinality(%s)" % x)

def element(x,y):
    if not is_int(x):
        raise TypeError("element(%s,%s)" % (x,y))
    if is_ints(x):
        return IExprELEM(x,y)
    if is_sets(x):
        return SExprELEM(x,y)
    raise TypeError("element(%s,%s)" % (x,y))

def setinter(x,y=None):
    if not is_sets(x):
        if y is None:
            raise TypeError("setinter(%s)" % x)
        else:
            raise TypeError("setinter(%s,%s)" % (x,y))
    if y is None:
        return SExprELEMINTER(x)
    if is_set(y):
        return SExprELEMINTER2(x,y)
    raise TypeError("setinter(%s,%s)" % (x,y))xs

inter = setinter

def setunion(x,y=None):
    if not is_sets(x):
        if y is None:
            raise TypeError("setunion(%s)" % x)
        else:
            raise TypeError("setunion(%s,%s)" % (x,y))
    if y is None:
        return SExprELEMUNION(x)
    if is_set(y):
        return SExprELEMUNION2(x,y)
    raise TypeError("setunion(%s,%s)" % (x,y))

union = setunion

def setdunion(x,y=None):
    if not is_sets(x):
        if y is None:
            raise TypeError("setdunion(%s)" % x)
        else:
            raise TypeError("setdunion(%s,%s)" % (x,y))
    if y is None:
        return SExprDUNION(x)
    if is_set(y):
        return SEXprDUNION2(x,y)
    raise TypeError("setdunion(%s,%s)" % (x,y))

dunion = setdunion

def singleton(x):
    if is_int(x):
        return SExprSINGLETON(x)
    raise TypeError("singleton(%s)" % x)
