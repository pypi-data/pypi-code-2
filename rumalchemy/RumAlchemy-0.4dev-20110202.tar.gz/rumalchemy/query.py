# -*- coding: utf-8 -*-

from sqlalchemy import sql, types
from rum import query as rumquery
from rum.genericfunctions import generic

from rumalchemy.util import get_mapper, primary_key_property_names,\
    get_dialect_name, get_other
from re import sub
from sqlalchemy.orm import aliased, eagerload_all
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty

_escape_char="0"
def _escape_pattern(p):
    p=p.replace(_escape_char,2*_escape_char)
    pattern=r'(%|_)'
    rep=_escape_char+r'\g<1>'
    return sub(pattern,rep,p)


    

class SAQuery(rumquery.Query):
    """Creates SA queries"""

    def filter(self, query):
        assert self.resource
        if self.expr is not None:
            query = self._apply_expression(query)
        self.count = query.count()
        if self.sort is not None:
            query = self._apply_sort(query)
        else:
            query=self.apply_default_ordering(query)
        
        query=self._apply_joins(query)
        if self.limit is not None:
            query = self._apply_limit(query)
        if self.offset is not None:
            query = self._apply_offset(query)
        query = self.set_query_options(query)
        return query

    
    def __init__(self, expr=None, sort=None, limit=None, offset=None, resource=None,join=[]):
        super(SAQuery, self).__init__(expr=expr, sort=sort, limit=limit, offset=offset, resource=resource, join=join)
        self.joins=dict()
    
    @generic
    def apply_default_ordering(self,query):
        """applies a default ordering to query"""
        pass
        
    @generic
    def remap_sort_column(self, col):
        pass
    
    @generic
    def translate(self, expr, resource, query):
        """
        Translate a :meth:`rum.query.Expression` into an sqlalchemy sql expression.
        """
    
    @remap_sort_column.when()
    def _default_criterium_for_field(self, col):
        return col
        
    apply_default_ordering.when()
    def _apply_default_ordering(self, query):
        r=self.resource
        return query.order_by(*[self.get_column(r,n, query) for n in primary_key_property_names(r)])
        
    @generic
    def set_query_options(self, query):
        """
        Apply sqlalchemy options like eagerload to query
        """
    
    set_query_options.when()
    def __default_query_options(self, query):
        for j in self.join:
            query=query.options(eagerload_all(j))
        return query
    def _apply_offset(self, query):
        return query.offset(self.offset)

    def _apply_limit(self, query):
        return query.limit(self.limit)

    def _apply_sort(self, query):
        r = self.resource
        return query.order_by(*[
            getattr(sql, s.name)(self.get_column(r, 
            self.remap_sort_column(s.col), query))
            for s in self.sort
            ])

    def _apply_expression(self, query):
        filter_expr=self.translate(self.expr, self.resource, query)


        
        return query.filter(filter_expr)
    def _apply_joins(self, query):
        def sort_key(dict_entry):
            (key, value)=dict_entry
            return len(key)
        joins_list=sorted(self.joins.iteritems(), key=sort_key)

        for (stack, resource) in joins_list:
            (parent, attr) = stack[-1]
            query = query.join((resource, getattr(parent, attr)))
        return query
    @translate.when((rumquery.eq,))
    def _eq(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) == expr.arg

    @translate.when((rumquery.neq,))
    def _neq(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) != expr.arg

    @translate.when((rumquery.contains,))
    def _contains(self, expr, resource, query):
        pattern = _escape_pattern(expr.arg)
        return normalize(self.get_column(resource, expr.col, query)).contains(normalize(pattern), escape=_escape_char)

    @translate.when((rumquery.startswith,))
    def _startswith(self, expr, resource, query):
        pattern = _escape_pattern(expr.arg)
        return normalize(self.get_column(resource, expr.col, query)).startswith(normalize(pattern), escape=_escape_char)

    @translate.when((rumquery.endswith,))
    def _endswith(self, expr, resource, query):
        pattern = _escape_pattern(expr.arg)
        return normalize(self.get_column(resource, expr.col, query)).endswith(normalize(pattern), escape=_escape_char)

    @translate.when((rumquery.and_,))
    def _and(self, expr, resource, query):
        return sql.and_(*[self.translate(e, resource, query) for e in expr.col])

    @translate.when((rumquery.or_,))
    def _or(self, expr, resource, query):
        return sql.or_(*[self.translate(e, resource, query) for e in expr.col])

    @translate.when((rumquery.lt,))
    def _lt(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) < expr.arg

    @translate.when((rumquery.lte,))
    def _lte(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) <= expr.arg

    @translate.when((rumquery.gt,))
    def _gt(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) > expr.arg

    @translate.when((rumquery.gte,))
    def _gte(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) >= expr.arg

    @translate.when(
        "isinstance(expr, rumquery.not_) and isinstance(expr.col, basestring)")
    def _not_col_name(self, expr, resource, query):
        return sql.not_(self.get_column(resource, expr.col, query))

    @translate.when(
        "isinstance(expr, rumquery.not_) and "
        "isinstance(expr.col, rumquery.Expression)")
    def _not_expr(self, expr, resource, query):
        return sql.not_(self.translate(expr.col, resource, query))

    @translate.when((rumquery.notnull,))
    def _notnull(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) != None

    @translate.when((rumquery.null,))
    def _null(self, expr, resource, query):
        return self.get_column(resource, expr.col, query) == None

    @translate.when((rumquery.in_,))
    def _in(self, expr, resource, query):
        return self.get_column(resource, expr.col, query).in_(expr.arg)
    
    def get_column(self, resource, column_name, query):
        resource_pure=resource
        columns=column_name.split(".")
        stack= ()
        for i in xrange(len(columns)-1):
            parent_pure=resource_pure
            parent=resource
            attr=columns[i]
            stack=stack + ((parent, attr),)
            
            
            prop = get_mapper(parent_pure).get_property(attr)
            if isinstance(prop, RelationshipProperty):
                resource_pure = get_other(prop)
                if stack in self.joins:
                    resource = self.joins[stack]
                else:
                    resource = aliased(resource_pure)
                    self.joins[stack] = resource
            else:
                resource_pure = resource = getattr(parent, attr)
            
        col=columns[-1]
        
        is_date = hasattr(resource, 'property')\
            and isinstance(resource.property, ColumnProperty)\
            and not isinstance(resource.property, RelationshipProperty)\
            and hasattr(resource.property, 'columns')\
            and (
                isinstance(resource.property.columns[0].type, types.Date)
                or 
                isinstance(resource.property.columns[0].type, types.DateTime))

        if not is_date:
            return getattr(resource, col)
        else:
            return date_part(col, resource)

rumquery.QueryFactory.register(SAQuery, pred = "get_mapper(resource) is not None")
apply_default_ordering = SAQuery.apply_default_ordering.im_func
set_query_options = SAQuery.set_query_options.im_func


lower = sql.func.lower


@generic
def date_part(part, date_col):
    "generate sql expression representing day/month/year part or date_col, part is passed as a string, e.g. 'month'"

@date_part.when()
def _date_part_default(part, date_col):
    "default implementation, works at least on postgresql"
    return sql.func.date_part(part, date_col)

@generic 
def normalize(expr):
    "Normalize expression to some standard form"


@normalize.when()
def _lower_case(expr):
    return lower(expr)

@normalize.when("get_dialect_name().lower().startswith('postgres')")
def _lower_and_accents(string):
    translate=sql.func.translate
    replace=sql.func.replace
    return replace(translate(lower(string),'äöüáéíóúàèìòùyw','aouaeiouaeiouiv'),'ß','ss')


remap_sort_column = SAQuery.remap_sort_column.im_func