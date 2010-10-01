#
# Copyright (c) 2006-2010, Prometheus Research, LLC
# Authors: Clark C. Evans <cce@clarkevans.com>,
#          Kirill Simonov <xi@resolvent.net>
#


"""
:mod:`htsql.tr.assemble`
========================

This module implements the assembling process.
"""


from ..util import maybe, listof
from ..adapter import Adapter, adapts
from .error import AssembleError
from .code import (Expression, Code, Space, ScalarSpace, ProductSpace,
                   FilteredSpace, OrderedSpace, MaskedSpace,
                   Unit, ScalarUnit, ColumnUnit, AggregateUnit, CorrelatedUnit,
                   QueryExpression, SegmentExpression,
                   BatchExpression, ScalarBatchExpression,
                   AggregateBatchExpression)
from .term import (RoutingTerm, ScalarTerm, TableTerm, FilterTerm, JoinTerm,
                   CorrelationTerm, ProjectionTerm, OrderTerm, WrapperTerm,
                   SegmentTerm, QueryTerm, Tie, ParallelTie, SeriesTie)


class AssemblingState(object):
    """
    Encapsulates the state of the assembling process.

    State attributes:

    `scalar` (:class:`htsql.tr.code.ScalarSpace`)
        The scalar space.

    `baseline` (:class:`htsql.tr.code.Space`)
        When assembling a new term, indicates the leftmost axis that must
        exported by the term.  Note that the baseline space is always
        inflated.

    `mask` (:class:`htsql.tr.code.Space`)
        When assembling a new term, indicates that the term is going to be
        attached to a term that represents the `mask` space.
    """

    def __init__(self):
        # The next term tag to be produced by `tag`.
        self.next_tag = 1
        # The scalar space.
        self.scalar = None
        # The stack of previous baseline spaces.
        self.baseline_stack = []
        # The current baseline space.
        self.baseline = None
        # The stack of previous mask spaces.
        self.mask_stack = []
        # The current mask space.
        self.mask = None

    def tag(self):
        """
        Generates and returns a new unique term tag.
        """
        tag = self.next_tag
        self.next_tag += 1
        return tag

    def set_scalar(self, space):
        """
        Initializes the scalar, baseline and mask spaces.

        This function must be called before state attributes `scalar`,
        `baseline` and `mask` could be used.

        `space` (:class:`htsql.tr.code.ScalarSpace`)
            A scalar space.
        """
        assert isinstance(space, ScalarSpace)
        # Check that the state spaces are not yet initialized.
        assert self.scalar is None
        assert self.baseline is None
        assert self.mask is None
        self.scalar = space
        self.baseline = space
        self.mask = space

    def unset_scalar(self):
        """
        Clears the state spaces.
        """
        # Check that the state spaces are initialized and the space stacks
        # are exhausted.
        assert self.scalar is not None
        assert not self.baseline_stack
        assert self.baseline is self.scalar
        assert not self.mask_stack
        assert self.mask is self.scalar
        self.scalar = None
        self.baseline = None
        self.mask = None

    def push_baseline(self, baseline):
        """
        Sets a new baseline space.

        This function masks the current baseline space.  To restore
        the previous baseline space, use :meth:`pop_baseline`.

        `baseline` (:class:`htsql.tr.code.Space`)
            The new baseline space.  Note that the baseline space
            must be inflated.
        """
        assert isinstance(baseline, Space) and baseline.is_inflated
        self.baseline_stack.append(self.baseline)
        self.baseline = baseline

    def pop_baseline(self):
        """
        Restores the previous baseline space.
        """
        self.baseline = self.baseline_stack.pop()

    def push_mask(self, mask):
        """
        Sets a new mask space.

        This function hides the current mask space.  To restore the
        previous mask space, use :meth:`pop_mask`.

        `mask` (:class:`htsql.tr.code.Space`)
            The new mask space.
        """
        assert isinstance(mask, Space)
        self.mask_stack.append(self.mask)
        self.mask = mask

    def pop_mask(self):
        """
        Restores the previous mask space.
        """
        self.mask = self.mask_stack.pop()

    def assemble(self, expression, baseline=None, mask=None):
        """
        Assembles a new term node for the given expression.

        `expression` (:class:`htsql.tr.code.Expression`)
            An expression node.

        `baseline` (:class:`htsql.tr.code.Space` or ``None``)
            The baseline space.  Specifies an axis space that the assembled
            term must export.  If not set, the current baseline space of
            the state is used.

            When `expression` is a space, the generated term must
            export the space itself as well as all inflated prefixes
            up to the `baseline` space.  It may (but it is not required)
            export other axes as well.

        `mask` (:class:`htsql.tr.code.Space` or ``None``)
            The mask space.  Specifies the mask space against which
            a new term is assembled.  When not set, the current mask space
            of the state is used.

            A mask indicates that the new term is going to be attached
            to a term that represent the mask space.  Therefore the
            assembler could ignore any non-axis operations that are
            already enforced by the mask space.
        """
        # FIXME: potentially, we could implement a cache of `expression`
        # -> `term` to avoid generating the same term node more than once.
        # There are several complications though.  First, the term depends
        # not only on the expression, but also on the current baseline
        # and mask spaces.  Second, each assembled term must have a unique
        # tag, therefore we'd have to replace the tags and route tables
        # of the cached term node.
        return assemble(expression, self, baseline=baseline, mask=mask)

    def inject(self, term, expressions):
        """
        Augments a term to make it capable of producing the given expressions.

        This method takes a term node and a list of expressions.  It returns
        a term that could produce the same expressions as the given term, and,
        in addition, all the given expressions.

        Note that, technically, a term only exports unit expressions;
        we claim that a term could export an expression if it exports
        all the units of the expression.

        `term` (:class:`htsql.tr.term.RoutingTerm`)
            A term node.

        `expression` (a list of :class:`htsql.tr.code.Expression`)
            A list of expressions to inject into the given term.
        """
        assert isinstance(term, RoutingTerm)
        assert isinstance(expressions, listof(Expression))
        # Screen out expressions that the term could already export.
        # This filter only works with spaces and non-column units,
        # therefore the filtered list could still contain some
        # exportable expressions.
        expressions = [expression for expression in expressions
                                  if expression not in term.routes]
        # No expressions to inject, return the term unmodified.
        if not expressions:
            return term
        # At this moment, we could just apply the `Inject` adapter
        # sequentially to each of the expressions.  However, in some
        # cases, the assembler is able to generate a more optimal
        # term tree when it processes all units sharing the same
        # form simultaneously.  To handle this case, we collect
        # all expressions into an auxiliary expression node
        # `BatchExpression`.  When injected, the group expression
        # applies the multi-unit optimizations.
        if len(expressions) == 1:
            expression = expressions[0]
        else:
            expression = BatchExpression(expressions, term.binding)
        # Realize and apply the `Inject` adapter.
        inject = Inject(expression, term, self)
        return inject()


class Assemble(Adapter):
    """
    Translates an expression node to a term node.

    This is an interface adapter; see subclasses for implementations.

    The :class:`Assemble` adapter is implemented for two classes
    of expressions:

    - top-level expressions such as the whole query and the query segment,
      for which it builds respective top-level term nodes;

    - spaces, for which the adapter builds a corresponding relational
      algebraic expression.

    After a term is built, it is typically augmented using the
    :class:`Inject` adapter to have it export any exprected units.

    The :class:`Assemble` adapter has the following signature::

        Assemble: (Expression, AssemblingState) -> Term

    The adapter is polymorphic on the `Expression` argument.

    `expression` (:class:`htsql.tr.code.Expression`)
        An expression node.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.
    """

    adapts(Expression)

    def __init__(self, expression, state):
        assert isinstance(expression, Expression)
        assert isinstance(state, AssemblingState)
        self.expression = expression
        self.state = state

    def __call__(self):
        # This should never be reachable; if we are here, it indicates
        # either a bug or an incomplete implementation.  Since normally it
        # cannot be triggered by a user, we don't bother with generating
        # a user-level HTSQL exception.
        raise NotImplementedError("the assemble adapter is not implemented"
                                  " for a %r node" % self.expression)


class Inject(Adapter):
    """
    Augments a term to make it capable of producing the given expression.

    This is an interface adapter; see subclasses for implementations.

    This adapter takes a term node and an expression (usually, a unit)
    and returns a new term (an augmentation of the given term) that is
    able to produce the given expression.

    The :class:`Inject` adapter has the following signature::

        Inject: (Expression, Term, AssemblingState) -> Term

    The adapter is polymorphic on the `Expression` argument.

    `expression` (:class:`htsql.tr.code.Expression`)
        An expression node to inject.

    `term` (:class:`htsql.tr.term.RoutingTerm`)
        A term node to inject into.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.
    """

    adapts(Expression)

    def __init__(self, expression, term, state):
        assert isinstance(expression, Expression)
        assert isinstance(term, RoutingTerm)
        assert isinstance(state, AssemblingState)
        self.expression = expression
        self.term = term
        self.state = state

    def __call__(self):
        # Same as with `Assemble`, unless it's a bug or an incomplete
        # implementation, it should never be reachable.
        raise NotImplementedError("the inject adapter is not implemented"
                                  " for a %r node" % self.expression)

    # Utility functions used by implementations.

    def assemble_shoot(self, space, trunk_term, codes=None):
        """
        Assembles a term corresponding to the given space.

        The assembled term is called *a shoot term* (relatively to
        the given *trunk term*).

        `space` (:class:`htsql.tr.code.Space`)
            A space node, for which the we assemble a term.

        `trunk_term` (:class:`htsql.tr.term.RoutingTerm`)
           Expresses a promise that the assembled term will be
           (eventually) joined to `trunk_term` (see :meth:`join_terms`).

        `codes` (a list of :class:`htsql.tr.code.Expression` or ``None``)
           If provided, a list of expressions to be injected
           into the assembled term.
        """

        # Sanity check on the arguments.
        assert isinstance(space, Space)
        assert isinstance(trunk_term, RoutingTerm)
        assert isinstance(codes, maybe(listof(Expression)))

        # Determine the longest prefix of the space that either
        # contains no non-axis operations or has all its non-axis
        # operations enforced by the trunk space.  This prefix will
        # be used as the baseline of the assembled term (that is,
        # we ask the assembler not to generate any axes under
        # the baseline).

        # Start with removing any filters enforced by the trunk space.
        baseline = space.prune(trunk_term.space)
        # Now find the longest prefix that does not contain any
        # non-axis operations.
        while not baseline.is_inflated:
            baseline = baseline.base
        # Handle the case when the given space is not spanned by the
        # trunk space -- it happens when we construct a plural term
        # for an aggregate unit.  In this case, before joining it
        # to the trunk term, the shoot term will be projected to some
        # singular prefix of the given space.  To enable such projection,
        # at least the base of the shoot baseline must be spanned by
        # the trunk space (then, we can project on the columns of
        # a foreign key that attaches the baseline to its base).
        if not trunk_term.space.spans(baseline):
            while not trunk_term.space.spans(baseline.base):
                baseline = baseline.base

        # Assemble the term, use the found baseline and the trunk space
        # as the mask.
        term = self.state.assemble(space,
                                   baseline=baseline,
                                   mask=trunk_term.space)

        # If provided, inject the given expressions.
        if codes is not None:
            term = self.state.inject(term, codes)

        # SQL syntax does not permit us evaluating scalar or aggregate
        # expressions in terminal terms.  So when generating terms for
        # scalar or aggregate units, we need to cover terminal terms
        # with a no-op wrapper.  It may generate an unnecessary
        # wrapper if the term is used for other purposes, but we rely
        # on the outliner to flatten any unused wrappers.
        if term.is_nullary:
            term = WrapperTerm(self.state.tag(), term,
                               term.space, term.routes.copy())

        # Return the assembled shoot term.
        return term

    def tie_terms(self, trunk_term, shoot_term):
        """
        Returns ties to attach the shoot term to the trunk term.

        `trunk_term` (:class:`htsql.tr.term.RoutingTerm`)
            The left (trunk) operand of the join.

        `shoot_term` (:class:`htsql.tr.term.RoutingTerm`)
            The right (shoot) operand of the join.

        Note that the trunk term may not export all the units necessary
        to generate tie conditions.  Apply :meth:`inject_ties` on the trunk
        before using the ties to join the trunk and the shoot.
        """
        # Sanity check on the arguments.
        assert isinstance(trunk_term, RoutingTerm)
        assert isinstance(shoot_term, RoutingTerm)
        # Verify that it is possible to join the terms without
        # changing the cardinality of the trunk.
        assert (shoot_term.baseline.is_scalar or
                trunk_term.space.spans(shoot_term.baseline.base))

        # There are two ways the ties are generated:
        #
        # - when the shoot baseline is an axis of the trunk space,
        #   in this case we join the terms using parallel ties on
        #   the common axes;
        # - otherwise, join the terms using a series tie between
        #   the shoot baseline and its base.

        # Ties to attach the shoot to the trunk.
        ties = []
        # Check if the shoot baseline is an axis of the trunk space.
        if trunk_term.backbone.concludes(shoot_term.baseline):
            # In this case, we join the terms by all axes of the trunk
            # space that are exported by the shoot term.
            # Find the first inflated axis of the trunk exported
            # by the shoot.
            axis = trunk_term.backbone
            while axis not in shoot_term.routes:
                axis = axis.base
            # Now the axes between `axis` and `baseline` are common axes
            # of the trunk space and the shoot term.  For each of them,
            # generate a parallel tie.  Note that we do not verify
            # (and, in general, it is not required) that these axes
            # are exported by the trunk term.  Apply `inject_ties()` on
            # the trunk term before using the ties to join the terms.
            while axis != shoot_term.baseline.base:
                assert axis in shoot_term.routes
                # Skip non-expanding axes (but always include the baseline).
                if axis.is_expanding or axis == shoot_term.baseline:
                    tie = ParallelTie(axis)
                    ties.append(tie)
                axis = axis.base
            # We prefer (for no particular reason) the ties to go
            # from inner to outer axes.
            ties.reverse()
        else:
            # When the shoot does not touch the trunk space, we attach it
            # using a series tie between the shoot baseline and its base.
            # Note that we do not verify (and it is not required) that
            # the trunk term export the base space.  Apply `inject_ties()`
            # on the trunk term to inject any necessary spaces before
            # joining the terms using the ties.
            tie = SeriesTie(shoot_term.baseline)
            ties.append(tie)

        # Return the generated ties.
        return ties

    def inject_ties(self, term, ties):
        """
        Augments the term to ensure it can export all units required
        to generate tie conditions.

        `term` (:class:`htsql.tr.term.RoutingTerm`)
            The term to update.

            It is assumed that `term` was the argument `trunk_term` of
            :meth:`tie_terms` when the ties were generated.

        `ties` (a list of :class:`htsql.tr.term.Tie`)
            The ties to inject.

            It is assumed the ties were generated by :meth:`tie_terms`.
        """
        # Sanity check on the arguments.
        assert isinstance(term, RoutingTerm)
        assert isinstance(ties, listof(Tie))

        # Accumulate the axes we need to inject.
        axes = []
        # Iterate over the ties.
        for tie in ties:
            # For a parallel tie, we inject the tie space.
            if tie.is_parallel:
                axes.append(tie.space)
            # For a series tie, we inject the base of the tie space
            # (the tie space itself goes to the shoot term).
            if tie.is_series:
                if tie.is_backward:
                    # Not really reachable since we never generate backward
                    # ties in `tie_terms()`.  It is here for completeness.
                    axes.append(tie.space)
                else:
                    axes.append(tie.space.base)

        # Inject the required spaces and return the updated term.
        return self.state.inject(term, axes)

    def join_terms(self, trunk_term, shoot_term, extra_routes):
        """
        Attaches a shoot term to a trunk term.

        The produced join term uses the space and the routing
        table of the trunk term, but also includes the given
        extra routes.

        `trunk_term` (:class:`htsql.tr.term.RoutingTerm`)
            The left (trunk) operand of the join.

        `shoot_term` (:class:`htsql.tr.term.RoutingTerm`)
            The right (shoot) operand of the term.

            The shoot term must be singular relatively to the trunk term.

        `extra_routes` (a mapping from a unit/space to a term tag)
            Any extra routes provided by the join.
        """
        # Sanity check on the arguments.
        assert isinstance(trunk_term, RoutingTerm)
        assert isinstance(shoot_term, RoutingTerm)
        # FIXME: Unfortunately, we cannot properly verify that the trunk
        # space spans the shoot space since the term space is generated
        # incorrectly for projection terms.
        #assert trunk_term.space.dominates(shoot_term.space)
        assert isinstance(extra_routes, dict)

        # Ties to attach the terms.
        ties = self.tie_terms(trunk_term, shoot_term)
        # Make sure the trunk term could export tie conditions.
        trunk_term = self.inject_ties(trunk_term, ties)
        # Determine if we could use an inner join to attach the shoot
        # to the trunk.  We could do it if the inner join does not
        # decrease cardinality of the trunk.
        # FIXME: The condition that the shoot space dominates the
        # trunk space is sufficient, but not really necessary.
        # In general, we can use the inner join if the shoot space
        # dominates the prefix of the trunk space cut at the longest
        # common axis of trunk and the shoot spaces.
        is_inner = shoot_term.space.dominates(trunk_term.space)
        # Use the routing table of the trunk term, but also add
        # the given extra routes.
        routes = trunk_term.routes.copy()
        routes.update(extra_routes)
        # Generate and return a join term.
        return JoinTerm(self.state.tag(), trunk_term, shoot_term,
                        ties, is_inner, trunk_term.space, routes)


class AssembleQuery(Assemble):
    """
    Assembles a top-level query term.
    """

    adapts(QueryExpression)

    def __call__(self):
        # Assemble the segment term.
        segment = None
        if self.expression.segment is not None:
            segment = self.state.assemble(self.expression.segment)
        # Construct a query term.
        return QueryTerm(self.state.tag(), segment, self.expression)


class AssembleSegment(Assemble):
    """
    Assembles a segment term.
    """

    adapts(SegmentExpression)

    def __call__(self):
        # Initialize the all state spaces with a scalar space.
        self.state.set_scalar(self.expression.space.scalar)
        # Construct a term corresponding to the segment space.
        kid = self.state.assemble(self.expression.space)
        # Get the ordering of the segment space.
        order = self.expression.space.ordering()
        # List of expressions we need the term to export.
        codes = self.expression.elements + [code for code, direction in order]
        # Inject the expressions into the term.
        kid = self.state.inject(kid, codes)
        # The assembler does not guarantee that the produced term respects
        # the space ordering, so it is our responsitibity to wrap the term
        # with an order node.
        if order:
            kid = OrderTerm(self.state.tag(), kid, order, None, None,
                            kid.space, kid.routes.copy())
        # Shut down the state spaces.
        self.state.unset_scalar()
        # Construct a segment term.
        return SegmentTerm(self.state.tag(), kid, self.expression.elements,
                           kid.space, kid.routes.copy())


class AssembleSpace(Assemble):
    """
    Assemble a term corresponding to a space node.

    This is an abstract class; see subclasses for implementations.

    The general algorithm for assembling a term node for the given space
    looks as follows:

    - assemble a term for the base space;
    - inject any necessary expressions;
    - build a new term node that represents the space operation.

    When assembling terms, the following optimizations are applied:

    Removing unnecessary non-axis operations.  The current `mask` space
    expresses a promise that the generated term will be attached to
    a term representing the mask space.  Therefore the assembler
    could skip any non-axis filters that are already enforced by
    the mask space.

    Removing unnecessary axis operations.  The current `baseline` space
    denotes the leftmost axis that the term should be able to export.
    The assembler may (but does not have to) omit any axes nested under
    the `baseline` axis.

    Because of these optimizations, the shape and cardinality of the
    term rows may differ from that of the space.  Additionally, the
    term is not required to respect the ordering of its space.

    Constructor arguments:

    `space` (:class:`htsql.tr.code.Space`)
        A space node.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.

    Other attributes:

    `backbone` (:class:`htsql.tr.code.Space`)
        The inflation of the given space.

    `baseline` (:class:`htsql.tr.code.Space`)
        An alias to `state.baseline`.

    `mask` (:class:`htsql.tr.code.Space`)
        An alias to `state.mask`.
    """

    adapts(Space)

    def __init__(self, space, state):
        assert isinstance(space, Space)
        # The inflation of the space.
        backbone = space.inflate()
        # Check that the baseline space is an axis of the given space.
        assert backbone.concludes(state.baseline)
        super(AssembleSpace, self).__init__(space, state)
        self.space = space
        self.state = state
        self.backbone = backbone
        # Extract commonly used state properties.
        self.baseline = state.baseline
        self.mask = state.mask


class InjectSpace(Inject):
    """
    Augments the term to make it produce the given space.

    `space` (:class:`htsql.tr.code.Space`)
        A space node to inject.

    `term` (:class:`htsql.tr.term.RoutingTerm`)
        A term node to inject into.

        The term space must span the given space.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.
    """

    adapts(Space)

    def __init__(self, space, term, state):
        assert isinstance(space, Space)
        # It is a bug if we get the `space` plural for the `term` here.
        # It is a responsibility of `InjectUnit` to guard against unexpected
        # plural expressions and to issue an appropriate HTSQL error.
        assert term.space.spans(space)
        super(InjectSpace, self).__init__(space, term, state)
        self.space = space
        self.term = term
        self.state = state

    def __call__(self):
        # Note that this function works for all space classes universally.
        # We start with checking for and handling several special cases;
        # if none of them apply, we grow a shoot term for the given space
        # and attach it to the main term.

        # Check if the space is already exported.
        if self.space in self.term.routes:
            return self.term

        # Remove any non-axis filters that are enforced by the term space.
        unmasked_space = self.space.prune(self.term.space)

        # When converged with the term space, `space` and `unmasked_space`
        # contains the same set of rows, therefore in the context of the
        # given term, they could be used interchangeably.
        # In particular, if `unmasked_space` is already exported, we could
        # use the same route for `space`.
        if unmasked_space in self.term.routes:
            routes = self.term.routes.copy()
            routes[self.space] = routes[unmasked_space]
            return self.term.clone(routes=routes)

        # A special case when the given space is an axis prefix of the term
        # space.  The fact that the space is not exported by the term means
        # that the term tree is optimized by cutting all axes below some
        # baseline.  Now we need to grow these axes back.
        if self.term.backbone.concludes(unmasked_space):
            # Here we assemble a table term corresponding to the space and
            # attach it to the axis directly above it using a backward
            # series tie.

            # Find the axis directly above the space.  Note that here
            # `unmasked_space` is the inflation of the given space.
            next_axis = self.term.baseline
            while next_axis.base != unmasked_space:
                next_axis = next_axis.base

            # It is possible that `next_axis` is also not exported by
            # the term (specifically, when `next_axis` is below the term
            # baseline).  So we call `inject()` with `next_axis`, which
            # should match the same special case and recursively add
            # `next_axis` to the routing table.  Bugs in the assembler
            # and in the compare-by-value code often cause an infinite
            # loop or recursion here!
            lkid = self.state.inject(self.term, [next_axis])
            # Injecting an axis prefix should never add any axes below
            # (but will add all the axis prefixes above).
            assert unmasked_space not in lkid.routes

            # Assemble a term corresponding to the axis itself.
            rkid = self.state.assemble(unmasked_space,
                                       baseline=unmasked_space,
                                       mask=self.state.scalar)
            # We expect to get a table or a scalar term here.
            assert rkid.is_nullary

            # Join the terms using a backward series tie.
            # FIXME: technically, nothing prevents us from joining `rkid`
            # to `lkid` using a forward series tie -- and then we could
            # remove support for backward ties since this is the only
            # place where they are used.  Currently, however, it is
            # easier for the outliner to flatten the left child of a join
            # term, so we put the more complex term to the left position.
            tie = SeriesTie(next_axis, is_backward=True)
            # Since we are expanding the term baseline, the join is always
            # inner.
            is_inner = True
            # Re-use the old routing table, but add the new axis.
            routes = lkid.routes.copy()
            routes[unmasked_space] = rkid[unmasked_space]
            routes[self.space] = rkid[unmasked_space]
            # Assemble and return a join term.
            return JoinTerm(self.state.tag(), lkid, rkid, [tie], is_inner,
                            lkid.space, routes)

        # None of the special cases apply, so we use a general method:
        # - grow a shoot term for the given space;
        # - attach the shoot to the main term.

        # Assemble a shoot term for the space.
        space_term = self.assemble_shoot(self.space, self.term)
        # The routes to add.
        extra_routes = {}
        extra_routes[self.space] = space_term.routes[self.space]
        extra_routes[unmasked_space] = space_term.routes[self.space]
        # Join the shoot to the main term.
        return self.join_terms(self.term, space_term, extra_routes)


class AssembleScalar(AssembleSpace):
    """
    Assembles a term corresponding to a scalar space.
    """

    adapts(ScalarSpace)

    def __call__(self):
        # Generate a `ScalarTerm` instance.
        tag = self.state.tag()
        routes = { self.space: tag }
        return ScalarTerm(tag, self.space, routes)


class AssembleProduct(AssembleSpace):
    """
    Assembles a term corresponding to a (cross or join) product space.
    """

    adapts(ProductSpace)

    def __call__(self):
        # We start with identifying and handling special cases, where
        # we able to generate a more optimal, less compex term tree than
        # in the regular case.  If none of the special cases are applicable,
        # we use the generic algorithm.

        # The first special case: the given space is the leftmost axis
        # we must export.  Since `baseline` is always an inflated space,
        # we need to compare it with the inflation of the given space
        # rather than with the space itself.
        if self.backbone == self.baseline:
            # Generate a table term that exports rows from the prominent
            # table.
            tag = self.state.tag()
            # The routing table must always include the term space, and also,
            # for any space it includes, the inflation of the space.
            # In this case, `self.space` is the term space, `self.backbone`
            # is its inflation.
            routes = { self.space: tag, self.backbone: tag }
            return TableTerm(tag, self.space, routes)

        # Term corresponding to the space base.
        term = self.state.assemble(self.space.base)

        # The second special case, when the term of the base could also
        # serve as a term for the space itself.  It is possible if the
        # following two conditions are met:
        # - the term exports the inflation of the given space (`backbone`),
        # - the given space conforms (has the same cardinality as) its base.
        # This case usually corresponds to an HTSQL expression of the form:
        #   (A?f(B)).B,
        # where `B` is a singular, non-nullable link from `A` and `f(B)` is
        # an expression on `B`.
        if self.backbone in term.routes and self.space.conforms(term.space):
            # We need to add the given space to the routing table and
            # replace the term space.
            routes = term.routes.copy()
            routes[self.space] = routes[self.backbone]
            return term.clone(space=self.space, routes=routes)

        # Now the general case.  We take two terms:
        # - the term assembled for the space base
        # - and a table term corresponding to the prominent table,
        # and join them using the tie between the space and its base.

        # This is the term for the space base, we already generated it.
        lkid = term
        # This is a table term corresponding to the prominent table of
        # the space.  Instead of generating it directly, we call `assemble`
        # on the same space, but with a different baseline, so that it
        # will hit the first special case and produce a table term.
        rkid = self.state.assemble(self.space, baseline=self.backbone)
        # The tie attaching the space to its base.
        tie = SeriesTie(self.backbone)
        is_inner = True
        # We use the routing table of the base term with extra routes
        # corresponding to the given space and its inflation which we
        # export from the table term.
        routes = lkid.routes.copy()
        routes[self.space] = rkid.routes[self.space]
        routes[self.backbone] = rkid.routes[self.backbone]
        # Generate a join term node.
        return JoinTerm(self.state.tag(), lkid, rkid, [tie], is_inner,
                        self.space, routes)


class AssembleFiltered(AssembleSpace):
    """
    Assembles a term corresponding to a filtered space.
    """

    adapts(FilteredSpace)

    def __call__(self):
        # To construct a term for a filtered space, we start with
        # a term for its base, ensure that it could generate the given
        # predicate expression and finally wrap it with a filter term
        # node.

        # The term corresponding to the space base.
        term = self.state.assemble(self.space.base)

        # Handle the special case when the filter is already enforced
        # by the mask.  There is no method to directly verify it, so
        # we prune the masked operations from the space itself and
        # its base.  When the filter belongs to the mask, the resulting
        # spaces will be equal.
        if self.space.prune(self.mask) == self.space.base.prune(self.mask):
            # We do not need to apply the filter since it is already
            # enforced by the mask.  We still need to add the space
            # to the routing table.
            routes = term.routes.copy()
            # The space itself and its base share the same inflated space
            # (`backbone`), therefore the backbone must be in the routing
            # table.
            routes[self.space] = routes[self.backbone]
            return term.clone(space=self.space, routes=routes)

        # Now wrap the base term with a filter term node.
        # Make sure the base term is able to produce the filter expression.
        kid = self.state.inject(term, [self.space.filter])
        # Inherit the routing table from the base term, add the given
        # space to the routing table.
        routes = kid.routes.copy()
        routes[self.space] = routes[self.backbone]
        # Generate a filter term node.
        return FilterTerm(self.state.tag(), kid, self.space.filter,
                          self.space, routes)


class AssembleOrdered(AssembleSpace):
    """
    Assembles a term corresponding to an ordered space.
    """

    adapts(OrderedSpace)

    def __call__(self):
        # An ordered space has two functions:
        # - adding explicit row ordering;
        # - extracting a slice from the row set.
        # Note the first function could be ignored since the assembled terms
        # are not required to respect the ordering of the underlying space.

        # There are two cases when we could reuse the base term without
        # wrapping it with an order term node:
        # - when the order space does not apply limit/offset to its base;
        # - when the order space is already enforced by the mask.
        if (self.space.is_expanding or
            self.space.prune(self.mask) == self.space.base.prune(self.mask)):
            # Generate a term for the space base.
            term = self.state.assemble(self.space.base)
            # Update its routing table to include the given space and
            # return the node.
            routes = term.routes.copy()
            routes[self.space] = routes[self.backbone]
            return term.clone(space=self.space, routes=routes)

        # Applying limit/offset requires special care.  Since slicing
        # relies on precise row numbering, the base term must produce
        # exactly the rows of the base.  Therefore we cannot apply any
        # optimizations as they change cardinality of the term.
        # Here we reset the current baseline and mask spaces to the
        # scalar space, which effectively disables any optimizations.
        kid = self.state.assemble(self.space.base,
                                  baseline=self.state.scalar,
                                  mask=self.state.scalar)
        # Extract the space ordering and make sure the base term is able
        # to produce the order expressions.
        order = self.space.ordering()
        codes = [code for code, direction in order]
        kid = self.state.inject(kid, codes)
        # Add the given space to the routing table.
        routes = kid.routes.copy()
        routes[self.space] = routes[self.backbone]
        # Generate an order term.
        return OrderTerm(self.state.tag(), kid, order,
                         self.space.limit, self.space.offset,
                         self.space, routes)


class InjectCode(Inject):
    """
    Augments the term to make it capable of producing the given expression.
    """

    adapts(Code)

    def __call__(self):
        # Inject all the units that compose the expression.
        return self.state.inject(self.term, self.expression.units)


class InjectUnit(Inject):
    """
    Augments the term to make it produce the given unit.

    Constructor arguments:

    `unit` (:class:`htsql.tr.code.Unit`)
        A unit node to inject.

    `term` (:class:`htsql.tr.term.RoutingTerm`)
        A term node to inject into.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.

    Other attributes:

    `space` (:class:`htsql.tr.code.Space`)
        An alias to `unit.space`.
    """

    adapts(Unit)

    def __init__(self, unit, term, state):
        assert isinstance(unit, Unit)
        super(InjectUnit, self).__init__(unit, term, state)
        self.unit = unit
        # Extract the unit attributes.
        self.space = unit.space

    def __call__(self):
        # Normally, this should never be reachable.  We raise an error here
        # to prevent an infinite recursion via `InjectCode` in cases when
        # `Inject` is not implemented for some unit type.
        raise NotImplementedError("the inject adapter is not implemented"
                                  " for a %r node" % self.unit)


class InjectColumn(Inject):
    """
    Injects a column unit into a term.
    """

    adapts(ColumnUnit)

    def __call__(self):
        # We don't keep column units in the routing table (there are too
        # many of them).  Instead presence of a space node in the routing
        # table indicates that all columns of the prominent table of the
        # space are exported from the term.

        # To avoid an extra `inject()` call, check if the unit space
        # is already exported by the term.
        if self.space in self.term.routes:
            return self.term
        # Verify that the unit is singular on the term space.
        if not self.term.space.spans(self.space):
            raise AssembleError("expected a singular expression",
                                self.unit.mark)
        # Inject the unit space into the term.
        return self.state.inject(self.term, [self.unit.space])


class InjectScalar(Inject):
    """
    Injects a scalar unit into a term.
    """

    adapts(ScalarUnit)

    def __call__(self):
        # Injecting is already implemented for a batch of scalar units
        # that belong to the same space.  To avoid code duplication,
        # we delegate injecting to a batch consisting of just one unit.

        # Check if the unit is already exported by the term.
        if self.unit in self.term.routes:
            return self.term
        # Form a batch consisting of a single unit.
        batch = ScalarBatchExpression(self.unit.space, [self.unit],
                                      self.unit.binding)
        # Delegate the injecting to the batch.
        return self.state.inject(self.term, [batch])


class InjectAggregate(Inject):
    """
    Inject an aggregate unit into a term.
    """

    adapts(AggregateUnit)

    def __call__(self):
        # Injecting is already implemented for a batch of aggregate units
        # that share the same base and plural spaces.  To avoid code
        # duplication, we delegate injecting to a batch consisting of
        # just one unit.

        # Check if the unit is already exported by the term.
        if self.unit in self.term.routes:
            return self.term
        # Form a batch consisting of a single unit.
        batch = AggregateBatchExpression(self.unit.plural_space,
                                         self.unit.space, [self.unit],
                                         self.unit.binding)
        # Delegate the injecting to the batch.
        return self.state.inject(self.term, [batch])


class InjectCorrelated(Inject):
    """
    Injects a correlated unit into a term.
    """

    adapts(CorrelatedUnit)

    def __call__(self):
        # In the term tree, correlated subqueries are represented using
        # a correlated term node.  A correlated term is a binary node with
        # the left operand representing the main query and the right operand
        # representing the correlated subquery.  Conditions that attach
        # the correlated subquery to the main query are expressed as
        # a list of ties.

        # Check if the unit is already exported by the term.
        if self.unit in self.term.routes:
            return self.term
        # Verify that the unit is singular on the term space.
        if not self.term.space.spans(self.space):
            raise AssembleError("expected a singular expression",
                                self.unit.mark)

        # The general chain of operations is as follows:
        #   - assemble a term for the unit space;
        #   - inject the unit into the unit term;
        #   - attach the unit term to the main term.
        # However, when the unit space coincides with the term space,
        # it could be reduced to:
        #   - inject the unit directly into the main term.
        # We say that the unit is *native* to the term if the unit
        # space coincides with the term space (or dominates over it).

        # Note that currently the latter is always the case because
        # all correlated units are wrapped with a scalar unit sharing
        # the same unit space.

        # Check if the unit is native to the term.
        is_native = self.space.dominates(self.term.space)
        if is_native:
            # If so, we are going to inject the unit directly into the term.
            unit_term = self.term
        else:
            # Otherwise, assemble a separate term for the unit space.
            # Note: currently, not reachable.
            unit_term = self.assemble_shoot(self.space, self.term)

        # Assemble a term for the correlated subquery.
        plural_term = self.assemble_shoot(self.unit.plural_space,
                                          unit_term, [self.unit.code])
        # The ties connecting the correlated subquery to the main query.
        ties = self.tie_terms(unit_term, plural_term)
        # Make sure that the unit term could export tie conditions.
        unit_term = self.inject_ties(unit_term, ties)
        # Generate a correlation term.
        routes = unit_term.routes.copy()
        routes[self.unit] = plural_term.tag
        unit_term = CorrelationTerm(self.state.tag(), unit_term, plural_term,
                                    ties, unit_term.space, routes)
        # If we attached the unit directly to the main term, we are done.
        if is_native:
            return unit_term
        # Otherwise, we need to attach the unit term to the main term.
        extra_routes = { self.unit: plural_term.tag }
        return self.join_terms(self.term, unit_term, extra_routes)


class InjectBatch(Inject):
    """
    Injects a batch of expressions into a term.
    """

    adapts(BatchExpression)

    def __init__(self, expression, term, state):
        super(InjectBatch, self).__init__(expression, term, state)
        # Extract attributes of the batch.
        self.collection = expression.collection

    def __call__(self):
        # The easiest way to inject a group of expressions is to inject
        # them into the term one by one.  However, it will not necessarily
        # generate the most optimal term tree.  We could obtain a better
        # tree structure if we group all units of the same form and inject
        # them all together.
        # Here we group similar scalar and aggregate units into scalar
        # and aggregate batch nodes and then inject the batches.  We do not
        # need to do the same for column units since injecting a column
        # unit effectively injects the unit space making any column from
        # the space exportable.

        # We start with the given term, at the end, it will be capable of
        # exporting all expressions from the given collection.
        term = self.term

        # Gather all the units from the given collection of expressions.
        units = []
        for expression in self.collection:
            # Ignore spaces and other non-code expressions.
            if isinstance(expression, Code):
                for unit in expression.units:
                    # We are only interested in units that are not already
                    # exportable by the term.
                    if unit not in term.routes:
                        units.append(unit)

        # Find all scalar units and group them by the unit space.  We
        # maintain a separate list of scalar spaces to ensure we process
        # the batches in some deterministic order.
        scalar_spaces = []
        scalar_space_to_units = {}
        for unit in units:
            if isinstance(unit, ScalarUnit):
                space = unit.space
                if space not in scalar_space_to_units:
                    scalar_spaces.append(space)
                    scalar_space_to_units[space] = []
                scalar_space_to_units[space].append(unit)
        # Form and inject batches of matching scalar units.
        for space in scalar_spaces:
            batch_units = scalar_space_to_units[space]
            batch = ScalarBatchExpression(space, batch_units,
                                          self.term.binding)
            term = self.state.inject(term, [batch])

        # Find all aggregate units and group them by their plural and unit
        # spaces.  Maintain a list of pairs of spaces to ensure deterministic
        # order of processing the batches.
        aggregate_space_pairs = []
        aggregate_space_pair_to_units = {}
        for unit in units:
            if isinstance(unit, AggregateUnit):
                pair = (unit.plural_space, unit.space)
                if pair not in aggregate_space_pair_to_units:
                    aggregate_space_pairs.append(pair)
                    aggregate_space_pair_to_units[pair] = []
                aggregate_space_pair_to_units[pair].append(unit)
        # Form and inject batches of matching aggregate units.
        for pair in aggregate_space_pairs:
            plural_space, space = pair
            group_units = aggregate_space_pair_to_units[pair]
            group = AggregateBatchExpression(plural_space, space, group_units,
                                             self.term.binding)
            term = self.state.inject(term, [group])

        # Finally, just take and inject all the given expressions.  We don't
        # have to bother with filtering out duplicates or expressions that
        # are already injected.
        for expression in self.collection:
            term = self.state.inject(term, [expression])
        return term


class InjectScalarBatch(Inject):
    """
    Injects a batch of scalar units sharing the same space.
    """

    adapts(ScalarBatchExpression)

    def __init__(self, expression, term, state):
        super(InjectScalarBatch, self).__init__(expression, term, state)
        # Extract attributes of the batch.
        self.space = expression.space

    def __call__(self):
        # To inject a scalar unit into a term, we need to do the following:
        # - assemble a term for the unit space;
        # - inject the unit into the unit term;
        # - attach the unit term to the main term.
        # If we do this for each unit individually, we may end up with
        # a lot of identical unit terms in our term tree.  To optimize
        # the term tree in this scenario, we collect all scalar units
        # sharing the same space into a batch expression.  Then, when
        # injecting the batch, we use the same unit term for all units
        # in the batch.

        # Get the list of units that are not already exported by the term.
        units = [unit for unit in self.collection
                      if unit not in self.term.routes]
        # If none, there is nothing to be done.
        if not units:
            return self.term
        # Verify that the units are singular relative to the term.
        # To report an error, we could point to any unit node.
        if not self.term.space.spans(self.space):
            raise AssembleError("expected a singular expression",
                                units[0].mark)
        # Extract the unit expressions.
        codes = [unit.code for unit in units]

        # Handle the special case when the unit space is equal to the
        # term space or dominates it.  In this case, we could inject
        # the units directly to the main term and avoid creating
        # a separate unit term.
        if self.space.dominates(self.term.space):
            # Make sure the term could export all the units.
            term = self.state.inject(self.term, codes)
            # SQL does not allow evaluating expressions in a terminal
            # (table or scalar) terms.  If we got a terminal term,
            # cover it with a no-op wrapper.
            if term.is_nullary:
                term = WrapperTerm(self.state.tag(), term,
                                   term.space, term.routes)
            # Update the routing table to add all the units and
            # return the term.
            routes = term.routes.copy()
            for unit in units:
                routes[unit] = term.tag
            return term.clone(routes=routes)

        # The general case: assemble a term for the unit space.
        unit_term = self.assemble_shoot(self.space, self.term, codes)
        # And join it to the main term.
        extra_routes = dict((unit, unit_term.tag) for unit in units)
        return self.join_terms(self.term, unit_term, extra_routes)


class InjectAggregateBatch(Inject):
    """
    Injects a batch of aggregate units sharing the same plural and unit spaces.
    """

    adapts(AggregateBatchExpression)

    def __init__(self, expression, term, state):
        super(InjectAggregateBatch, self).__init__(expression, term, state)
        # Extract attributes of the batch.
        self.plural_space = expression.plural_space
        self.space = expression.space

    def __call__(self):
        # To inject an aggregate unit into a term, we do the following:
        # - assemble a term for the unit space;
        # - assemble a term for the plural space relative to the unit term;
        # - inject the unit expression into the plural term;
        # - project plural term into the unit space;
        # - attach the projected term to the unit term;
        # - attach the unit term to the main term.
        # When the unit space coincides with the main term space, we could
        # avoid assembling a separate unit term, and instead attach the
        # projected term directly to the main term.

        # In any case, if we perform this procedure for each unit
        # individually, we may end up with a lot of identical unit terms
        # in the final term tree.  So when there are more than one aggregate
        # unit with the same plural and unit spaces, it make sense to
        # collect all of them into a batch expression.  Then, when injecting
        # the batch, we could reuse the same unit and plural terms for all
        # aggregates in the batch.

        # Get the list of units that are not already exported by the term.
        units = [unit for unit in self.collection
                      if unit not in self.term.routes]
        # If none, there is nothing to do.
        if not units:
            return self.term
        # Verify that the units are singular relative to the term.
        # To report an error, we could point to any unit node available.
        if not self.term.space.spans(self.space):
            raise AssembleError("expected a singular expression",
                                units[0].mark)
        # Extract the aggregate expressions.
        codes = [unit.code for unit in units]

        # Check if the unit space coincides with or dominates the term
        # space.  In this case we could avoid assembling a separate unit
        # term and instead attach the projected term directly to the main
        # term.
        is_native = self.space.dominates(self.term.space)
        if is_native:
            unit_term = self.term
        else:
            # Assemble a separate term for the unit space.
            # Note: currently it is not reachable since we wrap every
            # aggregate with a scalar unit sharing the same space.
            unit_term = self.assemble_shoot(self.space, self.term)

        # Assemble a term for the plural space against the unit space,
        # and inject all the aggregate expressions into it.
        plural_term = self.assemble_shoot(self.plural_space,
                                          unit_term, codes)
        # Generate ties to attach the projected term to the unit term.
        ties = self.tie_terms(unit_term, plural_term)
        # Make sure the unit term could export the tie conditions.
        unit_term = self.inject_ties(unit_term, ties)

        # Now we are going to project the plural term onto the unit
        # space.  As the projection basis, we are using the ties.
        # There are two kinds of ties we could get from `tie_terms()`:
        # - a list of parallel ties;
        # - or a single series tie.
        #
        # If we get a list of parallel ties, the projection basis
        # comprises the primary keys of the tie spaces.  Otherwise,
        # the basis is the foreign key that joins the tie space to
        # its base.  These are also the columns connecting the
        # projected term to the unit term.

        # Determine the space of the projected term.
        # FIXME: When we get a list of parralel ties from `tie_terms()`,
        # we take the rightmost tie and assume that the space of the
        # projected term is the tie space masked by the plural space,
        # which is more or less correct.
        # However, when `tie_terms()` returns a series tie, we also claim
        # that the projected space is the masked tie space, which is not
        # true at all.  Indeed, in this case, the tie space is the baseline
        # of the term.  Since we project the plural term onto the foreign
        # key joining the baseline to its base, the actual projected space
        # is the base of the baseline, masked appropriately.
        # Unfortunately, we cannot specify the real projected space because
        # the term cannot export any values from this space.  Currently,
        # we maintain an assumption that the term is always able to
        # export its own space.  Perhaps we need to lift it?
        # FIXME: when the unit space is the scalar space, the projected
        # space should not be masked (this is one of the peculiarities of
        # the SQL semantics).
        projected_space = MaskedSpace(ties[-1].space, self.plural_space,
                                      self.expression.binding)
        # The routing table of the projected term.
        # FIXME: the projected term should be able to export the tie
        # conditions, so we add the tie spaces to the routing table.
        # However we should never attempt to export any columns than
        # those that form the tie condition -- it will generate invalid
        # SQL.  It is not clear how to fix this, perhaps the routing
        # table should contain entries for each of the columns, or
        # a special entry for just tie conditions?
        routes = {}
        for tie in ties:
            routes[tie.space] = plural_term.routes[tie.space]
        # The term space must always be in the routing table.  Here,
        # `projected_space.base` is `ties[-1].space`.
        routes[projected_space] = routes[projected_space.base]
        # Project the plural term onto the basis of the unit space.
        projected_term = ProjectionTerm(self.state.tag(), plural_term,
                                        ties, projected_space, routes)
        # Attach the projected term to the unit term, add extra entries
        # to the routing table for each of the unit in the collection.
        extra_routes = dict((unit, projected_term.tag) for unit in units)
        unit_term = self.join_terms(unit_term, projected_term, extra_routes)
        # For native units, we are done since we use the main term as
        # the unit term.  Note: currently this condition always holds.
        if is_native:
            return unit_term
        # Otherwise, attach the unit term to the main term.
        return self.join_terms(self.term, unit_term, extra_routes)


def assemble(expression, state=None, baseline=None, mask=None):
    """
    Assembles a new term node for the given expression.

    Returns a :class:`htsql.tr.term.Term` instance.

    `expression` (:class:`htsql.tr.code.Expression`)
        An expression node.

    `state` (:class:`AssemblingState` or ``None``)
        The assembling state to use.  If not set, a new assembling state
        is instantiated.

    `baseline` (:class:`htsql.tr.code.Space` or ``None``)
        The baseline space.  Specifies an axis that the assembled
        term must export.  If not set, the current baseline space of
        the state is used.

    `mask` (:class:`htsql.tr.code.Space` or ``None``)
        The mask space.  Specifies the mask space against which
        a new term is assembled.  When not set, the current mask space
        of the state is used.
    """
    # Instantiate a new assembling state if not given one.
    if state is None:
        state = AssemblingState()
    # If passed, assign new baseline and mask spaces.
    if baseline is not None:
        state.push_baseline(baseline)
    if mask is not None:
        state.push_mask(mask)
    # Realize and apply the `Assemble` adapter.
    assemble = Assemble(expression, state)
    term = assemble()
    # Restore old baseline and mask spaces.
    if baseline is not None:
        state.pop_baseline()
    if mask is not None:
        state.pop_mask()
    # Return the assembled term.
    return term


