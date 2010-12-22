"""
LINQ-style query implementation for Python.

"We don't need expression trees 'round these parts."
"""

__author__ = "Tony Young <rofflwaffls@gmail.com>"
__version__ = "0.1"

import operator
from itertools import chain, ifilter, imap, izip, takewhile

def _as_is(x): return x
def _as_is_packed(*x): return x
def _as_true(*x): return True

class Query(object):
    def __new__(cls, iterable):
        """
        Create a new Query object, only if the provided iterable is not already
        wrapped with Query.

        @param iterable: Iterable to wrap.
        @return: L{Query}-wrapped iterable.
        """
        if isinstance(iterable, cls):
            return iterable

        query = super(Query, cls).__new__(cls)
        query.iterable = iterable
        return query

    def where(self, predicate):
        """
        Filter a container using a predicate.

        @param predicate: Function specifying a condition for a value.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(ifilter(predicate, self))

    def select(self, selector):
        """
        Select an element from a container using a selector.

        @param selector: Function to use when selecting results.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(imap(selector, self))

    def _select_many(self, selector):
        """
        Internal L{select_many} implementation.
        """
        for elem in self:
            for subelem in imap(selector, self):
                yield subelem

    def select_many(self, selector):
        """
        Select nested elements from a container.

        @param selector: Function to use when selecting results.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._select_many(selector))

    def order_by(self, key_selector, reverse=False):
        """
        Order an iterable by key selector.

        @param key_selector: Function to use to select the key.
        @param reverse: Reverse the list.
        @return: L{Query}-wrapped iterable.
        """
        return Query(sorted(self, key=key_selector, reverse=reverse))

    def aggregate(self, aggregator):
        """
        Build a return value by iterating over an iterable.

        @param aggregator: The function to use to combine the iterable.
        @return: Reduced iterable.
        """
        return reduce(aggregator, self)

    def _union(self, other, comparer=operator.eq):
        """
        Internal L{union} implementation.
        """
        present = []

        for elem in chain(self, other):
            skip = False
            for item in present:
                if comparer(elem, item):
                    skip = True
                    break
            if skip: continue
            present.append(elem)
            yield elem

    def union(self, other):
        """
        Get the distinct elements of two iterables.

        @param other: Iterable to perform a union with.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._union(other))

    def concat(self, other):
        """
        Join two iterables together, one after the other.

        @param other: Iterable to concatenate.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(chain(self, other))

    def zip(self, other, zipper=_as_is_packed):
        """
        Join two iterables together by combining one element with another.

        @param other: Iterable to zip with.
        @param zipper: Function to use when combining elements,
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(imap(zipper, izip(self, other)))

    def any(self, predicate=_as_is):
        """
        Check if any element in the iterable meets a condition.

        @param predicate: Function specifying a condition for a value.
        @return: C{True} or C{False}.
        """
        for elem in self:
            if predicate(elem):
                return True
        return False

    def all(self, predicate=_as_is):
        """
        Check if all elements in the iterable meets a condition.

        @param predicate: Function specifying a condition for a value.
        @return: C{True} or C{False}.
        """
        for elem in self:
            if not predicate(elem):
                return False
        return True

    def _reverse(self):
        """
        Internal L{reverse} implementation.
        """
        items = list(self)
        for i in xrange(len(items) - 1, -1, -1):
            yield items[i]

    def reverse(self):
        """
        Reverse an iterable.

        @return: The reversed iterable.
        @note: Supports deferred execution only after being called.
        """
        return Query(self._reverse())

    def sequence_equal(self, other, comparer=operator.eq):
        """
        Check if two iterables are equal to each other.

        @param other: Iterable to check equality with.
        @param comparer: Function to use for comparing equality.
        @return: C{True} or C{False}.
        """
        self_iter = iter(self)
        other_iter = iter(other)

        while True:
            try:
                self_value = self_iter.next()
            except StopIteration:
                try:
                    other_value = other_iter.next()
                except StopIteration:
                    return True
                else:
                    return False
            else:
                try:
                    other_value = other_iter.next()
                except StopIteration:
                    return False
                else:
                    if not comparer(self_value, other_value): return False

    def take_while(self, predicate=_as_is):
        """
        Take elements from the iterable while a condition is met.

        @param predicate: Function specifying a condition to meet.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(takewhile(predicate, self))

    def _skip_while(self, predicate):
        """
        Internal L{skip_while} implementation.
        """
        skip = True
        for elem in self:
            if not predicate(elem):
                skip = False
            if not skip: yield elem

    def skip_while(self, predicate=_as_is):
        """
        Skip elements in the iterable while a condition is met.

        @param predicate: Function specifying a condition to meet.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._skip_while(predicate))

    def _take(self, num):
        """
        Internal L{take} implementation.
        """
        count = 0
        for elem in self:
            count += 1
            if count > num: break
            yield elem

    def take(self, num):
        """
        Take the first few elements of an iterable.

        @param num: Number of elements to take.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._take(num))

    def _skip(self, num):
        """
        Internal L{skip} implementation.
        """
        count = 0
        for elem in self:
            count += 1
            if count < num: continue
            yield elem

    def skip(self, num):
        """
        Skip the first few elements of an iterable.

        @param num: Number of elements to skip.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._skip(num))

    def contains(self, item, comparer=operator.eq):
        """
        Check if an item exists in an iterable.

        @param item: Item to check for.
        @param comparer: Function to use for comparing equality.
        @return: C{True} or C{False}.
        """
        for elem in self:
            if comparer(elem, item):
                return True
        return False

    def count(self):
        """
        Return the number of elements in an iterable.

        @return: The number of elements in the iterable.
        """
        return len(self)

    def not_empty_or(self, value=None):
        """
        Return the iterable if it contains items, otherwise return C{value}.

        @param value: Value to return if the iterable is empty.
        @return: The iterable or C{value}.
        """
        for elem in self:
            return self
        return value

    def _join(
        self,
        inner,
        outer_key_selector,
        inner_key_selector,
        result_selector,
        comparer
    ):
        """
        Internal L{join} implementation.
        """
        inners = {}

        for elem in inner:
            inners[inner_key_selector(elem)] = elem

        for elem in self:
            outer_key = outer_key_selector(elem)
            for inner_key in inners:
                if comparer(inner_key, outer_key):
                    yield result_selector(elem, inners[inner_key])

    def join(
        self,
        inner,
        outer_key_selector,
        inner_key_selector,
        result_selector=_as_is_packed,
        comparer=operator.eq
    ):
        """
        Perform an inner join between two iterables.

        @param inner: The inner iterable to join with.
        @param outer_key_selector: Function used to select the key from this
                                   iterable.
        @param inner_key_selector: Function used to select the key from the
                                   inner iterable.
        @param result_selector: Function used to select the result.
        @param comparer: Function used to compare equality of keys.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._join(
            inner,
            outer_key_selector,
            inner_key_selector,
            result_selector,
            comparer
        ))

    def _group_join(
        self,
        inner,
        outer_key_selector,
        inner_key_selector,
        result_selector,
        comparer
    ):
        """
        Internal L{group_join} implementation.
        """
        raise NotImplementedError("wtf is a group join")

    def group_join(
        self,
        inner,
        outer_key_selector,
        inner_key_selector,
        result_selector=_as_is_packed,
        comparer=operator.eq
    ):
        """
        Perform a group join between two iterables.

        @param inner: The inner iterable to join with.
        @param outer_key_selector: Function used to select the key from this
                                   iterable.
        @param inner_key_selector: Function used to select the key from the
                                   inner iterable.
        @param result_selector: Function used to select the result.
        @param comparer: Function used to compare equality of keys.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._group_join(
            inner,
            outer_key_selector,
            inner_key_selector,
            result_selector,
            comparer
        ))

    def _difference(self, other, comparer):
        """
        Internal L{difference} implementation.
        """
        for elem in self:
            skipping = False
            for item in other:
                if comparer(elem, item):
                    skipping = True
                    break
            if skipping: continue
            yield elem

    def difference(self, other, comparer=operator.eq):
        """
        Get the set difference of two iterables using the specified equality
        comparer.

        @param other: The other iterable.
        @param comparer: Function used to compare the equality of two elements.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._difference(other, comparer))

    def _group_by(self, key_selector, element_selector, comparer):
        """
        Internal L{group_by} implementation.
        """
        groups = {}
        for elem in self:
            appended = False
            key = key_selector(elem)
            for group_key in groups:
                if comparer(key, group_key):
                    groups[key].append(element_selector(elem))
                    appended = True
                    break
            if not appended:
                groups[key] = [ element_selector(elem) ]

        for group in groups.iteritems():
            yield group

    def group_by(
        self,
        key_selector,
        element_selector=_as_is,
        comparer=operator.eq
    ):
        """
        Group an iterable by key.

        @param key_selector: Function used to select the key.
        @param element_selector: Function used to select the element.
        @param comparer: Function used to compare the equality of two keys.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._group_by(key_selector, element_selector, comparer))

    def single(self, predicate=_as_is):
        """
        Return the only element in an iterable that matches the predicate,
        otherwise raise an exception if not.

        @param predicate: Function specifying a condition for a value.
        @return: The item.
        """
        for elem in self:
            if predicate(elem):
                try:
                    result
                except NameError:
                    result = elem
                else:
                    raise ValueError("more than one element matches predicate")
        try:
            return result
        except NameError:
            raise ValueError("no elements match predicate")

    def single_or(self, predicate=_as_is, value=None):
        """
        Return the only element in an iterable that matches the predicate,
        otherwise return C{value}.

        @param predicate: Function specifying a condition for a value.
        @param value: Value to return if nothing matches the predicate.
        @return: The item or C{value}.
        """
        for elem in self:
            if predicate(elem):
                try:
                    result
                except NameError:
                    result = elem
                else:
                    return None
        try:
            return result
        except NameError:
            return value

    def max(self, selector=_as_is):
        """
        Get the maximum of all elements in the iterable.

        @param selector: Function to use when selecting a value.
        """
        return max(self, key=selector)

    def min(self, selector=_as_is):
        """
        Get the minimum of all elements in the iterable.

        @param selector: Function to use when selecting a value.
        """
        return min(self, key=selector)

    def element_at(self, index):
        """
        Get the element at a specific index of the iterable.

        @param index: The index.
        @return: The value at the index.
        """
        iterator = iter(self)
        try:
            for i in xrange(index):
                iterator.next()
            return iterator.next()
        except StopIteration:
            raise IndexError("index out of range")

    def element_at_or(self, index, value=None):
        """
        Get the element at a specific index of the iterable or return C{value}
        if the index is not in the iterable.

        @param index: The index.
        @param value: Value to return if specified index does not exist.
        @return: The value at the index or C{value}.
        """
        iterator = iter(self)
        try:
            for i in xrange(index):
                iterator.next()
            return iterator.next()
        except StopIteration:
            return value

    def _distinct(self, comparer):
        """
        Internal L{distinct} implementation.
        """
        already = []
        for elem in self:
            present = False
            for item in already:
                if comparer(elem, item):
                    present = True
                    break
            if not present:
                already.append(elem)
                yield elem

    def distinct(self, comparer=operator.eq):
        """
        Get only the distinct elements of the iterable.

        @param comparer: Function to use when comparing two elements.
        @return: L{Query}-wrapped iterable.
        @note: Supports deferred execution.
        """
        return Query(self._distinct(comparer))

    def first(self, predicate=_as_is):
        """
        Get the first element that matches the predicate.

        @param predicate: Function specifying a condition for a value.
        @return: The item.
        """
        for elem in self:
            if predicate(elem):
                return elem
        raise ValueError("no elements match the predicate")

    def first_or(self, predicate=_as_is, value=None):
        """
        Get the first element that matches the predicate or return C{value} if
        none are found.

        @param predicate: Function specifying a condition for a value.
        @param value: Value to return if nothing matches the predicate.
        @return: The item or C{value}.
        """
        for elem in self:
            if predicate(elem):
                return elem
        return value

    def __iter__(self):
        """
        Iterator wrapper.

        @return: Iterator for the iterable.
        """
        return iter(self.iterable)
