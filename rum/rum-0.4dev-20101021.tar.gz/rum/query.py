from urllib import urlencode

from formencode import variabledecode
from formencode.validators import Int

from rum.genericfunctions import generic
from rum.basefactory import BaseFactory
from rum import util

class QueryFactory(BaseFactory):
    @generic
    def get(self, resource):
        """
        Returns a :class:`Query` subclass able to handle ``resource``
        """

    # By default return None instead of raising NoApplicableMethods
    get.when()(lambda s,r:None)

    def __call__(self, resource, request_args=None, **kw):
        query_cls = self.get(resource)
        if query_cls:
            if request_args:
                query = query_cls.from_dict(request_args)
            else:
                query = query_cls(**kw)
            query.resource = resource
            return query

@generic
def simplify(obj):
    """Convert an object to an something we can stick into a query string"""

class _QueryElementType(type):
    _types = {}
    def __new__(meta, name, bases, dct):
        if 'name' not in dct:
            dct['name'] = name
        dct['__slots__'] = ('name', 'col', 'arg')
        obj = type.__new__(meta, name, bases, dct)
        meta._types[obj.name] = obj
        return obj

    @classmethod
    def by_name(meta, name):
        return meta._types[name]

class _QueryElement(object):
    __metaclass__ = _QueryElementType

    def __init__(self, col, arg=None):
        self.col = col
        self.arg = arg
    
    def __repr__(self):
        if not self.arg:
            data = '(' + `self.col` + ')'
        else:
            data = `(self.col, self.arg)`
        return self.__class__.__name__ + data
    def __eq__(self,other):
        if self.__class__ ==other.__class__ and\
            self.col==other.col and self.arg==other.arg:
            return True
        else:
            return False
simplify.when()(lambda s: s)
simplify.when((unicode,))(lambda s: s.encode('utf-8'))

@simplify.when((_QueryElement,))
def _simplify_qe(obj):
    return {'o':obj.name, 'c':simplify(obj.col), 'a':simplify(obj.arg)}


@simplify.when((dict,))
def _simplify_dct(obj):
    return dict((k, simplify(v)) for (k,v) in obj.iteritems())

@simplify.when((list,))
@simplify.when((tuple,))
def _simplify_list(obj):
    return map(simplify, obj)



class _sort(_QueryElement):
    @classmethod
    def from_dict(cls, d):
        cls = cls.by_name(d.get('dir', 'asc'))
        return cls(d['c'])

@simplify.when((_sort,))
def _simplify_sort(obj):
    return {'dir':obj.name, 'c':obj.col}

class asc(_sort):
    """
    Ascending ordering criteria.

    Example, order in ascending order by attribute ``name``::

        >>> asc('name')
        asc('name')
   """

class desc(_sort):
    """
    Descending ordering criteria.

    Example, order in descending order by attribute ``age``::

        >>> desc('age')
        desc('age')
   """


def _maybe_unicode(s):
    if isinstance(s, str):
        try:
            s.decode('ascii')
        except UnicodeDecodeError:
            s = s.decode('utf-8')
    return s

class Expression(_QueryElement):
    """
    This is a basic expression to build up queries.
    """
    @classmethod
    def from_dict(cls, d):
        if isinstance(d, (list,tuple)):
            return map(cls.from_dict, d)
        if not isinstance(d, dict):
            # stops recursion at leaves
            return d
        cls = cls.by_name(d['o'])
        col = d['c']
        arg = d.get('a')
        args = [col, _maybe_unicode(arg)]
        return cls(*map(cls.from_dict, args))

class and_(Expression):
    """A boolean AND of all arguments"""
    name = 'and'
class or_(Expression):
    """A boolean OR of all arguments"""
    name = 'or'
class eq(Expression):
    """arg1 is equal to"""
class neq(Expression):
    """arg 1 is not equal to"""
class lt(Expression):
    """arg1 is less than arg2"""
class lte(Expression):
    """arg1 is less than or equal arg2"""
class gt(Expression):
    """arg1 is greater than arg2"""
class gte(Expression):
    """arg1 is greater than or equal arg2"""
class not_(Expression):
    """Negates arg1"""
    name = 'not'
class startswith(Expression):
    """arg1 starts with arg2"""
class endswith(Expression):
    """arg1 ends with arg2"""
class contains(Expression):
    """arg1 contains arg2"""
    name = 'contains'
class null(Expression):
    """arg1 is null"""
class notnull(Expression):
    """arg1 is not null"""
class in_(Expression):
    """arg1 is in arg2 (which should be a sequence)"""



class Query(object):
    """
    A base query object.

    This object serves as a layer to decouple a query from the web in the form
    of query-string args into an internal object which
    :class:`rum.interfaces.IRepository` use to filter the collection of objects.

    It is the responsability of the :class:`rum.interfaces.IRepository` to
    translate this object into a query the underlying data backend undersands.

    **Parameters**
    
    `expr`
        An :class:`Expression` object.
    `sort`
        A :class:`asc` or a :class:`desc` object or list of objects representing
        the sorting criteria for each attribute
    `limit`
        Tells the :class:`rum.interfaces.IRepository` to return `limit` objects
        the most.
    `offset`
        Tells the :class:`rum.interfaces.IRepository` to begin returning objects
        from this
        offset.

    Examples::

        >>> # A simple query: "name == Alberto"

        >>> q = Query(eq('name', 'Alberto'))
        >>> q
        Query(eq('name', 'Alberto'), None, None, None)

        >>> # Get a query string

        >>> q.as_qs()
        'q.o=eq&q.a=Alberto&q.c=name'

        >>> # A query can be converted to a urlencodable dict and back

        >>> Query.from_dict(q.as_dict())
        Query(eq('name', 'Alberto'), None, None, None)

        >>> # A more complex query: "name == 'Alberto' and (20 < age < 30)" with
        >>> # sorting criteria, offset and limit

        >>> q = Query(and_([eq('name', 'Alberto'), or_([gt('age', 20), lt('age', 30)])]), [desc('join_date')], 10, 10)
        >>> q
        Query(and_([eq('name', 'Alberto'), or_([gt('age', 20), lt('age', 30)])]), [desc('join_date')], 10, 10)
        >>> Query.from_dict(q.as_dict())
        Query(and_([eq('name', 'Alberto'), or_([gt('age', 20), lt('age', 30)])]), [desc('join_date')], 10, 10)

    """
        


    __slots__ = ('expr', 'sort', 'limit', 'offset', 'count', 'resource')
    count = None
    def __init__(self, expr=None, sort=None, limit=None, offset=None, resource=None):
        self.expr = expr
        self.sort = sort
        self.limit = limit
        self.offset = offset
        self.resource = resource

    def __repr__(self):
        data = (self.expr, self.sort, self.limit, self.offset)
        return self.__class__.__name__ + `data`

    @classmethod
    def from_dict(cls, d):
        """Builds up a :class:`Query` object from a dictionary"""
        expr = sort = limit = offset = None
        d = variabledecode.variable_decode(d)
        if 'q' in d and 'c' in d['q']:
            expr = Expression.from_dict(d['q'])
        if 'sort' in d:
            sort = d['sort']
            if sort:
                sort = map(_sort.from_dict, sort)
        if 'limit' in d:
            limit = Int(min=0).to_python(d['limit'])
        if 'offset' in d:
            offset = Int(min=0).to_python(d['offset'])
        return cls(expr, sort, limit, offset)
        

    def as_dict(self):
        """
        Builds up a dictionary from a :class:`Query` object.

        This condition always holds True ``q == Query.from_dict(q.as_dict())``::

            >>> q = Query(eq('dummy', 2))
            >>> Query.from_dict(q.as_dict())
            Query(eq('dummy', 2), None, None, None)
        """
        d = simplify({
            'q': self.expr,
            'sort': self.sort,
            'limit': self.limit,
            'offset': self.offset,
            })
        return dict((k,v) for (k,v) in d.iteritems() if v is not None)

    def as_flat_dict(self):
        return variabledecode.variable_encode(self.as_dict(),
                                              add_repetitions=False)

    def as_qs(self):
        return urlencode(self.as_flat_dict())
        
    def clone(self, **kw):
        args = dict((k, getattr(self,k)) for k in self.__class__.__slots__)
        args.update(kw)
        return util.adapt_call(self.__class__, **args)

    __str__ = as_qs

    def filter(self, items):
        raise NotImplementedError("I'm an abstract method")


    def add_criteria(self, expr):
        """
        "ands" an expression to this Query's expression returning a new
        Query.
        """
        if self.expr is not None:
            new_expr = and_(self.expr, expr)
        else:
            new_expr = expr
        return self.clone(expr=new_expr)

__all__ = ['Query', 'QueryFactory'] + [
    k for (k,v) in locals().items()
      if isinstance(v, _QueryElementType) and not k.startswith('_')
    ]
