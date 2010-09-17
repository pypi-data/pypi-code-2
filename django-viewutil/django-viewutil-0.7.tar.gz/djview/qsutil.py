"""
Parts of this implementation are taken from akaihola's snippet on
stackoverflow:

  http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view

"""


from itertools import islice
from operator import attrgetter


class SortedQuerySetChain(object):
    """
    a wrapper around multiple querysets that you would like to sort and
    paginate together (that is, get a slice rather than the complete sorted
    list).

    N.B.: getting a slice from this object always involves walking from the
    start of the list, so in effect one is always sorting from the beginning
    of the list up to the slice one wants -- without, however, having to keep
    unwanted results in memory.

    """

    def __init__(self, querysets, sort_keys, reverse=False, chunk_size=10):
        """
        - "querysets" should be a list of querysets; they should already be
          sorted in a manner consistent with the merge being performed.
        - "sort_keys" should be a dictionary mapping Model classes to either
          attribute names or sort key functions.
        - "reverse" is whether the sort should be reversed or not.
        - "chunk_size" is how many elements should be pulled from each queryset
          at a time.
        """
        self.querysets = querysets
        self.sort_keys = dict((k, (v  if callable(v) else attrgetter(v))) \
                              for k, v in sort_keys.iteritems())
        self.reverse = reverse
        self.chunk_size = chunk_size

    def _clone(self):
        return self.__class__(self.querysets, self.sort_keys, self.chunk_size)

    def count(self):
        return sum(qs.count() for qs in self.querysets)

    def _sort_key(self, obj):
        key = self.sort_keys.get(type(obj[0]), None)
        if key:
            return key(obj[0])
        return obj[0]

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return list(islice(self._all(),
                               idx.start,
                               idx.stop,
                               idx.step or 1))
        else:
            return islice(self._all(), idx, idx + 1).next()

    def _all(self):
        chunk_size = self.chunk_size

        def contains(list, qs_idx):
            """Checks if the list contains a qs_idx."""
            for x in list:
                if x[1] == qs_idx:
                    return True
            return False

        class QSPointer(object):

            def __init__(self, qs):
                self.qs = qs
                self.next = 0  # index of next unread item

        querysets = dict((idx, QSPointer(qs)) for
                         idx, qs in enumerate(self.querysets))
        next_results = []  # a list of tuples: (element from qs, qs idx)
        qs_to_remove = []
        while True:
            next_modified = False
            for idx in querysets:
                qs_pointer = querysets[idx]
                if not contains(next_results, idx):
                    end = qs_pointer.next + chunk_size
                    chunk = qs_pointer.qs[qs_pointer.next:end]
                    if not chunk:
                        qs_to_remove.append(idx)
                    else:
                        querysets[idx].next = end
                        next_results.extend([(item, idx) for item in chunk])
                        next_modified = True

            while qs_to_remove:
                del querysets[qs_to_remove.pop()]

            if next_modified:
                next_results.sort(key=self._sort_key, reverse=not self.reverse)

            if next_results:
                yield next_results.pop()[0]
            else:
                break


__all__ = ['SortedQuerySetChain']
