# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Alexis Petrounias.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the author nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Django CTE Trees Models.
"""

__status__ = "Prototype"
__version__ = "0.9.0"
__maintainer__ = ("Alexis Petrounias <www.petrounias.org>", )
__author__ = ("Alexis Petrounias <www.petrounias.org>", )

# Django

from django.core.exceptions import ImproperlyConfigured, FieldError
from django.db import connections
from django.db.models import Model, Manager, ForeignKey
from django.db.models.fields import FieldDoesNotExist
from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from django.db.models.sql.compiler import SQLCompiler
from django.utils.translation import ugettext as _


class CTENodeManager(Manager):
    """ Custom :class:`Manager` which ensures all queries involving
        :class:`CTENode` objects are processed by the custom SQL compiler.
        Additionally, provides tree traversal queries for obtaining node
        children, siblings, ancestors, descendants, and roots.
        
        If your Model inherits from :class:`CTENode` and use your own custom
        :class:`Manager`, you must ensure the following three:
        
        1) your :class:`Manager` inherits from :class:`CTENodeManager`,
        
        2) if you override the :meth:`get_query_set` method in order to
        return a custom :class:`QuerySet`, then your `QuerySet` must also
        inherit from :class:`CTENodeManager.CTEQuerySet`, and
        
        3) invoke the :meth:`_ensure_parameters` on your :class:`Manager`
        at least once before using a :class:`QuerySet` which inherits from
        :class:`CTENodeManager.CTEQuerySet`, unless you have supplied the
        necessary CTE node attributes on the :class:`CTENode` :class:`Model` in
        some other way.
            
        The methods :meth:`prepare_delete`, :meth:`prepare_delete_pharaoh`,
        :meth:`prepare_delete_grandmother`, and
        :meth:`prepare_delete_monarchy` can be directly used to prepare
        nodes for deletion with either the default or explicitly-specified
        deletion semantics. The :class:`CTENode` abstract :class:`Model`
        defines a :meth:`CTENode.delete` method which delegates preparation
        to this manager.
        
    """
    
    class CTEQuerySet(QuerySet):
        
        class CTEQuery(Query):
            
            class CTEQueryCompiler(SQLCompiler):
                
                CTE = """WITH RECURSIVE {cte} (
           "{depth}", "{path}", "{ordering}", "{pk}") AS (
                
    SELECT 1 AS depth,
           array[{pk_path}] AS {path},
           {order} AS {ordering},
           T."{pk}"
     FROM  {db_table} T
     WHERE T."{parent}" IS NULL

     UNION ALL

    SELECT {cte}.{depth} + 1 AS {depth},
           {cte}.{path} || {pk_path},
           {cte}.{ordering} || {order},
           T."{pk}"
     FROM  {db_table} T
     JOIN  {cte} ON T."{parent}" = {cte}."{pk}")
    
    """
    
                def as_sql(self, *args, **kwargs):
                    """ Overrides the :class:`SQLCompiler` method in order to
                        prepend the necessary CTE to the default SQL.
                    """
                    
                    # If the Query was cloned in order to implement a statement
                    # other than SELECT, then we don't modify the SQL at all.
                    if not self.__class__ == \
                        CTENodeManager.CTEQuerySet.CTEQuery.CTEQueryCompiler:
                        return super(self.__class__, self).as_sql(*args,
                            **kwargs)
                    
                    def maybe_alias(table):
                        if self.query.table_map.has_key(table):
                            return self.query.table_map[table][0]
                        return table
                    
                    # Add the CTE implicit join, noting any aliasing which may
                    # have occurred during query construction.
                    where = ['{cte}."{pk}" = {table}."{pk}"'.format(
                        cte = self.query.model._cte_node_table,
                        pk = self.query.model._meta.pk.attname,
                        table = maybe_alias(self.query.model._meta.db_table))]
                    
                    self.query.add_extra(
                        select = None,
                        select_params = None,
                        where = where,
                        params = None,
                        tables = [self.query.model._cte_node_table],
                        order_by = None,
                    )
                    
                    # Obtain compiled SQL from Django.
                    sql = super(self.__class__, self).as_sql(*args, **kwargs)
                    

                    def maybe_cast(field):
                        # If the ordering information specified a type to cast
                        # to, then use this type immediately, otherwise
                        # determine whether a variable-length character field
                        # should be cast into TEXT or if no casting is
                        # necessary. A None type defaults to the latter.
                        if type(field) == tuple and not field[1] is None:
                            return 'CAST (T."%s" AS %s)' % field
                        else:
                            if type(field) == tuple:
                                name = field[0]
                            else:
                                name = field
                            if self.query.model._meta.get_field_by_name(name)[
                                0].db_type().startswith('varchar'):
                                return 'CAST (T."%s" AS TEXT)' % name
                            else:
                                return 'T."%s"' % name
                    
                    
                    # The primary key is used in the path; in case it is of a
                    # custom type, ensure appropriate casting is performed. This
                    # is a very rare condition, as most types can be used
                    # directly in the path, especially since no other fields
                    # with incompatible types are combined (with a notable
                    # exception of VARCHAR types which must be converted to
                    # TEXT).
                    pk_path = maybe_cast((self.query.model._meta.pk.attname,
                        self.query.model._cte_node_primary_key_type))
                    
                    # If no explicit ordering is specified, then use the primary
                    # key. If the primary key is used in ordering, and it is of
                    # a type which needs casting in order to be used in the
                    # ordering, then it is possible that explicit casting was
                    # not specified through _cte_node_order_by because it is
                    # expected to be specified through the
                    # _cte_node_primary_key_type attribute. Specifying the cast
                    # type of the primary key in the _cte_node_order_by
                    # attribute has precedence over _cte_node_primary_key_type.
                    if not hasattr(self.query.model, '_cte_node_order_by') or \
                        self.query.model._cte_node_order_by is None or \
                        len(self.query.model._cte_node_order_by) == 0:
                        
                        order = 'array[%s]' % maybe_cast((
                            self.query.model._meta.pk.attname,
                            self.query.model._cte_node_primary_key_type))
                        
                    else:
                        
                        # Compute the ordering virtual field constructor,
                        # possibly casting fields into a common type.
                        order = '||'.join(['array[%s]' % maybe_cast(field) for \
                            field in self.query.model._cte_node_order_by])
                    
                    # Prepend the CTE with the ordering constructor and table
                    # name to the SQL obtained from Django above.
                    return (''.join([
                        self.CTE.format(order = order,
                            cte = self.query.model._cte_node_table,
                            depth = self.query.model._cte_node_depth,
                            path = self.query.model._cte_node_path,
                            ordering = self.query.model._cte_node_ordering,
                            parent = self.query.model._cte_node_parent_attname,
                            pk = self.query.model._meta.pk.attname,
                            pk_path = pk_path,
                            db_table = self.query.model._meta.db_table
                        ), sql[0]]), sql[1])
                    
                    
            def get_compiler(self, using = None, connection = None):
                """ Overrides the Query method get_compiler in order to return
                    an instance of the above custom compiler.
                """
                
                # Copy the body of this method from Django except the final
                # return statement. We will ignore code coverage for this.
                if using is None and connection is None: #pragma: no cover
                    raise ValueError("Need either using or connection")
                if using:
                    connection = connections[using]
        
                # Check that the compiler will be able to execute the query
                for alias, aggregate in self.aggregate_select.items():
                    connection.ops.check_aggregate_support(aggregate)
                
                # Instantiate the custom compiler.
                return self.CTEQueryCompiler(self, connection, using)
            
        
        def __init__(self, model = None, query = None, using = None,
            offset = None):
            """ Provides an additional argument offset for use in obtaining the
                descendants of a node; this argument should contain a valid
                Node. This QuerySet will return an instance of the above custom
                Query, which can, however, be used as a normal Query (for
                instance chaining with other queries).
            """
            
            # Only create an instance of a Query if this is the first invocation
            # in a query chain.
            if query is None:
                
                query = CTENodeManager.CTEQuerySet.CTEQuery(model)
                
                if not model is None:
                    
                    where = []
                    
                    # If an offset Node is specified, then only those Nodes
                    # which contain the offset Node as a parent (in their path
                    # virtual field) will be returned.
                    if not offset is None:
                        
                        where.append("""NOT {cte}."{pk}" = '{id}'""".format(
                            cte = model._cte_node_table,
                            pk = model._meta.pk.attname,
                            id = str(offset.id)))
                        
                        where.append("""'{id}' = ANY({cte}."{path}")""".format(
                            cte = model._cte_node_table,
                            path = model._cte_node_path,
                            id = str(offset.id)))
                    
                    order_by_prefix = []
                    
                    if model._cte_node_traversal == \
                        CTENodeManager.TREE_TRAVERSAL_NONE:
                        chosen_traversal = CTENodeManager.DEFAULT_TREE_TRAVERSAL
                    else:
                        chosen_traversal = model._cte_node_traversal
                        
                    if chosen_traversal == CTENodeManager.TREE_TRAVERSAL_DFS:
                        order_by_prefix = [ model._cte_node_ordering ]
                    if chosen_traversal == CTENodeManager.TREE_TRAVERSAL_BFS:
                        order_by_prefix = [ model._cte_node_depth,
                            model._cte_node_ordering ]
                        
                    order_by = order_by_prefix
                    
                    if hasattr(model, '_cte_node_order_by') and \
                        not model._cte_node_order_by is None and \
                        len(model._cte_node_order_by) > 0:
                        
                        order_by.extend([field[0] if type(field) == tuple else \
                            field for field in model._cte_node_order_by])
                    
                    # Specify the virtual fields for depth, path, and ordering;
                    # optionally the offset Node constraint; and the desired
                    # ordering. The CTE table will be added later by the
                    # Compiler only if the actual query is a SELECT.
                    query.add_extra(
                        select = {
                            model._cte_node_depth : model._cte_node_depth,
                            model._cte_node_path : model._cte_node_path,
                            model._cte_node_ordering : model._cte_node_ordering,
                        },
                        select_params = None,
                        where = where,
                        params = None,
                        tables = None,          # Will be added by the Compiler.
                        order_by = order_by,
                    )
            
            super(CTENodeManager.CTEQuerySet, self).__init__(model, query,
                using)
            
    
    # SQL CTE temporary table name.
    
    DEFAULT_TABLE_NAME = 'cte'
    
    DEFAULT_CHILDREN_NAME = 'children'
    
    
    # Tree traversal semantics.
    
    TREE_TRAVERSAL_NONE = 'none'
    
    TREE_TRAVERSAL_DFS = 'dfs'
    
    TREE_TRAVERSAL_BFS = 'bfs'
    
    TREE_TRAVERSAL_METHODS = (TREE_TRAVERSAL_NONE, TREE_TRAVERSAL_DFS,
        TREE_TRAVERSAL_BFS)
    
    TREE_TRAVERSAL_CHOICES = (
        (TREE_TRAVERSAL_NONE, _('none')),
        (TREE_TRAVERSAL_DFS, _('depth first search')),
        (TREE_TRAVERSAL_BFS, _('breadth first search')),
    )
    
    DEFAULT_TREE_TRAVERSAL = TREE_TRAVERSAL_DFS
    
    
    # Virtual fields.
    
    VIRTUAL_FIELD_DEPTH = 'depth'
    
    VIRTUAL_FIELD_PATH = 'path'
    
    VIRTUAL_FIELD_ORDERING = 'ordering'
    
    
    # Deletion semantics.
    
    DELETE_METHOD_NONE = 'none'
    
    DELETE_METHOD_PHARAOH = 'pharaoh'
    
    DELETE_METHOD_GRANDMOTHER = 'grandmother'
    
    DELETE_METHOD_MONARCHY = 'monarchy'
    
    DELETE_METHODS = (DELETE_METHOD_NONE, DELETE_METHOD_PHARAOH,
        DELETE_METHOD_GRANDMOTHER, DELETE_METHOD_MONARCHY)
    
    DELETE_METHOD_CHOICES = (
        (DELETE_METHOD_NONE, _('none')),
        (DELETE_METHOD_PHARAOH, _('pharaoh (all subtree)')),
        (DELETE_METHOD_GRANDMOTHER, _('grandmother (move subtree up)')),
        (DELETE_METHOD_MONARCHY,
         _('monarchy (first child becomes subtree root)')),
    )
    
    DEFAULT_DELETE_METHOD = DELETE_METHOD_PHARAOH
    
     
    # Related manager lookup should return this custom Manager in order to use
    # the custom QuerySet above.
    use_for_related_fields = True
    
    
    def _ensure_parameters(self):
        """ Attempts to load and verify the CTE node parameters. Will use
            default values for all missing parameters, and raise an exception if
            a parameter's value cannot be verified. This method will only
            perform these actions once, and set the :attr:`_parameters_checked`
            attribute to ``True`` upon its first success.
        """
        
        if hasattr(self, '_parameters_checked'):
            return
        
        if not hasattr(self.model, '_cte_node_table') or \
            self.model._cte_node_table is None:
            setattr(self.model, '_cte_node_table',
                self.DEFAULT_TABLE_NAME)
            
        if not hasattr(self.model, '_cte_node_depth') or \
            self.model._cte_node_depth is None:
            setattr(self.model, '_cte_node_depth',
                self.VIRTUAL_FIELD_DEPTH)
        
        if not hasattr(self.model, '_cte_node_path') or \
            self.model._cte_node_depth is None:
            setattr(self.model, '_cte_node_path',
                self.VIRTUAL_FIELD_PATH)
        
        if not hasattr(self.model, '_cte_node_ordering') or \
            self.model._cte_node_ordering is None:
            setattr(self.model, '_cte_node_ordering',
                self.VIRTUAL_FIELD_ORDERING)
        
        if not hasattr(self.model, '_cte_node_traversal') or \
            self.model._cte_node_traversal is None:
            setattr(self.model, '_cte_node_traversal',
                self.DEFAULT_TREE_TRAVERSAL)
        
        if not hasattr(self.model, '_cte_node_children') or \
            self.model._cte_node_children is None:
            setattr(self.model, '_cte_node_children',
                self.DEFAULT_CHILDREN_NAME)
            
        if not hasattr(self.model, '_cte_node_primary_key_type'):
            setattr(self.model, '_cte_node_primary_key_type', None)
            
        # Determine the parent foreign key field name, either
        # explicitly specified, or the first foreign key to 'self'.
        # If we need to determine, then we set the attribute for future
        # reference.
        if not hasattr(self.model, '_cte_node_parent') or \
            self.model._cte_node_parent is None:
            found = False
            for f in self.model._meta.fields:
                if isinstance(f, ForeignKey):
                    if f.rel.to == self.model:
                        setattr(self.model, '_cte_node_parent', f.name)
                        found = True
            if not found:
                raise ImproperlyConfigured(
                    _('CTENode must have a Foreign Key to self for the parent relation.'))
        
        try:
            parent_field = self.model._meta.get_field_by_name(
                self.model._cte_node_parent)[0]
        except FieldDoesNotExist:
            raise ImproperlyConfigured(''.join([
                _('CTENode._cte_node_parent must specify a Foreign Key to self, instead it is: '),
                self.model._cte_node_parent]))
        
        # Ensure parent relation is a Foreign Key to self.
        if not parent_field.rel.to == self.model:
            raise ImproperlyConfigured(''.join([
                _('CTENode._cte_node_parent must specify a Foreign Key to self, instead it is: '),
                self.model._cte_node_parent]))
        
        # Record the parent field attribute name for future reference.
        setattr(self.model, '_cte_node_parent_attname',
            self.model._meta.get_field_by_name(
                self.model._cte_node_parent)[0].attname)
            
        # Ensure traversal choice is valid.
        traversal_choices = [choice[0] for choice in \
            self.TREE_TRAVERSAL_CHOICES]
        if not self.model._cte_node_traversal in traversal_choices:
            raise ImproperlyConfigured(
                ' '.join(['CTENode._cte_node_traversal must be one of [',
                    ', '.join(traversal_choices), ']; instead it is:',
                    self.model._cte_node_traversal]))
        
        # Ensure delete choice is valid.
        if not hasattr(self.model, '_cte_node_delete_method') or \
            self.model._cte_node_delete_method is None:
            setattr(self.model, '_cte_node_delete_method',
                self.DEFAULT_DELETE_METHOD)
        else:
            # Ensure specified method is valid.
            method_choices = [dm[0] for dm in \
                self.DELETE_METHOD_CHOICES]
            if not self.model._cte_node_delete_method in method_choices:
                raise ImproperlyConfigured(
                    ' '.join(['delete method must be one of [',
                        ', '.join(method_choices), ']; instead it is:',
                        self.model._cte_node_delete_method]))
            
        setattr(self, '_parameters_checked', True)
                        
    
    def _ensure_virtual_fields(self, node):
        """ Attempts to read the virtual fields from the given `node` in order
            to ensure they exist, resulting in an early :class:`AttributeError`
            exception in case of missing virtual fields. This method requires
            several parameters, and thus invoked :meth:`_ensure_parameters`
            first, possibly resulting in an :class:`ImproperlyConfigured`
            exception being raised.
            
            :param node: the :class:`CTENode` for which to verify that the
                virtual fields are present.
        """
        
        # Uses several _cte_node_* parameters, so ensure they exist. 
        self._ensure_parameters()
        
        for vf in [self.model._cte_node_depth, self.model._cte_node_path,
            self.model._cte_node_ordering]:
            
            if not hasattr(node, vf):
                
                raise FieldError(
                    _('CTENode objects must be loaded from the database before they can be used.'))
                    
                                          
    def get_query_set(self):
        """ Returns a custom :class:`QuerySet` which provides the CTE
            functionality for all queries concerning :class:`CTENode` objects.
            This method overrides the default :meth:`get_query_set` method of
            the :class:`Manager` class.
            
            :returns: a custom :class:`QuerySet` which provides the CTE
                functionality for all queries concerning :class:`CTENode`
                objects.
        """
        
        # The CTEQuerySet uses _cte_node_* attributes from the Model, so ensure
        # they exist.
        self._ensure_parameters()
        
        return self.CTEQuerySet(self.model, using = self._db)
    
    
    def roots(self):
        """ Returns a :class:`QuerySet` of all root :class:`CTENode` objects.
        
            :returns: a :class:`QuerySet` of all root :class:`CTENode` objects.
        """
    
        # We need to read the _cte_node_parent attribute, so ensure it exists.
        self._ensure_parameters()
        
        # We need to construct: self.filter(parent = None)
        return self.filter(**{ self.model._cte_node_parent : None})
    
    
    def leaves(self):
        """ Returns a :class:`QuerySet` of all leaf nodes (nodes with no
            children).
            
            :return: A :class:`QuerySet` of all leaf nodes (nodes with no
                children.
        """
        
        # We need to read the _cte_node_children attribute, so ensure it exists.
        self._ensure_parameters()
        
        return self.filter().exclude(**{
            '%s__id__in' % self.model._cte_node_children : self.all(),
        })
    
    
    def root(self, node):
        """ Returns the :class:`CTENode` which is the root of the tree in which
            the given `node` participates (or `node` if it is a root node). This
            method functions through the :meth:`get` method.
            
            :param node: A :class:`CTENode` whose root is required.
            
            :return: A :class:`CTENode` which is the root of the tree in which
                the given `node` participates (or the given `node` if it is a
                root node).
        """
        
        # We need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)
        
        return self.get(pk = getattr(node, self.model._cte_node_path)[0])
    
    
    def siblings(self, node):
        """ Returns a :class:`QuerySet` of all siblings of a given
            :class:`CTENode` `node`.
        
            :param node: a :class:`CTENode` whose siblings are required.
            
            :returns: A :class:`QuerySet` of all siblings of the given `node`.
        """
        
        # We need to read the _cte_node_parent* attributes, so ensure they
        # exist.
        self._ensure_parameters()
        
        # We need to construct: filter(parent = node.parent_id)
        return self.filter(**{ self.model._cte_node_parent : \
            getattr(node, self.model._cte_node_parent_attname) }).exclude(
                id = node.id)
    
    
    def ancestors(self, node):
        """ Returns a :class:`QuerySet` of all ancestors of a given
            :class:`CTENode` `node`.
        
            :param node: A :class:`CTENode` whose ancestors are required.
            
            :returns: A :class:`QuerySet` of all ancestors of the given `node`.
        """
        
        # We need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)
        
        return self.filter(
            pk__in = getattr(node, self.model._cte_node_path)[:-1])
    
        
    def descendants(self, node):
        """ Returns a :class:`QuerySet` with all descendants for a given
            :class:`CTENode` `node`.
        
            :param node: the :class:`CTENode` whose descendants are required.
            
            :returns: A :class:`QuerySet` with all descendants of the given
                `node`.
        """
        
        # We need to read the _cte_node_* attributes, so ensure they exist.
        self._ensure_parameters()
        
        # This is implemented in the CTE WHERE logic, so we pass a reference to
        # the offset CTENode to the custom QuerySet, which will process it.
        return self.CTEQuerySet(self.model, using = self._db, offset = node)
    
    
    def is_parent_of(self, node, subject):
        """ Returns ``True`` if the given `node` is the parent of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`parent` field, and so does not perform any query.
            
            :param node: the :class:`CTENode' for which to determine whether it
                is a parent of the `subject`.
                
            :param subject: the :class:`CTENode` for which to determine whether
                its parent is the `node`.
                
            :returns: ``True`` if `node` is the parent of `subject`, ``False``
                otherwise.
        """
        
        return subject.parent_id == node.id
    
    
    def is_child_of(self, node, subject):
        """ Returns ``True`` if the given `node` is a child of the given
            `subject` node, ``False`` otherwise. This method used the
            :attr:`parent` field, and so does not perform any query.
            
            :param node: the :class:`CTENode' for which to determine whether it
                is a child of the `subject`.
                
            :param subject: the :class:`CTENode` for which to determine whether
                one of its children is the `node`.
                
            :returns: ``True`` if `node` is a child of `subject`, ``False``
                otherwise.
        """
        
        return node.parent_id == subject.id
    
    
    def is_sibling_of(self, node, subject):
        """ Returns ``True`` if the given `node` is a sibling of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`parent` field, and so does not perform any query.
            
            :param node: the :class:`CTENode' for which to determine whether it
                is a sibling of the `subject`.
                
            :param subject: the :class:`CTENode` for which to determine whether
                one of its siblings is the `node`.
                
            :returns: ``True`` if `node` is a sibling of `subject`, ``False``
                otherwise.
        """
        
        # Ensure nodes are not siblings of themselves.
        return not node.id == subject.id and node.parent_id == subject.parent_id
    
    
    def is_ancestor_of(self, node, subject):
        """ Returns ``True`` if the given `node` is an ancestor of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`path` virtual field, and so does not perform any query.
            
            :param node: the :class:`CTENode' for which to determine whether it
                is an ancestor of the `subject`.
                
            :param subject: the :class:`CTENode` for which to determine whether
                one of its ancestors is the `node`.
                
            :returns: ``True`` if `node` is an ancestor of `subject`, ``False``
                otherwise.
        """
        
        # We will need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)
        
        # Convenience check so is_ancestor_of can be combined with methods
        # returning nodes without the caller having to worry about a None
        # subject.
        if subject is None:
            
            return False
        
        # Optimization: a node will never be an ancestor of a root node.
        if subject.depth == 1:
            
            return False
        
        # The path will either be an index of primitives, or an encoding of an
        # array.
        if type(node.path) == list:
            
            # We can slice with -1 because we know that depth > 1 from above.
            return node.id in subject.path[0:-1]
        
        else:
            
            # Search for node id up to the penultimate entry in the path of the
            # subject, meaning we ignore the end of the path consisting of:
            # a) the ending closing curly brace,
            # b) the length of the subject id, and
            # c) the separator character,
            # therefore we look for a match ending at the length of the
            # subject's id string plus two (so negative index length minus two).
            return subject.path[:-len(str(subject.id)) - 2].index(
                str(node.id)) > 0
    
    
    def is_descendant_of(self, node, subject):
        """ Returns ``True`` if the given `node` is a descendant of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`path` virtual field, and so does not perform any query.
            
            :param node: the :class:`CTENode' for which to determine whether it
                is a descendant of the `subject`.
                
            :param subject: the :class:`CTENode` for which to determine whether
                one of its descendants is the `node`.
                
            :returns: ``True`` if `node` is a descendant of `subject`, ``False``
                otherwise.
        """
        
        # We will need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)
        
        # Convenience check so is_descendent_of can be combined with methods
        # returning nodes without the caller having to worry about a None
        # subject.
        if subject is None:
            
            return False
        
        # Optimization: a root node will never be a descendant of any node.
        if node.depth == 1:
            
            return False
        
        # The path will either be an index of primitives, or an encoding of an
        # array.
        if type(node.path) == list:
            
            # We can slice with -1 because we know that depth > 1 from above.
            return subject.id in node.path[0:-1]
        
        else:
            
            # Search for subject id up to the penultimate entry in the path of
            # the node, meaning we ignore the end of the path consisting of:
            # a) the ending closing curly brace,
            # b) the length of the node id, and
            # c) the separator character,
            # therefore we look for a match ending at most at the length of the
            # node's id string plus two (so negative index length minus two).
            return node.path[:-len(str(node.id)) - 2].index(str(subject.id)) > 0
    
    
    def is_leaf(self, node):
        """ Returns ``True`` if the given `node` is a leaf (has no children),
            ``False`` otherwise.
            
            :param node: the :class:`CTENode` for which to determine whether it
                is a leaf.
                
            :return: ``True`` if `node` is a leaf, ``False`` otherwise.
        """
        
        return not node.children.exists()
    
    
    def prepare_delete(self, node, method, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the required deletion semantics (Pharaoh, Grandmother, or Monarchy).
            
            The `method` argument can be one of the valid
            :const:`DELETE_METHODS` choices. If it is
            :const:`DELETE_METHOD_NONE` or ``None``, then the default delete
            method will be used (as specified from the optional
            :attr:`_cte_node_delete_method`).
            
            Under the :const:`DELETE_METHOD_GRANDMOTHER` and
            :const:`DELETE_METHOD_MONARCHY` delete semantics, descendant nodes
            may be moved; in this case the optional `position` can be a
            ``callable`` which is invoked prior to each move operation (see
            :meth:`move` for details).
            
            Furthermore, by default, after each move operation, sub-tree nodes
            which were moved will be saved through a call to :meth:`Model.save`
            unless `save` is ``False``.
            
            This method delegates move operations to :meth:`move`.
            
            :param node: the :class:`CTENode` to prepare for deletion.
            
            :param method: optionally, a delete method to use.
            
            :param position: optionally, a ``callable`` to invoke prior to each
                move operation.
                
            :param save: flag indicating whether to save after each move
                operation, ``True`` by default.
        """
    
        # If no delete method preference is specified, use attribute.
        if method is None:
            method = node._cte_node_delete_method
            
        # If no preference specified, use default.
        if method == self.DELETE_METHOD_NONE:
            method = self.DEFAULT_DELETE_METHOD
                
        # Delegate to appropriate method.
        getattr(self, 'prepare_delete_%s' % method)(node, position, save)
        
    
    def prepare_delete_pharaoh(self, node, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the :const:`DELETE_METHOD_PHARAOH` semantics.
            
            This method does not perform any sub-tree reorganization, and hence
            no move operation, so the `position` and `save` arguments are
            ignored; they are present for regularity purposes with the rest of
            the deletion preparation methods.
            
            :param node: the :class:`CTENode` to prepare for deletion.
            
            :param position: this is ignored, but present for regularity.
                
            :param save: this is ignored, but present for regularity.
        """
        
        # Django will take care of deleting the sub-tree through the reverse
        # Foreign Key parent relation.
        pass
    
    
    def prepare_delete_grandmother(self, node, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the :const:`DELETE_METHOD_GRANDMOTHER` semantics. Descendant nodes,
            if present, will be moved; in this case the optional `position` can
            be a ``callable`` which is invoked prior to each move operation (see
            :meth:`move` for details).
            
            By default, after each move operation, sub-tree nodes which were
            moved will be saved through a call to :meth:`Model.save` unless
            `save` is ``False``.
            
            This method delegates move operations to :meth:`move`.
            
            :param node: the :class:`CTENode` to prepare for deletion.
            
            :param position: optionally, a ``callable`` to invoke prior to each
                move operation.
                
            :param save: flag indicating whether to save after each move
                operation, ``True`` by default.
        """
        
        # Move all children to the node's parent.
        for child in node.children.all():
            child.move(node.parent, position, save)
    
    
    def prepare_delete_monarchy(self, node, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the :const:`DELETE_METHOD_MONARCHY` semantics. Descendant nodes,
            if present, will be moved; in this case the optional `position` can
            be a ``callable`` which is invoked prior to each move operation (see
            :meth:`move` for details).
            
            By default, after each move operation, sub-tree nodes which were
            moved will be saved through a call to :meth:`Model.save` unless
            `save` is ``False``.
            
            This method delegates move operations to :meth:`move`.
            
            :param node: the :class:`CTENode` to prepare for deletion.
            
            :param position: optionally, a ``callable`` to invoke prior to each
                move operation.
                
            :param save: flag indicating whether to save after each move
                operation, ``True`` by default.
        """
        
        # We are going to iterate all children, even though the first child is
        # treated in a special way, because the query iterator may be custom, so
        # we will avoid using slicing children[0] and children[1:].
        first = None
        for child in node.children.all():
            if first is None:
                first = child
                first.move(node.parent, position, save)
            else:
                child.move(first, position, save)
                
        
    def move(self, node, destination, position = None, save = False):
        """ Moves the given :class:`CTENode` `node` and places it as a child
            node of the `destination` :class:`CTENode` (or makes it a root node
            if `destination` is ``None``).
            
            Optionally, `position` can be a ``callable`` which is invoked prior
            to placement of the `node` with the `node` and the `destination`
            node as the sole two arguments; this can be useful in implementing
            specific sibling ordering semantics.
            
            Optionally, if `save` is ``True``, after the move operation
            completes (after the :attr:`CTENode.parent` foreign key is updated
            and the `position` callable is called if present), a call to
            :meth:`Model.save` is made.
        """
        
        # Allow custom positioning semantics to specify the position before
        # setting the parent.
        if not position is None:
            position(node, destination)
        
        node.parent = destination
          
        if save:
            node.save()
            
    
class CTENode(Model):
    """ Abstract :class:`Model` which implements a node in a CTE tree. This
        model features a mandatory foreign key to the parent node (hence to
        ``self``), which, when ``None``, indicates a root node. Multiple nodes
        with a ``None`` parent results in a forest, which can be constrained
        either with custom SQL constraints or through application logic.
        
        It is necessary for any custom :class:`Manager` of this model to inherit
        from :class:`CTENodeManager`, as all functionality of the CTE tree is
        implemented in the manager.
        
        It is possible to manipulate individual nodes when not loaded through
        the custom manager, or when freshly created either through the
        :meth:`create` method or through the constructor, however, any operation
        which requires tree information (the :attr:`depth`, :attr:`path`,
        and :attr:`ordering` virtual fields) will not work, and any attempt to
        invoke such methods will result in an :class:`ImproperlyConfigured`
        exception being raised.
        
        Many runtime properties of nodes are specified through a set of
        parameters which are stored as attributes of the node class, and begin
        with ``_cte_node_``. Before any of these parameters are used, the
        manager will attempt to load and verify them, raising an
        :class:`ImproperlyConfigured` exception if any errors are encountered.
        All parameters have default values.
        
        All :class:`QuerySet` objects involving CTE nodes use the
        :meth:`QuerySet.extra` semantics in order to specify additional
        ``SELECT``, ``WHERE``, and ``ORDER_BY`` SQL semantics, therefore, they
        cannot be combined through the ``OR`` operator (the ``|`` operator).
        
        The following parameters can optionally be specified at the class level:
         
        * _cte_node_traversal:
        
            A string from one of :const:`TREE_TRAVERSAL_METHODS`, which
            specifies the default tree traversal order. If this parameters is
            ``None`` or :const:`TREE_TRAVERSAL_NONE`, then
            :const:`DEFAULT_TREE_TRAVERSAL` method is used (which is ``dfs``
            for depth-first).
            
        * _cte_node_order_by:
        
            A list of strings or tuples specifying the ordering of siblings
            during tree traversal (in the breadth-first method, siblings are
            ordered depending on their parent and not the entire set of nodes at
            the given depth of the tree).
            
            The entries in this list can be any of the model fields, much like
            the entries in the :attr:`ordering` of the model's :class:`Meta`
            class or the arguments of the :meth:`order_by` method of
            :class:`QuerySet`.
            
            These entries may also contain the virtual field :attr:`depth`,
            which cannot be used by the normal :class:`QuerySet` because Django
            cannot recognize such virtual fields.
            
            In case of multiple entries, they must all be of the same database
            type. For VARCHAR fields, their values will be cast to TEXT, unless
            otherwise specified. It is possible to specify the database type
            into which the ordering field values are cast by providing tuples of
            the form ``(fieldname, dbtype)`` in the ordering sequence.
            
            Specifying cast types is necessary when combining different data
            types in the ordering sequence, such as an int and a float (casting
            the int into a float is probably the desired outcome in this
            situation). In the worst case, TEXT can be specified for all casts.
            
        * _cte_node_delete_method:
        
            A string specifying the desired default deletion semantics, which
            may be one of :const:`DELETE_METHODS`. If this parameter is missing
            or ``None`` or :const:`DELETE_METHOD_NONE`, then the default
            deletion semantics :const:`DEFAULT_DELETE_METHOD` will be used
            (which is :const:`DELETE_METHOD_PHARAOH` or ``pharaoh`` for the
            Pharaoh deletion semantics).
            
        * _cte_node_parent:
        
            A string referencing the name of the :class:`ForeignKey` field which
            implements the parent relationship, typically called ``parent`` and
            automatically inherited from this class.
            
            If this parameter is missing, and no field with the name ``parent``
            can be found, then the first :class:`ForeignKey` which relates to
            this model will be used as the parent relationship field.
            
        * _cte_node_children:
        
            A string referencing the `related_name` attribute of the
            :class:`ForeignKey` field which implements the parent relationship,
            typically called ``parent`` (specified in
            :const:`DEFAULT_CHILDREN_NAME`) and automatically
            inherited from this class.
            
        * _cte_node_table:
        
            The name of the temporary table to use with the ``WITH`` CTE SQL
            statement when compiling queries involving nodes. By default this is
            :const:`DEFAULT_TABLE_NAME` (which is ``cte``).
            
        * _cte_node_primary_key_type:
        
            A string representing the database type of the primary key, if the
            primary key is a non-standard type, and must be cast in order to be
            used in the :attr:`path` or :attr:`ordering` virtual fields
            (similarly to the :attr:`_cte_node_order_by` parameter above).
            
            A ``VARCHAR`` primary key will be automatically cast to ``TEXT``,
            unless explicitly specified otherwise through this parameter. 

            
        * _cte_node_path, _cte_node_depth, _cte_node_ordering:
        
            Strings specifying the attribute names of the virtual fields
            containing the path, depth, and ordering prefix of each node, by
            default, respectively, :const:`VIRTUAL_FIELD_PATH` (which is
            ``path``), :const:`VIRTUAL_FIELD_DEPTH` (which is ``depth``), and
            :const:`VIRTUAL_FIELD_ORDERING` (which is ``ordering``).
    """
    
    # This ForeignKey is mandatory, however, its name can be different, as long
    # as it's specified through _cte_node_parent.
    parent = ForeignKey('self', null = True, blank = True,
        related_name = 'children')
    
    # This custom Manager is mandatory.
    objects = CTENodeManager()
    
    
    def root(self):
        """ Returns the CTENode which is the root of the tree in which this
            node participates.
        """
        return self.__class__.objects.root(self)
    
    def siblings(self):
        """ Returns a :class:`QuerySet` of all siblings of this node.
        
            :returns: A :class:`QuerySet` of all siblings of this node.
        """
        return self.__class__.objects.siblings(self)
    
    def ancestors(self):
        """ Returns a :class:`QuerySet` of all ancestors of this node.
        
            :returns: A :class:`QuerySet` of all ancestors of this node.
        """
        return self.__class__.objects.ancestors(self)
    
    def descendants(self):
        """ Returns a :class:`QuerySet` of all descendants of this node.
            
            :returns: A :class:`QuerySet` of all descendants of this node.
        """
        return self.__class__.objects.descendants(self)
    
    
    def is_parent_of(self, subject):
        """ Returns ``True`` if this node is the parent of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`parent`
            field, and so does not perform any query.
            
            :param subject: the :class:`CTENode` for which to determine whether
                its parent is this node.
                
            :returns: ``True`` if this node is the parent of `subject`,
                ``False`` otherwise.
        """
        
        return self.__class__.objects.is_parent_of(self, subject)
    
    
    def is_child_of(self, subject):
        """ Returns ``True`` if this node is a child of the given `subject`
            node, ``False`` otherwise. This method used the :attr:`parent`
            field, and so does not perform any query.
            
            :param subject: the :class:`CTENode` for which to determine whether
                one of its children is this node.
                
            :returns: ``True`` if this node is a child of `subject`, ``False``
                otherwise.
        """
        
        return self.__class__.objects.is_child_of(self, subject)
    

    def is_sibling_of(self, subject):
        """ Returns ``True`` if this node is a sibling of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`parent`
            field, and so does not perform any query.
            
            :param subject: the :class:`CTENode` for which to determine whether
                one of its siblings is this node.
                
            :returns: ``True`` if this node is a sibling of `subject`, ``False``
                otherwise.
        """
        
        return self.__class__.objects.is_sibling_of(self, subject)
    
    
    def is_ancestor_of(self, subject):
        """ Returns ``True`` if the node is an ancestor of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`path` virtual
            field, and so does not perform any query.
            
            :param subject: the :class:`CTENode` for which to determine whether
                one of its ancestors is this node.
                
            :returns: ``True`` if this node is an ancestor of `subject`,
                ``False`` otherwise.
        """
        
        return self.__class__.objects.is_ancestor_of(self, subject)
    
    
    def is_descendant_of(self, subject):
        """ Returns ``True`` if the node is a descendant of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`path` virtual
            field, and so does not perform any query.
            
            :param subject: the :class:`CTENode` for which to determine whether
                one of its descendants is this node.
                
            :returns: ``True`` if this node is a descendant of `subject`,
                ``False`` otherwise.
        """
        
        return self.__class__.objects.is_descendant_of(self, subject)
    
    
    def is_leaf(self):
        """ Returns ``True`` if this node is a leaf (has no children), ``False``
            otherwise.
                
            :return: ``True`` if this node is a leaf, ``False`` otherwise.
        """
        
        return self.__class__.objects.is_leaf(self)
    
    
    def move(self, destination = None, position = None, save = False):
        """ Moves this node and places it as a child node of the `destination`
            :class:`CTENode` (or makes it a root node if `destination` is
            ``None``).
            
            Optionally, `position` can be a ``callable`` which is invoked prior
            to placement of the node with this node and the destination node as
            the sole two arguments; this can be useful in implementing specific
            sibling ordering semantics.
            
            Optionally, if `save` is ``True``, after the move operation
            completes (after the :attr:`parent` foreign key is updated and the
            `position` callable is called if present), a call to
            :meth:`Model.save` is made.
        """
        
        return self.__class__.objects.move(self, destination, position, save)
    
    
    def delete(self, method = None, position = None, save = True):
        
        self.__class__.objects.prepare_delete(self, method = method,
            position = position, save = save)
        
        return super(CTENode, self).delete()
                
        
    class Meta:
        
        abstract = True
        
        # Prevent cycles in order to maintain tree / forest property.
        unique_together = [('id', 'parent'), ]
        
        